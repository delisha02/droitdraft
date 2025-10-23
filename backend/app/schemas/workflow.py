
from pydantic import BaseModel
from typing import List, Optional

class WorkflowNode(BaseModel):
    name: str
    type: str
    entry: Optional[bool] = False

class WorkflowEdge(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None

class WorkflowDefinition(BaseModel):
    name: str
    version: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
