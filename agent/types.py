from dataclasses import dataclass


@dataclass
class ToolCall:

    name: str

    arguments: dict


@dataclass
class ToolResult:

    name: str

    result: object


@dataclass
class FinalAnswer:

    answer: str