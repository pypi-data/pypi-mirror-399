from typing import Any, Literal, Union

from ...flow_metrics import ArqMetric
from ...schemas.investigation import (
    ArqInvestigation,
    ArqInvestigationContext,
    BaseInvestigationData,
    InvestigationTriggerType,
)
from .investigation_thresholds import InvestigationEvaluationContext
from .investigation_utils import minimize_object_with_defaults
from .processor import BaseInvestigationProcessor
from .triggers import ArqTriggerChecker


class ArqInvestigationProcessor(
    BaseInvestigationProcessor[ArqInvestigationContext, ArqMetric]
):

    def __init__(self) -> None:
        super().__init__("arq")

    def get_trigger_type(
        self,
        metric: ArqMetric,
        ctx: InvestigationEvaluationContext,
        **framework_data: Any
    ) -> Union[InvestigationTriggerType, Literal[False]]:
        return ArqTriggerChecker().check(metric, ctx)

    def build_context(
        self, base_data: BaseInvestigationData, metric: ArqMetric, **framework_data: Any
    ) -> ArqInvestigationContext:
        arq_function_name = framework_data.get("arq_function_name", "")
        arq_function_args = framework_data.get("arq_function_args")
        arq_function_kwargs = framework_data.get("arq_function_kwargs")
        job_id = framework_data.get("job_id")
        job_try = framework_data.get("job_try")

        return ArqInvestigationContext(
            timestamp=base_data.timestamp,
            machine_metrics=base_data.machine_metrics,
            system_info=base_data.system_info,
            arq_function_name=arq_function_name,
            arq_function_args=minimize_object_with_defaults(arq_function_args),
            arq_function_kwargs=minimize_object_with_defaults(arq_function_kwargs),
            job_id=job_id,
            job_try=job_try,
            error=metric.error,
            user_context=base_data.user_context,
        )

    def _finalize(
        self,
        base_data: BaseInvestigationData,
        context: ArqInvestigationContext,
        metric: ArqMetric,
    ) -> ArqInvestigation:
        return ArqInvestigation(
            exceptions=base_data.exceptions,
            context=context,
            flow_id=base_data.flow_id,
            trigger_type=base_data.trigger_type,
            duration=base_data.duration,
            duration_threshold=base_data.duration_threshold,
        )
