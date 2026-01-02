from dataclasses import dataclass
from typing import Any, Dict, Optional, cast

from ...flow_metrics import EndpointMetric
from ...schemas.investigation import BaseInvestigationData, HttpInvestigationContext
from ..apm_trace_ids import collect_apm_trace_ids
from .http_investigation import (
    HttpInvestigationProcessor,
    safe_get_header,
)
from .investigation_utils import minimize_object_with_defaults


@dataclass
class FlaskRequestData:
    request_body: Optional[Any] = None
    query: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    path: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None


class FlaskProcessor(HttpInvestigationProcessor):
    def build_context(
        self,
        base_data: BaseInvestigationData,
        metric: EndpointMetric,
        **framework_data: Any,
    ) -> HttpInvestigationContext:
        flask_data = framework_data.get("flask_data")
        if not flask_data:
            raise ValueError("flask_data is required")

        path = flask_data.path
        apm_trace_ids = collect_apm_trace_ids(flask_data.headers)

        return HttpInvestigationContext(
            timestamp=base_data.timestamp,
            machine_metrics=base_data.machine_metrics,
            system_info=base_data.system_info,
            status_code=cast(int, metric.status_code),
            route=path or "unknown",
            method=metric.method or "unknown",
            query_params=minimize_object_with_defaults(flask_data.query),
            path_params=minimize_object_with_defaults(flask_data.params),
            body=minimize_object_with_defaults(flask_data.request_body),
            observability_identifiers=apm_trace_ids,
            content_type=safe_get_header(flask_data.headers, "content-type"),
            content_encoding=safe_get_header(flask_data.headers, "content-encoding"),
            user_context=base_data.user_context,
        )
