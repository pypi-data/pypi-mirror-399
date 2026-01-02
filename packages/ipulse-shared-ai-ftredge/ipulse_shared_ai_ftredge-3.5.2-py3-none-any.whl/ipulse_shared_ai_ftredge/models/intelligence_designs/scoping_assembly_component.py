from typing import List, Optional
from pydantic import BaseModel, Field

class ScopingAssemblyComponent(BaseModel):
    """
    Represents a component in the prompt assembly.
    """
    component_id: str = Field(..., description="Unique identifier for the component")
    component_name: str = Field(..., description="Name of the component")
    component_type: str = Field(..., description="Type of the component")
    component_description: str = Field(..., description="Description of the component")
    prompt_template: str = Field(..., description="Template for the prompt")
    prompt_variables: List[str] = Field(default_factory=list, description="Variables used in the prompt template")
    is_mandatory: bool = Field(..., description="Whether the component is mandatory")
    order_index: int = Field(..., description="Order index of the component in the assembly")
