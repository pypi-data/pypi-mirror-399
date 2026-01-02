from typing import Optional
from pydantic import Field
from ipulse_shared_ai_ftredge.models.common.base_versioned_model import BaseVersionedModel
from ipulse_shared_base_ftredge.enums.enums_analysts import (
    ThinkingLevel,
    CreativityLevel,
    WebSearchMode,
    RagRetrievalMode
)

class AIAnalystMode(BaseVersionedModel):
    """
    Represents the 'HOW' of the AI Analyst - their execution capabilities and tools.
    """
    analyst_mode_id: str = Field(..., description="Unique identifier for the analyst mode")
    analyst_mode_name: str = Field(..., description="System name of the mode")
    analyst_mode_display_name: str = Field(..., description="Display name of the mode")
    mode_description: str = Field(..., description="Description of the mode")
    thinking_level: ThinkingLevel = Field(..., description="Level of thinking required")
    creativity_level: CreativityLevel = Field(..., description="Level of creativity allowed")
    web_enabled: bool = Field(..., description="Whether web search is enabled")
    web_search_mode: WebSearchMode = Field(..., description="Mode of web search")
    rag_enabled: bool = Field(..., description="Whether RAG is enabled")
    rag_retrieval_mode: RagRetrievalMode = Field(..., description="Mode of RAG retrieval")
    deep_research_enabled: bool = Field(..., description="Whether deep research is enabled")
    analyst_mode_id_seed_phrase: str = Field(..., description="Seed phrase used to generate the ID")
