from typing import Optional
from pydantic import Field
from ipulse_shared_ai_ftredge.models.common.base_versioned_model import BaseVersionedModel

class AIAnalyst(BaseVersionedModel):
    """
    Represents an instantiation of an Analyst Persona with a specific Model and Assembly.
    """
    analyst_id: str = Field(..., description="Unique identifier for the analyst")
    analyst_name: str = Field(..., description="Name of the analyst")
    analyst_persona_id: str = Field(..., description="ID of the persona")
    model_spec_id: str = Field(..., description="ID of the model specification")
    model_spec_name: str = Field(..., description="Name of the model specification")
    model_version_id: str = Field(..., description="ID of the model version")
    model_version_name: str = Field(..., description="Name of the model version")
    model_training_config_id: Optional[str] = Field(None, description="ID of the training configuration")
    model_version_agnostic: bool = Field(False, description="Whether the analyst is agnostic to model versions")
    ai_analyst_assembly_variant_id: str = Field(..., description="ID of the assembly variant")
    ai_analyst_assembly_variant_name: str = Field(..., description="Name of the assembly variant")
    analyst_id_seed_phrase: str = Field(..., description="Seed phrase used to generate the ID")
