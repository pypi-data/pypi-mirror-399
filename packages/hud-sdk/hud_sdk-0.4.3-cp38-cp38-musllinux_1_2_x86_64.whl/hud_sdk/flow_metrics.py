import time
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from . import globals
from .config import config
from .forkable import ForksafeLock, ForksafeMapping
from .instrumentation.limited_logger import limited_logger
from .logging import internal_logger
from .native import RawInvestigation, SketchData, get_time
from .schemas.events import ArqFunctionMetric as ArqMetricEvent
from .schemas.events import EndpointMetric as EndpointMetricEvent
from .schemas.events import FlowMetric as FlowMetricEvent
from .schemas.events import KafkaMetric as KafkaMetricEvent
from .schemas.events import Sketch
from .schemas.investigation import AggregatedErrorBreakdown, ErrorBreakdown
from .utils import get_time_since_epoch_in_ns, timestamp_to_ns


class FlowMetric(ABC):
    def __init__(self, flow_id: Optional[str] = None) -> None:
        self.flow_id = flow_id
        self.duration = 0
        self.start_time = 0
        self.error_breakdown: Optional[ErrorBreakdown] = None

    def start(self) -> None:
        self.start_time = get_time()

    def stop(self) -> None:
        if self.start_time > 0:
            self.duration = get_time() - self.start_time

    def save(self) -> None:
        if globals.metrics_aggregator is None:
            internal_logger.error("Metrics aggregator is not initialized")
            return
        globals.metrics_aggregator.add_metric(self)

    def set_error_breakdown(self, error_breakdown: ErrorBreakdown) -> None:
        self.error_breakdown = error_breakdown

    @abstractmethod
    def get_aggregation_key(self) -> str:
        pass

    def type_name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def get_status(self) -> Optional[str]:
        pass


class MetricWithError(FlowMetric):
    def __init__(self, flow_id: Optional[str] = None) -> None:
        super().__init__(flow_id)
        self.error = None  # type: Optional[str]

    def set_error(self, error: Optional[str]) -> None:
        self.error = error

    def update_error_from_investigation(self, investigation: RawInvestigation) -> None:
        if investigation.user_defined_error is None:
            return

        self.set_error(investigation.user_defined_error)

    def get_status(self) -> Optional[str]:
        return self.error


class EndpointMetric(FlowMetric):
    def __init__(self, flow_id: Optional[str] = None) -> None:
        super().__init__(flow_id)
        self.status_code = None  # type: Optional[int]
        self.method = None  # type: Optional[str]

    def set_request_attributes(self, method: str) -> None:
        self.method = method.upper()

    def set_response_attributes(self, status_code: int) -> None:
        self.status_code = status_code

    def get_aggregation_key(self) -> str:
        if self.flow_id is None or self.method is None or self.status_code is None:
            internal_logger.warning(
                "Metric is missing required attributes",
                data=self.__dict__,
            )
            raise ValueError("Metric is missing required attributes")

        key = "{}|{}|{}".format(self.flow_id, self.method, self.status_code)
        return key

    def get_status(self) -> Optional[str]:
        if self.status_code is None:
            return None

        return str(self.status_code)


class KafkaMetric(MetricWithError):
    def __init__(self, flow_id: Optional[str] = None) -> None:
        super().__init__(flow_id)
        self.partition = None  # type: Optional[int]
        self.produced_timestamp = None  # type: Optional[int]
        self.total_consumed_duration = 0

    def set_partition(self, partition: int) -> None:
        self.partition = partition

    def set_produced_timestamp(self, produced_timestamp: Optional[int]) -> None:
        self.produced_timestamp = produced_timestamp

    def stop(self) -> None:
        super().stop()
        if self.produced_timestamp:
            self.total_consumed_duration = (
                get_time_since_epoch_in_ns() - timestamp_to_ns(self.produced_timestamp)
            )

    def get_aggregation_key(self) -> str:
        if self.flow_id is None or self.partition is None:
            internal_logger.warning(
                "Metric is missing required attributes",
                data=self.__dict__,
            )
            raise ValueError("Metric is missing required attributes")
        key = "{}|{}".format(self.flow_id, self.partition)
        return key


class ArqMetric(MetricWithError):
    def __init__(self, flow_id: Optional[str] = None) -> None:
        super().__init__(flow_id)
        self.e2e_sum_duration = 0  # type: int
        self.enqueue_time = 0  # type: float

    def set_start_time(self, start_time: int) -> None:
        self.start_time = start_time

    def set_enqueue_time(self, enqueue_time: float) -> None:
        self.enqueue_time = enqueue_time

    def stop(self) -> None:
        super().stop()
        if self.enqueue_time:
            self.e2e_sum_duration = get_time_since_epoch_in_ns() - timestamp_to_ns(
                self.enqueue_time
            )

    def get_aggregation_key(self) -> str:
        if self.flow_id is None:
            internal_logger.warning(
                "Metric is missing required attributes",
                data=self.__dict__,
            )
            raise ValueError("Metric is missing required attributes")
        key = self.flow_id
        return key


class AggregatedFlowMetric(ABC):
    def __init__(self, flow_id: str) -> None:
        self.flow_id = flow_id
        self.count = 0
        self.sum_duration = 0
        self.sum_squared_duration = 0.0
        self.sketch_data = SketchData(config.sketch_bin_width)
        self.error_breakdowns: Dict[str, AggregatedErrorBreakdown] = {}

    def update(self, metric: FlowMetric) -> None:
        self.count += 1
        self.sum_duration += metric.duration
        self.sum_squared_duration += metric.duration**2
        if metric.duration != 0:
            self.sketch_data.add(metric.duration)

        if metric.error_breakdown:
            key = metric.error_breakdown.key
            if key not in self.error_breakdowns:
                self.error_breakdowns[key] = AggregatedErrorBreakdown(
                    errors=metric.error_breakdown.errors,
                    failure_type=metric.error_breakdown.failure_type,
                    count=0,
                )
            self.error_breakdowns[key].count += 1

    @abstractmethod
    def to_event(self, timeslice: int) -> FlowMetricEvent:
        pass

    @classmethod
    @abstractmethod
    def create_from_metric(cls, metric: FlowMetric) -> "AggregatedFlowMetric":
        pass


class AggregatedEndpointMetric(AggregatedFlowMetric):
    def __init__(self, flow_id: str, method: str, status_code: int) -> None:
        super().__init__(flow_id)
        self.method = method
        self.status_code = status_code

    def to_event(self, timeslice: int) -> EndpointMetricEvent:
        if self.count == 0:
            raise ValueError("No metrics to aggregate")

        sketch = Sketch(
            bin_width=self.sketch_data.bin_width,
            index_shift=self.sketch_data.index_shift,
            data=self.sketch_data.data.copy(),
        )

        error_breakdown_list = None
        if self.error_breakdowns:
            error_breakdown_list = list(self.error_breakdowns.values())

        return EndpointMetricEvent(
            flow_id=self.flow_id,
            count=self.count,
            sum_duration=self.sum_duration,
            sum_squared_duration=self.sum_squared_duration,
            timeslice=timeslice,
            timestamp=datetime.now(timezone.utc),
            sketch=sketch,
            status_code=self.status_code,
            method=self.method,
            error_breakdown=error_breakdown_list,
        )

    @classmethod
    def create_from_metric(cls, metric: FlowMetric) -> "AggregatedEndpointMetric":
        if not isinstance(metric, EndpointMetric):
            raise TypeError("metric must be an EndpointMetric")
        if (
            metric.flow_id is None
            or metric.method is None
            or metric.status_code is None
        ):
            raise ValueError("Metric is missing required attributes")
        return cls(
            flow_id=metric.flow_id,
            method=metric.method,
            status_code=metric.status_code,
        )


class AggregatedErroredMetric(AggregatedFlowMetric):
    def __init__(self, flow_id: str, errors: Dict[str, int]) -> None:
        super().__init__(flow_id)
        self.errors = errors  # type: Dict[str, int]

    def update(self, metric: FlowMetric) -> None:
        super().update(metric)
        if not isinstance(metric, MetricWithError):
            return

        if metric.error is not None:
            if metric.error not in self.errors:
                if len(self.errors) >= config.max_metric_errors:
                    # Since the error string can be configured by the user, we want to make sure this buffer doesn't explode
                    limited_logger.log(
                        "Flow metrics max errors reached",
                        data={"flow_id": self.flow_id},
                    )
                    self.errors["HUD_MAX_ERRORS_REACHED"] = (
                        self.errors.get("HUD_MAX_ERRORS_REACHED", 0) + 1
                    )
                    return

                self.errors[metric.error] = 1
            else:
                self.errors[metric.error] += 1


class AggregatedKafkaMetric(AggregatedErroredMetric):
    def __init__(self, flow_id: str, partition: int, errors: Dict[str, int]) -> None:
        super().__init__(flow_id, errors)
        self.partition = partition
        self.sum_consumed_duration = 0
        self.sum_squared_consumed_duration = 0.0
        self.sketch_consumed_data = SketchData(config.sketch_bin_width)

    def update(self, metric: FlowMetric) -> None:
        super().update(metric)
        if not isinstance(metric, KafkaMetric):
            return
        if metric.total_consumed_duration != 0:
            self.sum_consumed_duration += metric.total_consumed_duration
            self.sum_squared_consumed_duration += metric.total_consumed_duration**2
            self.sketch_consumed_data.add(metric.total_consumed_duration)

    def to_event(self, timeslice: int) -> KafkaMetricEvent:
        if self.count == 0:
            raise ValueError("No metrics to aggregate")

        sketch = Sketch(
            bin_width=self.sketch_data.bin_width,
            index_shift=self.sketch_data.index_shift,
            data=self.sketch_data.data.copy(),
        )
        sketch_consumed = Sketch(
            bin_width=self.sketch_consumed_data.bin_width,
            index_shift=self.sketch_consumed_data.index_shift,
            data=self.sketch_consumed_data.data.copy(),
        )

        return KafkaMetricEvent(
            flow_id=self.flow_id,
            count=self.count,
            sum_duration=self.sum_duration,
            sum_squared_duration=self.sum_squared_duration,
            timeslice=timeslice,
            timestamp=datetime.now(timezone.utc),
            sketch=sketch,
            partition=self.partition,
            errors=self.errors,
            sum_consumed_duration=self.sum_consumed_duration,
            sum_squared_consumed_duration=self.sum_squared_consumed_duration,
            sketch_consume=sketch_consumed,
        )

    @classmethod
    def create_from_metric(cls, metric: FlowMetric) -> "AggregatedKafkaMetric":
        if not isinstance(metric, KafkaMetric):
            raise TypeError("metric must be a KafkaMetric")
        if metric.flow_id is None or metric.partition is None:
            raise ValueError("Metric is missing required attributes")
        return cls(flow_id=metric.flow_id, partition=metric.partition, errors={})


class AggregatedArqMetric(AggregatedErroredMetric):
    def __init__(self, flow_id: str, errors: Dict[str, int]) -> None:
        super().__init__(flow_id, errors)
        self.e2e_sum_duration = 0
        self.e2e_sum_squared_duration = 0.0
        self.e2e_sketch_data = SketchData(config.sketch_bin_width)

    def update(self, metric: FlowMetric) -> None:
        super().update(metric)
        if not isinstance(metric, ArqMetric):
            return

        if metric.e2e_sum_duration != 0:
            self.e2e_sum_duration += metric.e2e_sum_duration
            self.e2e_sum_squared_duration += metric.e2e_sum_duration**2
            self.e2e_sketch_data.add(metric.e2e_sum_duration)

    def to_event(self, timeslice: int) -> ArqMetricEvent:
        if self.count == 0:
            raise ValueError("No metrics to aggregate")

        sketch = Sketch(
            bin_width=self.sketch_data.bin_width,
            index_shift=self.sketch_data.index_shift,
            data=self.sketch_data.data.copy(),
        )
        e2e_sketch = Sketch(
            bin_width=self.e2e_sketch_data.bin_width,
            index_shift=self.e2e_sketch_data.index_shift,
            data=self.e2e_sketch_data.data.copy(),
        )

        error_breakdown_list = None
        if self.error_breakdowns:
            error_breakdown_list = list(self.error_breakdowns.values())

        return ArqMetricEvent(
            flow_id=self.flow_id,
            count=self.count,
            sum_duration=self.sum_duration,
            sum_squared_duration=self.sum_squared_duration,
            timeslice=timeslice,
            timestamp=datetime.now(timezone.utc),
            sketch=sketch,
            e2e_sum_duration=self.e2e_sum_duration,
            e2e_sum_squared_duration=self.e2e_sum_squared_duration,
            e2e_sketch=e2e_sketch,
            errors=self.errors,
            error_breakdown=error_breakdown_list,
        )

    @classmethod
    def create_from_metric(cls, metric: FlowMetric) -> "AggregatedArqMetric":
        if not isinstance(metric, ArqMetric):
            raise TypeError("metric must be an ArqMetric")
        if metric.flow_id is None:
            raise ValueError("Metric is missing required attributes")
        return cls(
            flow_id=metric.flow_id,
            errors={},
        )


class FlowMetricsAggregator:
    def __init__(self) -> None:
        self.aggregated_metrics_storage = ForksafeMapping(
            lambda: defaultdict(dict)
        )  # type: ForksafeMapping[str, Dict[str, AggregatedFlowMetric]]
        self.lock = ForksafeLock()
        self.last_dump = time.perf_counter()

    def add_metric(self, metric: FlowMetric) -> None:
        metric_type = metric.type_name()
        try:
            aggregation_key = metric.get_aggregation_key()
        except ValueError:
            internal_logger.warning(
                "Failed to get aggregation key for metric",
                data=metric.__dict__,
            )
            return

        with self.lock:
            if aggregation_key in self.aggregated_metrics_storage[metric_type]:
                try:
                    aggregated_metric = self.aggregated_metrics_storage[metric_type][
                        aggregation_key
                    ]
                    aggregated_metric.update(metric)
                except Exception:
                    internal_logger.warning(
                        "Failed to update aggregated metric",
                        data=metric.__dict__,
                        exc_info=True,
                    )
            else:
                try:
                    if isinstance(metric, EndpointMetric):
                        aggregated_metric = AggregatedEndpointMetric.create_from_metric(
                            metric
                        )
                    elif isinstance(metric, KafkaMetric):
                        aggregated_metric = AggregatedKafkaMetric.create_from_metric(
                            metric
                        )
                    elif isinstance(metric, ArqMetric):
                        aggregated_metric = AggregatedArqMetric.create_from_metric(
                            metric
                        )
                    else:
                        internal_logger.warning(
                            "Unsupported metric type",
                            data={"metric_type": metric_type},
                        )
                        return

                    aggregated_metric.update(metric)
                    self.aggregated_metrics_storage[metric_type][
                        aggregation_key
                    ] = aggregated_metric

                except Exception:
                    internal_logger.warning(
                        "Failed to create aggregated metric",
                        data=metric.__dict__,
                        exc_info=True,
                    )

    def get_and_clear_metrics(self) -> Dict[str, List[FlowMetricEvent]]:
        aggregated_metrics = self._get_and_clear_metrics()
        return self._create_events_from_aggregated(aggregated_metrics)

    def _get_and_clear_metrics(self) -> Dict[str, Dict[str, AggregatedFlowMetric]]:
        with self.lock:
            current_metrics = self.aggregated_metrics_storage.get_wrapped()
            self.aggregated_metrics_storage.reset_wrapped()
        return current_metrics

    def _create_events_from_aggregated(
        self, aggregated_metrics: Dict[str, Dict[str, AggregatedFlowMetric]]
    ) -> Dict[str, List[FlowMetricEvent]]:
        timeslice = self._calculate_timeslice()
        events = defaultdict(list)  # type: Dict[str, List[FlowMetricEvent]]

        for metric_type, metrics in aggregated_metrics.items():
            for aggregated_metric in metrics.values():
                try:
                    event = aggregated_metric.to_event(timeslice)
                    events[metric_type].append(event)
                except ValueError:
                    internal_logger.warning(
                        "Failed to create event from aggregated metric",
                        data=aggregated_metric.__dict__,
                        exc_info=True,
                    )
                    pass

        return events

    def _calculate_timeslice(self) -> int:
        current_time = time.perf_counter()
        timeslice = int(current_time - self.last_dump)
        self.last_dump = current_time
        return timeslice


globals.metrics_aggregator = FlowMetricsAggregator()
