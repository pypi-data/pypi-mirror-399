from typing import Any, Callable, Dict


class Tool:
    def __init__(self, name: str, description: str, schema: Dict, function: Callable):
        self.name = name
        self.description = description
        self.schema = schema
        self.function = function

    def run(self, arguments: Dict[str, Any]):
        return self.function(**arguments)
