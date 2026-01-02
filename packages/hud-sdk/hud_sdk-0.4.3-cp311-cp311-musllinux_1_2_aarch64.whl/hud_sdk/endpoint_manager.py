from typing import Dict, List, Optional  # noqa: F401

from ._internal import worker_queue
from .schemas.events import EndpointDeclaration
from .utils import calculate_uuid


def _normalize_methods(methods: List[str]) -> List[str]:
    methods = [method.upper() for method in methods]
    return sorted(methods)


def calculate_endpoint_flow_id(path: str, methods: List[str]) -> str:
    methods_sorted = _normalize_methods(methods)
    unique_string = "{}|{}".format(path, methods_sorted)
    return str(calculate_uuid(unique_string))


class EndpointManager:
    def __init__(self) -> None:
        self.endpoint_to_id = {}  # type: Dict[str, str]

    def save_endpoint_declaration(
        self,
        path: str,
        methods: List[str],
        framework: str,
        flow_id: Optional[str] = None,
    ) -> str:
        if not flow_id:
            flow_id = calculate_endpoint_flow_id(path, methods)

        methods = _normalize_methods(methods)
        endpoint_declaration = EndpointDeclaration(flow_id, path, methods, framework)
        worker_queue.append(endpoint_declaration)

        for method in methods:
            key = "{}|{}".format(path, method.upper())
            self.endpoint_to_id[key] = flow_id

        return flow_id

    def get_endpoint_id(self, path: str, method: str) -> Optional[str]:
        key = "{}|{}".format(path, method.upper())
        return self.endpoint_to_id.get(key)


class EndpointsDeclarationsAggregator:
    def __init__(self) -> None:
        self.declarations = []  # type: List[EndpointDeclaration]

    def add_declaration(self, declaration: EndpointDeclaration) -> None:
        self.declarations.append(declaration)

    def get_and_clear_declarations(self) -> List[EndpointDeclaration]:
        declarations = [declaration for declaration in self.declarations]
        self.clear()
        return declarations

    def clear(self) -> None:
        self.declarations = []
