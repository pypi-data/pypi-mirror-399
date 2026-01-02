from typing import List, Optional
from pydantic import Field
from ipulse_shared_ai_ftredge.models.common.base_versioned_model import BaseVersionedModel
from ipulse_shared_ai_ftredge.models.intelligence_designs.scoping_assembly_component import ScopingAssemblyComponent

class AIAnalystAssemblyVariant(BaseVersionedModel):
    """
    Represents a variant of the prompt assembly configuration.
    """
    ai_analyst_assembly_variant_id: str = Field(..., description="Unique identifier for the assembly variant")
    ai_analyst_assembly_variant_name: str = Field(..., description="Name of the assembly variant")
    assembly_description: str = Field(..., description="Description of the assembly variant")
    scoping_assembly_components: List[ScopingAssemblyComponent] = Field(default_factory=list, description="List of components in the assembly")
    ai_analyst_assembly_variant_id_seed_phrase: str = Field(..., description="Seed phrase used to generate the ID")
