import pytest
from griptape_nodes.exe_types.connections import Connections
from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

from storyboard.storyboard_image_node import StoryboardImageNode


class ImageListSource(DataNode):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.add_parameter(
            Parameter(
                name="images", output_type="list", allowed_modes={ParameterMode.OUTPUT}
            )
        )


@pytest.fixture
def connections(monkeypatch: pytest.MonkeyPatch) -> Connections:
    connections = Connections()
    flow_manager = GriptapeNodes.FlowManager()
    monkeypatch.setattr(flow_manager, "get_connections", lambda: connections)
    return connections


def test_validation_passes_when_images_is_connected(connections: Connections) -> None:
    source = ImageListSource(name="source")
    node = StoryboardImageNode(name="storyboard")
    connections.add_connection(
        source,
        source.get_parameter_by_name("images"),
        node,
        node.get_parameter_by_name("images"),
    )

    assert node.validate_before_workflow_run() is None


@pytest.mark.usefixtures("connections")
def test_validation_fails_when_images_is_unconnected_and_empty() -> None:
    node = StoryboardImageNode(name="storyboard")

    exceptions = node.validate_before_workflow_run()

    assert exceptions is not None
    assert len(exceptions) == 1
    assert "No images provided" in str(exceptions[0])
