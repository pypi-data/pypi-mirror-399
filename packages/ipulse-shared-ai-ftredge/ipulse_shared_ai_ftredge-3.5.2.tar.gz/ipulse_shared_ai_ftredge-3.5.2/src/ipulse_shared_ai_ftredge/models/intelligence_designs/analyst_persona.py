from typing import List, Optional
from pydantic import Field
from ipulse_shared_ai_ftredge.models.common.base_versioned_model import BaseVersionedModel

class AnalystPersona(BaseVersionedModel):
    """
    Represents the 'WHO' of the AI Analyst - their personality, philosophy, and cognitive style.
    """
    analyst_persona_id: str = Field(..., description="Unique identifier for the analyst persona")
    analyst_persona_name: str = Field(..., description="System name of the persona")
    analyst_persona_display_name: str = Field(..., description="Display name of the persona")
    investment_philosophy: str = Field(..., description="Description of the investment philosophy")
    risk_tolerance: str = Field(..., description="Risk tolerance level description")
    primary_focus_areas: List[str] = Field(default_factory=list, description="List of primary focus areas")
    communication_style_traits: List[str] = Field(default_factory=list, description="List of communication style traits")
    cognitive_biases_to_simulate: List[str] = Field(default_factory=list, description="List of cognitive biases to simulate")
    persona_description: str = Field(..., description="Detailed description of the persona")
    system_prompt_template: str = Field(..., description="Template for the system prompt")
    system_prompt_variables: List[str] = Field(default_factory=list, description="Variables used in the system prompt template")
    analyst_persona_id_seed_phrase: str = Field(..., description="Seed phrase used to generate the ID")
