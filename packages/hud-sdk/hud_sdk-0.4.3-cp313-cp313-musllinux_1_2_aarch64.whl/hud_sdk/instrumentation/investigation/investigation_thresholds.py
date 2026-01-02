from dataclasses import dataclass
from typing import Dict, Optional

from ...schemas.investigation import EndpointDurationThresholdAndCount
from ...schemas.responses import EndpointDurationThresholdAndCountMapping

_investigation_duration_thresholds: EndpointDurationThresholdAndCountMapping = (
    EndpointDurationThresholdAndCountMapping({})
)
_investigation_duration_counters: Dict[str, int] = {}
_total_investigations_error_based: int = 0
_total_investigations_duration_based: int = 0


def set_investigation_duration_thresholds(
    thresholds: EndpointDurationThresholdAndCountMapping,
) -> None:
    global _investigation_duration_thresholds
    _investigation_duration_thresholds = EndpointDurationThresholdAndCountMapping({})
    for flow_id, threshold_data in thresholds.items():
        _investigation_duration_thresholds[flow_id] = threshold_data


def get_investigation_duration_thresholds() -> EndpointDurationThresholdAndCountMapping:
    return _investigation_duration_thresholds


def get_flow_id_duration_threshold_and_count(
    flow_id: str,
) -> Optional[EndpointDurationThresholdAndCount]:
    return _investigation_duration_thresholds.get(flow_id)


def get_effective_duration_threshold(
    flow_id: str, framework_type: str
) -> Optional[EndpointDurationThresholdAndCount]:
    threshold = get_flow_id_duration_threshold_and_count(flow_id)
    if threshold is None:
        threshold = get_flow_id_duration_threshold_and_count(
            f"default-{framework_type}"
        )
    return threshold


@dataclass
class InvestigationEvaluationContext:
    framework_type: str
    threshold: Optional[EndpointDurationThresholdAndCount] = None

    @classmethod
    def create(
        cls, flow_id: str, framework_type: str
    ) -> "InvestigationEvaluationContext":
        threshold = get_effective_duration_threshold(flow_id, framework_type)
        return cls(framework_type=framework_type, threshold=threshold)

    def exceeds_duration_threshold(self, duration: int) -> bool:
        if self.threshold is None:
            return False
        return duration > self.threshold.duration


def get_duration_threshold_for_investigation(
    flow_id: str,
    framework_type: str,
) -> Optional[int]:
    threshold_config = get_effective_duration_threshold(flow_id, framework_type)
    if threshold_config:
        return threshold_config.duration

    return None


def increase_investigation_duration_count(flow_id: str) -> None:
    global _investigation_duration_counters
    _investigation_duration_counters[flow_id] = (
        _investigation_duration_counters.get(flow_id, 0) + 1
    )


def get_investigation_duration_count(flow_id: str) -> int:
    return _investigation_duration_counters.get(flow_id, 0)


def reset_investigation_duration_counts() -> None:
    global _investigation_duration_counters
    _investigation_duration_counters = {}


def get_total_investigations_error_based() -> int:
    return _total_investigations_error_based


def increase_total_investigations_error_based() -> None:
    global _total_investigations_error_based
    _total_investigations_error_based += 1


def reset_total_investigations_error_based() -> None:
    global _total_investigations_error_based
    _total_investigations_error_based = 0


def get_total_investigations_duration_based() -> int:
    return _total_investigations_duration_based


def increase_total_investigations_duration_based() -> None:
    global _total_investigations_duration_based
    _total_investigations_duration_based += 1


def reset_total_investigations_duration_based() -> None:
    global _total_investigations_duration_based
    _total_investigations_duration_based = 0


def reset_total_investigations() -> None:
    reset_total_investigations_error_based()
    reset_total_investigations_duration_based()
