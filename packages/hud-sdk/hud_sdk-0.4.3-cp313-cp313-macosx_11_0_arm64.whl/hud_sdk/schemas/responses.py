from typing import Any, Dict, List, Optional, cast

from .events import FileDeclaration
from .investigation import EndpointDurationThresholdAndCount
from .schema import JSON, Schema


class FileDeclarations(Schema):

    def __init__(self, files: List[FileDeclaration], send_all: bool):
        self.files: List[FileDeclaration] = files
        self.send_all = send_all

    @staticmethod
    def from_json_data(data: JSON) -> "FileDeclarations":
        if not isinstance(data, dict):
            raise ValueError("Invalid data")

        files = data.get("files")
        send_all = data.get("send_all")
        if not isinstance(files, list) or not isinstance(send_all, bool):
            raise ValueError("Invalid data")

        return FileDeclarations(
            files=[FileDeclaration.from_json_data(file) for file in files],
            send_all=send_all,
        )


class EndpointDurationThresholdAndCountMapping(
    Dict[str, EndpointDurationThresholdAndCount]
):
    def __init__(
        self, mapping: Optional[Dict[str, EndpointDurationThresholdAndCount]] = None
    ):
        super().__init__(mapping or {})

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {flow_id: threshold.to_dict() for flow_id, threshold in self.items()}

    @staticmethod
    def from_json_data(data: JSON) -> "EndpointDurationThresholdAndCountMapping":
        if not isinstance(data, dict):
            raise ValueError("Invalid data")

        mapping: Dict[str, EndpointDurationThresholdAndCount] = {}
        for flow_id, threshold_data in data.items():
            if not isinstance(threshold_data, dict):
                raise ValueError("Invalid data")
            mapping[cast(str, flow_id)] = EndpointDurationThresholdAndCount(
                duration=cast(int, threshold_data["duration"]),
                number_of_dumps=cast(int, threshold_data["number_of_dumps"]),
            )
        return EndpointDurationThresholdAndCountMapping(mapping)
