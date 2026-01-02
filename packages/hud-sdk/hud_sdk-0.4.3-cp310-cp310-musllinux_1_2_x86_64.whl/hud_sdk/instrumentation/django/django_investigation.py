import json
from typing import TYPE_CHECKING, Any, cast

from ...flow_metrics import EndpointMetric
from ...schemas.investigation import BaseInvestigationData, HttpInvestigationContext
from ..apm_trace_ids import collect_apm_trace_ids
from ..investigation.http_investigation import (
    HttpInvestigationProcessor,
    safe_get_header,
)
from ..investigation.investigation_utils import minimize_object_with_defaults
from ..limited_logger import limited_logger

if TYPE_CHECKING:
    from django.http import HttpRequest


class DjangoProcessor(HttpInvestigationProcessor):
    def build_context(
        self,
        base_data: BaseInvestigationData,
        metric: EndpointMetric,
        **framework_data: Any,
    ) -> HttpInvestigationContext:
        request = framework_data.get("request")
        if request is None:
            raise ValueError("request is required")

        path = request.path
        apm_trace_ids = collect_apm_trace_ids(request.headers)

        try:
            body = json.loads(request.body)
        except Exception:
            body = None

        return HttpInvestigationContext(
            timestamp=base_data.timestamp,
            machine_metrics=base_data.machine_metrics,
            system_info=base_data.system_info,
            status_code=cast(int, metric.status_code),
            route=path or "unknown",
            method=metric.method or "unknown",
            query_params=minimize_object_with_defaults(request.GET),
            path_params=minimize_object_with_defaults(self._get_path_params(request)),
            body=minimize_object_with_defaults(body),
            observability_identifiers=apm_trace_ids,
            content_type=request.content_type,
            content_encoding=safe_get_header(request.headers, "Content-Encoding"),
            user_context=base_data.user_context,
        )

    def _get_path_params(self, request: "HttpRequest") -> Any:
        try:
            path_params = getattr(request, "resolver_match")
            if path_params:
                return path_params.kwargs
        except Exception:
            limited_logger.log("Failed to get path params from request")
        return None
