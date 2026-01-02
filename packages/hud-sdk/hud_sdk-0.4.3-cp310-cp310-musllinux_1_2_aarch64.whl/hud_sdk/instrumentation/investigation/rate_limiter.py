from typing import Optional

from ...config import config
from ...schemas.investigation import (
    EndpointDurationThresholdAndCount,
    InvestigationTriggerType,
)
from ..limited_logger import limited_logger
from .investigation_thresholds import (
    get_investigation_duration_count,
    get_total_investigations_duration_based,
    get_total_investigations_error_based,
    increase_investigation_duration_count,
    increase_total_investigations_duration_based,
    increase_total_investigations_error_based,
)
from .investigation_utils import (
    get_total_investigations,
    increase_total_investigations,
)


class RateLimiter:
    def can_investigate(
        self,
        trigger_type: InvestigationTriggerType,
        flow_id: str,
        threshold: Optional[EndpointDurationThresholdAndCount],
    ) -> bool:
        if get_total_investigations() >= config.max_investigations:
            limited_logger.log("Max investigations reached")
            return False

        if trigger_type == "Error":
            return self._check_error_limits()
        elif trigger_type == "Duration":
            if threshold is None:
                return False
            return self._check_duration_limits(flow_id, threshold)

    def _check_error_limits(self) -> bool:
        if (
            get_total_investigations_error_based()
            >= config.max_investigations_error_based
        ):
            limited_logger.log("Max error-based investigations reached")
            return False

        # Deduplication checking with dedup_key happens later in
        # processor._check_dedup() after the dedup_key is extracted via
        # _apply_error_breakdown().
        return True

    def _check_duration_limits(
        self,
        flow_id: str,
        threshold: EndpointDurationThresholdAndCount,
    ) -> bool:
        if (
            get_total_investigations_duration_based()
            >= config.max_investigations_duration_based
        ):
            limited_logger.log("Max duration-based investigations reached")
            return False

        current_count = get_investigation_duration_count(flow_id)
        if current_count >= threshold.number_of_dumps:
            limited_logger.log("Max duration investigations for endpoint reached")
            return False

        return True

    def record_investigation(
        self, trigger_type: InvestigationTriggerType, flow_id: str
    ) -> None:
        increase_total_investigations()

        if trigger_type == "Error":
            increase_total_investigations_error_based()
        elif trigger_type == "Duration":
            increase_total_investigations_duration_based()
            increase_investigation_duration_count(flow_id)
