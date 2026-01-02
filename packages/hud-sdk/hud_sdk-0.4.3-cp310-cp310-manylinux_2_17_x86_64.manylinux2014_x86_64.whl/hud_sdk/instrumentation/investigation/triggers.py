from abc import ABC, abstractmethod
from typing import Generic, Literal, TypeVar, Union

from ...flow_metrics import ArqMetric, EndpointMetric, FlowMetric
from ...schemas.investigation import InvestigationTriggerType
from .investigation_thresholds import InvestigationEvaluationContext

M = TypeVar("M", bound=FlowMetric)


class TriggerChecker(ABC, Generic[M]):
    @abstractmethod
    def check(
        self, metric: M, ctx: InvestigationEvaluationContext
    ) -> Union[InvestigationTriggerType, Literal[False]]: ...


class HttpTriggerChecker(TriggerChecker[EndpointMetric]):
    def check(
        self, metric: EndpointMetric, ctx: InvestigationEvaluationContext
    ) -> Union[InvestigationTriggerType, Literal[False]]:
        if metric.status_code is not None and metric.status_code >= 500:
            return "Error"
        if ctx.exceeds_duration_threshold(metric.duration):
            return "Duration"

        return False


class ArqTriggerChecker(TriggerChecker[ArqMetric]):
    def check(
        self, metric: ArqMetric, ctx: InvestigationEvaluationContext
    ) -> Union[InvestigationTriggerType, Literal[False]]:
        if metric.error is not None:
            return "Error"
        if ctx.exceeds_duration_threshold(metric.duration):
            return "Duration"

        return False
