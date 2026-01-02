from abc import ABC, abstractmethod
from typing import (
    Any,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
)

from ...config import config
from ...flow_metrics import FlowMetric
from ...investigation_manager import send_investigation_to_worker
from ...native import RawInvestigation
from ...schemas.investigation import (
    BaseInvestigationContext,
    BaseInvestigationData,
    EndpointDurationThresholdAndCount,
    ErrorBreakdown,
    Investigation,
    InvestigationExceptionInfo,
    InvestigationTriggerType,
)
from ..limited_logger import limited_logger
from .investigation_thresholds import (
    InvestigationEvaluationContext,
)
from .investigation_utils import (
    get_error_records_from_investigation,
    get_investigation_dedup,
    get_investigation_deduping_key_for_errors,
    get_machine_metrics,
    get_system_info,
    minimize_exception_info_in_place,
)
from .rate_limiter import RateLimiter

C = TypeVar("C", bound=BaseInvestigationContext)
M = TypeVar("M", bound=FlowMetric)


class BaseInvestigationProcessor(ABC, Generic[C, M]):
    def __init__(self, framework_type: str):
        self.framework_type = framework_type
        self.rate_limiter = RateLimiter()

    def _process_before_enrichment(
        self, raw_investigation: RawInvestigation, metric: M, **framework_data: Any
    ) -> Optional[BaseInvestigationData]:
        if not self._validate(raw_investigation, metric):
            return None

        flow_id = metric.flow_id
        if flow_id is None:
            return None  # This should never happen after validation, but helps type checker

        ctx = InvestigationEvaluationContext.create(flow_id, self.framework_type)
        trigger_type = self.get_trigger_type(metric, ctx, **framework_data)
        if not trigger_type:
            return None

        if not self.rate_limiter.can_investigate(trigger_type, flow_id, ctx.threshold):
            return None

        if trigger_type == "Error":
            dedup_key = ""
            try:
                dedup_key = self._apply_error_breakdown(raw_investigation, metric)
            except Exception:
                limited_logger.log("Error extracting error breakdown", exc_info=True)
            if not self._check_dedup(metric, flow_id, dedup_key):
                return None

        self.rate_limiter.record_investigation(trigger_type, flow_id)
        base_data = self._create_base_data(
            raw_investigation, metric, flow_id, trigger_type, ctx.threshold
        )
        return base_data

    def _serialize_and_store(
        self,
        base_data: BaseInvestigationData,
        context: C,
        metric: M,
    ) -> Optional[Investigation[C]]:
        investigation = self._finalize(base_data, context, metric)
        self._send(investigation)

        return investigation

    def process(
        self, raw_investigation: RawInvestigation, metric: M, **framework_data: Any
    ) -> Optional[Investigation[C]]:
        try:
            base_data = self._process_before_enrichment(
                raw_investigation, metric, **framework_data
            )
            if base_data is None:
                return None

            investigation_context = self.build_context(
                base_data, metric, **framework_data
            )

            return self._serialize_and_store(base_data, investigation_context, metric)
        except Exception:
            limited_logger.log("Error processing investigation", exc_info=True)
            return None

    def _validate(self, raw_investigation: RawInvestigation, metric: M) -> bool:
        if metric.flow_id is None:
            limited_logger.log("No flow id in metric")
            return False

        if raw_investigation.error_accoured == 1:
            limited_logger.log("Error occurred in investigation")
            return False

        return True

    @abstractmethod
    def get_trigger_type(
        self, metric: M, ctx: InvestigationEvaluationContext, **framework_data: Any
    ) -> Union[InvestigationTriggerType, Literal[False]]: ...

    def _apply_error_breakdown(
        self, raw_investigation: RawInvestigation, metric: M
    ) -> str:

        metric_status = metric.get_status()
        if metric_status is None:
            metric_status = ""
            limited_logger.log("Metric status is None")

        error_records = get_error_records_from_investigation(raw_investigation)
        dedup_key = get_investigation_deduping_key_for_errors(
            error_records, metric_status
        )

        error_breakdown = ErrorBreakdown(
            key=dedup_key, errors=error_records, failure_type=metric_status
        )
        metric.set_error_breakdown(error_breakdown)
        return dedup_key

    def _check_dedup(self, metric: M, flow_id: str, dedup_key: str) -> bool:
        investigation_dedup = get_investigation_dedup()

        if investigation_dedup.get(flow_id) is None:
            investigation_dedup[flow_id] = dict()

        if investigation_dedup[flow_id].get(dedup_key) is None:
            investigation_dedup[flow_id][dedup_key] = 0

        if investigation_dedup[flow_id][dedup_key] >= config.max_same_investigation:
            limited_logger.log("Max same investigation reached")
            return False

        investigation_dedup[flow_id][dedup_key] += 1
        return True

    def _create_base_data(
        self,
        raw_investigation: RawInvestigation,
        metric: M,
        flow_id: str,
        trigger_type: InvestigationTriggerType,
        threshold: Optional[EndpointDurationThresholdAndCount] = None,
    ) -> BaseInvestigationData:
        duration_threshold: Optional[int] = None
        if threshold is not None:
            duration_threshold = threshold.duration

        return BaseInvestigationData(
            exceptions=[
                minimize_exception_info_in_place(
                    InvestigationExceptionInfo(raw_exception)
                )
                for raw_exception in raw_investigation.exceptions.values()
            ],
            timestamp=raw_investigation.start_time,
            machine_metrics=get_machine_metrics(),
            system_info=get_system_info(),
            user_context=raw_investigation.user_context,
            flow_id=flow_id,
            duration=metric.duration,
            duration_threshold=duration_threshold,
            trigger_type=trigger_type,
        )

    def build_context(
        self, base_data: BaseInvestigationData, metric: M, **framework_data: Any
    ) -> C:
        raise NotImplementedError(
            "Subclass must implement either build_context() or build_context_async()"
        )

    async def build_context_async(
        self, base_data: BaseInvestigationData, metric: M, **framework_data: Any
    ) -> C:
        raise NotImplementedError(
            "Subclass must implement either build_context() or build_context_async()"
        )

    @abstractmethod
    def _finalize(
        self,
        base_data: BaseInvestigationData,
        context: C,
        metric: M,
    ) -> Investigation[C]: ...

    def _send(self, investigation: Investigation[C]) -> None:
        send_investigation_to_worker(investigation)

    async def process_async(
        self, raw_investigation: RawInvestigation, metric: M, **framework_data: Any
    ) -> Optional[Investigation[C]]:
        try:
            base_data = self._process_before_enrichment(
                raw_investigation, metric, **framework_data
            )
            if base_data is None:
                return None

            investigation_context = await self.build_context_async(
                base_data, metric, **framework_data
            )

            return self._serialize_and_store(base_data, investigation_context, metric)
        except Exception:
            limited_logger.log("Error processing investigation", exc_info=True)
            return None
