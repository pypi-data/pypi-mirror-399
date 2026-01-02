from typing import Any, Literal, Mapping, Optional, Union

from ...flow_metrics import EndpointMetric
from ...schemas.investigation import (
    BaseInvestigationData,
    HttpInvestigation,
    HttpInvestigationContext,
    InvestigationTriggerType,
)
from ..limited_logger import limited_logger
from .investigation_thresholds import InvestigationEvaluationContext
from .processor import BaseInvestigationProcessor
from .triggers import HttpTriggerChecker


def safe_get_header(
    headers: Optional[Mapping[str, str]], header_name: str
) -> Optional[str]:
    try:
        if headers is None:
            return None

        return headers.get(header_name)
    except Exception as e:
        limited_logger.log(
            "Failed to get header", data={"error": str(e), "header_name": header_name}
        )
    return None


class HttpInvestigationProcessor(
    BaseInvestigationProcessor[HttpInvestigationContext, EndpointMetric]
):
    def __init__(self) -> None:
        super().__init__("http")

    def get_trigger_type(
        self,
        metric: EndpointMetric,
        ctx: InvestigationEvaluationContext,
        **framework_data: Any
    ) -> Union[InvestigationTriggerType, Literal[False]]:
        return HttpTriggerChecker().check(metric, ctx)

    def _finalize(
        self,
        base_data: BaseInvestigationData,
        context: HttpInvestigationContext,
        metric: EndpointMetric,
    ) -> HttpInvestigation:
        return HttpInvestigation(
            exceptions=base_data.exceptions,
            context=context,
            flow_id=base_data.flow_id,
            trigger_type=base_data.trigger_type,
            duration=base_data.duration,
            duration_threshold=base_data.duration_threshold,
        )
