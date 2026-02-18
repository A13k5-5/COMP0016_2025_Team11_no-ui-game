from pydantic import BaseModel

from graph.serial_node import SerialNode


class SerialGraph(BaseModel):
    nodes: dict[int, SerialNode]
