import gzip
import json
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional, Union, cast

from ...config import config
from ...flow_metrics import EndpointMetric
from ...schemas.investigation import (
    BaseInvestigationData,
    HttpInvestigationContext,
)
from ..limited_logger import limited_logger
from .http_investigation import (
    HttpInvestigationProcessor,
    safe_get_header,
)
from .investigation_utils import minimize_object_with_defaults

if TYPE_CHECKING:
    from starlette.datastructures import Headers


def bytes_to_generator(body: bytes) -> AsyncGenerator[bytes, None]:
    async def generator() -> AsyncGenerator[bytes, None]:
        yield body
        # The FormBody parser expect an empty body at the end so it will know the body is finished (not sure why the end of the iteration is not enough)
        yield b""

    return generator()


async def safe_parse_body(
    body: bytes, headers: Optional[Any], is_truncated: bool
) -> Union[Any, bytes]:
    # This functions is based on https://github.com/fastapi/fastapi/blob/97fdbdd0d8b3e24b3d850865033f6746ee13f82c/fastapi/routing.py#L242
    if is_truncated:
        return body

    try:
        if headers is None:
            return json.loads(body)

        headers = safe_parse_headers(headers)

        if headers is None:
            return json.loads(body)

        encoding = headers.get("content-encoding", "")
        if encoding == "gzip":
            try:
                body = gzip.decompress(body)
            except Exception:
                pass

        content_type = headers.get("content-type", "")
        if content_type == "application/json" or (
            content_type.startswith("application/") and content_type.endswith("+json")
        ):
            return json.loads(body)

        if "multipart/form-data" in content_type:
            from starlette.formparsers import MultiPartParser

            multipart_form_parser = MultiPartParser(headers, bytes_to_generator(body))
            result = dict(await multipart_form_parser.parse())
            parsed_result = {
                key: parse_mutipart_part(value) for key, value in result.items()
            }
            return parsed_result

        if content_type == "application/x-www-form-urlencoded":
            from starlette.formparsers import FormParser

            form_parser = FormParser(headers, bytes_to_generator(body))
            return dict(await form_parser.parse())

        return body
    except Exception as e:
        limited_logger.log(
            "Error parsing body",
            data={"error": str(e)},
        )
        return body


def parse_mutipart_part(value: Any) -> Any:
    from starlette.datastructures import UploadFile

    if isinstance(value, UploadFile):
        return {
            "filename": value.filename,
            "content_type": value.content_type,
            "file": value.file.read(config.investigation_max_string_length),
        }
    return value


def safe_parse_query_string(query_string: str) -> Dict[str, str]:
    try:
        from starlette.datastructures import QueryParams

        return dict(QueryParams(query_string))
    except Exception:
        return dict()


def safe_parse_headers(headers: Optional[Any]) -> Optional["Headers"]:
    try:
        from fastapi.datastructures import Headers

        if headers is None:
            return None

        return Headers(raw=headers)
    except Exception:
        return None


class FastApiProcessor(HttpInvestigationProcessor):
    async def build_context_async(
        self,
        base_data: BaseInvestigationData,
        metric: EndpointMetric,
        **framework_data: Any
    ) -> HttpInvestigationContext:
        headers = framework_data.get("headers")
        query_string = framework_data.get("query_string")
        raw_body = framework_data.get("raw_body")
        is_truncated = framework_data.get("is_truncated", False)
        path_params = framework_data.get("path_params")
        path = framework_data.get("path")

        parsed_body = None
        if raw_body is not None:
            parsed_body = await safe_parse_body(raw_body, headers, is_truncated)
            parsed_body = minimize_object_with_defaults(parsed_body)

        parsed_query = None
        if query_string is not None:
            parsed_query_string = safe_parse_query_string(query_string)
            parsed_query = minimize_object_with_defaults(parsed_query_string)

        headers_dict = safe_parse_headers(headers)
        return HttpInvestigationContext(
            timestamp=base_data.timestamp,
            machine_metrics=base_data.machine_metrics,
            system_info=base_data.system_info,
            status_code=cast(int, metric.status_code),
            route=path or "unknown",
            method=metric.method or "unknown",
            query_params=parsed_query,
            path_params=minimize_object_with_defaults(path_params),
            body=parsed_body,
            observability_identifiers=framework_data.get("apm_trace_ids"),
            content_type=safe_get_header(headers_dict, "content-type"),
            content_encoding=safe_get_header(headers_dict, "content-encoding"),
            user_context=base_data.user_context,
        )
