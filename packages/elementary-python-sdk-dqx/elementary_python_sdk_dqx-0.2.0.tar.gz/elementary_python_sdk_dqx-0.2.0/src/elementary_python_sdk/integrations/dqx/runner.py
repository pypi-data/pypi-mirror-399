from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable

import pytz
from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.tests.runners.base import (
    CommonTestFields,
    TestRunner,
    TestRunnerParams,
)
from elementary_python_sdk.core.tests.runners.executor import execute_test_decorator
from elementary_python_sdk.core.types.test import (
    Test,
    TestExecution,
    TestExecutionStatus,
    TestSeverity,
    TestType,
)
from pyspark.sql import DataFrame
from pyspark.sql.column import Column
from pyspark.sql.functions import count, explode, lit
from pyspark.sql.functions import max as spark_max

logger = get_logger()

# Order is important because when we aggregate errors, we want to prioritize failures over warnings
DQX_ERROR_FIELD_TO_STATUS = OrderedDict(
    [
        ("_errors", TestExecutionStatus.FAIL),
        ("_warnings", TestExecutionStatus.WARN),
    ]
)


class DQXTestParams(TestRunnerParams):
    """Parameters for DQX test runner."""

    dqx_rules: list


class DQXTestRunner(TestRunner[DQXTestParams, DataFrame]):
    """DQX test runner extending the most base class.

    Unlike SingleResultTestRunner, this produces multiple test results
    from a single DataFrame validation.
    """

    def validate_test_argument(
        self, test_argument: Any, params: DQXTestParams
    ) -> DataFrame:
        """Validate that the result is a DataFrame with DQX validation columns."""
        if not isinstance(test_argument, DataFrame):
            raise TypeError(
                f"DQX test must return DataFrame, got {type(test_argument).__name__}"
            )

        # Check that the DataFrame has the expected DQX error columns
        df_columns = set(test_argument.columns)
        expected_columns = {"_errors", "_warnings"}

        if not expected_columns.issubset(df_columns):
            missing = expected_columns - df_columns
            raise ValueError(
                f"DataFrame missing DQX validation columns: {missing}. "
                f"Make sure to run DQEngine.apply_checks() before returning the DataFrame."
            )

        return test_argument

    def resolve_tests(
        self,
        params: DQXTestParams,
        common: CommonTestFields,
        asset_id: str | None,
    ) -> list[Test]:
        tests = []

        for dqx_rule in params.dqx_rules:
            config = dqx_rule.to_dict()["check"]
            column_name = self._parse_column_name(dqx_rule.column)

            test_id = self._generate_test_id(
                test_name=dqx_rule.name,
                asset_id=asset_id,
                column_name=column_name,
            )
            tags = (dqx_rule.user_metadata or {}).get("elementary_tags", [])
            tags.extend(common.tags or [])
            owners = (dqx_rule.user_metadata or {}).get("elementary_owners", [])
            owners.extend(common.owners or [])

            test = Test(
                id=test_id,
                name=dqx_rule.name,
                test_type=TestType.DQX,
                asset_id=asset_id,
                column_name=column_name,
                severity=(
                    TestSeverity.ERROR
                    if dqx_rule.criticality == "error"
                    else TestSeverity.WARNING
                ),
                config=config,
                metadata={**(common.metadata or {}), **(dqx_rule.user_metadata or {})},
            )
            tests.append(test)

        return tests

    def _aggregate_errors(self, dqx_result: DataFrame) -> DataFrame:
        aggregated_errors_of_specific_status: list[DataFrame] = []
        for error_field, status in DQX_ERROR_FIELD_TO_STATUS.items():
            aggregated_errors = (
                dqx_result.withColumn("dqx_error", explode(error_field))
                .groupBy("dqx_error.name")
                .agg(
                    count("dqx_error.name").alias("failure_count"),
                    spark_max("dqx_error.message").alias("message"),
                )
                .withColumn("status", lit(status.value))
            )
            aggregated_errors_of_specific_status.append(aggregated_errors)
        aggregated_errors_all_statuses = aggregated_errors_of_specific_status[0]
        for aggregated_errors in aggregated_errors_of_specific_status[1:]:
            # This will join only the rows of tests that are not already in the aggregated_errors_all_statuses
            aggregated_errors_all_statuses = aggregated_errors_all_statuses.unionByName(
                aggregated_errors.join(
                    aggregated_errors_all_statuses.select("name"),
                    on="name",
                    how="left_anti",
                )
            )

        return aggregated_errors_all_statuses

    def resolve_test_results(
        self,
        tests: list[Test],
        params: DQXTestParams,
        test_argument: DataFrame,
        start_time: datetime,
        duration_seconds: float,
        code: str | None,
        common: CommonTestFields,
    ) -> list[TestExecution]:
        executions = []

        test_by_name = {test.name: test for test in tests}

        sql_code_per_test = {
            rule.name: self._get_sql_code(rule) for rule in params.dqx_rules
        }

        aggregated_errors = self._aggregate_errors(test_argument)

        for test_name, failure_count, message, status in aggregated_errors.collect():
            if test_name not in test_by_name:
                logger.warning(
                    f"Found DQX result for unknown test: {test_name}, skipping"
                )
                continue

            test = test_by_name[test_name]
            execution = TestExecution(
                test_id=test.id,
                test_sub_unique_id=test.id,
                sub_type=TestType.DQX.value,
                failure_count=failure_count,
                status=TestExecutionStatus(status),
                code=sql_code_per_test.get(test_name),
                start_time=start_time,
                duration_seconds=(datetime.now(pytz.utc) - start_time).total_seconds(),
                description=message or f"Test {status.value}",
                column_name=test.column_name,
            )
            executions.append(execution)

        # Create passing executions for tests that didn't appear in errors/warnings
        failed_tests = {exec.test_id for exec in executions}
        for test in tests:
            if test.id not in failed_tests:
                execution = TestExecution(
                    test_id=test.id,
                    test_sub_unique_id=test.id,
                    sub_type=TestType.DQX.value,
                    failure_count=0,
                    status=TestExecutionStatus.PASS,
                    code=sql_code_per_test.get(test.name),
                    start_time=start_time,
                    duration_seconds=(
                        datetime.now(pytz.utc) - start_time
                    ).total_seconds(),
                    description="Test succeeded",
                    column_name=test.column_name,
                )
                executions.append(execution)

        return executions

    def _generate_test_id(
        self,
        test_name: str,
        asset_id: str | None,
        column_name: str | None,
    ) -> str:
        test_id = "test.dqx"
        if asset_id:
            test_id += f".[{asset_id}]"
        if column_name:
            test_id += f".{column_name}"
        test_id += f".{test_name}"
        return test_id

    @staticmethod
    def _parse_column_name(column: str | Column | None) -> str | None:
        if isinstance(column, str):
            return column
        elif isinstance(column, Column):
            # Spark Connect (Python client -> remote Spark)
            if hasattr(column, "_expr") and isinstance(column._expr, str):
                return column._expr

            # Classic PySpark (JVM-backed)
            if hasattr(column, "_jc") and column._jc is not None:
                return str(column._jc)

            return None
        else:
            return None

    @staticmethod
    def _get_sql_code(dqx_rule) -> str | None:
        if hasattr(dqx_rule, "check"):
            check = dqx_rule.check
            if isinstance(check, tuple):
                check = check[0]
            return str(check._expr) if hasattr(check, "_expr") else None
        return None


def elementary_dqx_test(
    dqx_rules: list,
    name: str,
    description: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
    owners: list[str] | None = None,
    lazy: bool = True,
) -> Callable[[Callable[..., DataFrame]], Callable[..., DataFrame | None]]:
    """Decorator to record DQX rule results as Elementary test executions.

    Decorate a function that returns a Spark DataFrame produced by
    `DQEngine.apply_checks(...)` (it must include DQX columns like `_errors` and
    `_warnings`). When called inside `elementary_test_context(...)`, each DQX rule
    is registered as a test and its result is recorded as a test execution.

    Args:
        dqx_rules: DQX rule objects to apply.
        name: Logical name for this validation group.
        description: Optional description shown in Elementary.
        metadata: Optional metadata dict.
        tags: Optional list of tags.
        owners: Optional list of owners.
        lazy: If True, Spark actions will be executed lazily only when the results are collected/sent.

    Returns:
        A decorator that records DQX executions when invoked in a context
        Example:
            ```python
            from elementary_python_sdk.integrations.dqx import elementary_dqx_test
            from elementary_python_sdk.core.tests import elementary_test_context
            from pyspark.sql import DataFrame

            @elementary_dqx_test(dqx_rules=my_dqx_rules)
            def my_dqx_test(df: DataFrame) -> DataFrame:
                return dqx_engine.apply_checks(df, my_dqx_rules)

            with elementary_test_context(asset=my_asset) as ctx:
                my_dqx_test(df)
    """

    def decorator(func: Callable[..., DataFrame]) -> Callable[..., DataFrame | None]:
        test_runner = DQXTestRunner()
        params = DQXTestParams(dqx_rules=dqx_rules)
        common = CommonTestFields(
            name=name,
            description=description,
            metadata=metadata,
            tags=tags,
            owners=owners,
            severity=TestSeverity.ERROR,  # Default severity, will be overridden by each rule criticality
        )

        def execute_dqx_test(decorated_function_execution) -> None:
            from elementary_python_sdk.core.tests.runners.executor import (
                execute_test,
            )

            execute_test(
                test_runner=test_runner,
                params=params,
                common=common,
                argument=decorated_function_execution.function_result,
                start_time=decorated_function_execution.start_time,
                code=decorated_function_execution.function_source_code,
                lazy=lazy,
            )

        return execute_test_decorator(execute_dqx_test, func, name)

    return decorator
