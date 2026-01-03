# PyroMind Node SDK

A lightweight SDK stub for local development and testing of third-party nodes without the full platform codebase (without `app.models.nodes`).

In the real platform runtime environment, nodes should prioritize importing base classes from `app.models.nodes`.

## Installation

```bash
pip install pyromind-sdk
```

## Usage

```python
from pyromind_sdk import BaseNode, PodExecutionNode, NodeType

# Create a custom node
class MyCustomNode(PodExecutionNode):
    CATEGORY = "custom"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    DISPLAY_NAME = "My Custom Node"
    
    @classmethod
    def BASE_INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"default": ""}),
            }
        }
    
    def execute(self, input_text):
        return (input_text.upper(),)
```

## Main Classes

- `BaseNode`: Base class for all nodes
- `PodExecutionNode`: Base class for Pod execution nodes
- `PortPodExecutionNode`: Pod execution node with port resource
- `DaemonPodExecutionNode`: Daemon Pod execution node
- `GpuPodExecutionNode`: GPU Pod execution node
- `JupyterLabPodExecutionNode`: Pod execution node with JupyterLab environment
- `PassThroughNode`: Pass-through node
- `EndpointNode`: Base class for endpoint nodes
- `NodeType`: Node type enumeration

## Development

### Building the Package

```bash
pip install build
python -m build
```

### Publishing to PyPI

```bash
pip install twine
twine upload dist/*
```

## License

MIT License

## Links

- Website: https://pyromind.ai/
