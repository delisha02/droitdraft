
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.llm_service import LLMService

@pytest.fixture
def llm_service():
    return LLMService()

@pytest.mark.asyncio
@patch('app.agents.document_generator.llm_client.llm_client.generate', new_callable=AsyncMock)
async def test_generate_document_groq(mock_generate, llm_service):
    mock_generate.return_value = "**Generated Document:**\nThis is a test document."
    
    case_facts = {"plaintiff": "John Doe", "defendant": "Jane Smith"}
    template = "[plaintiff] v. [defendant]"
    
    document = await llm_service.generate_document(case_facts, template, use_groq=True)
    
    assert document == "This is a test document."
    mock_generate.assert_called_once()
    assert llm_service.get_token_usage() > 0

@pytest.mark.asyncio
@patch('app.agents.document_generator.llm_client.llm_client.generate', new_callable=AsyncMock)
async def test_generate_document_gemini(mock_generate, llm_service):
    mock_generate.return_value = "**Generated Document:**\nThis is a test document from Gemini."
    
    case_facts = {"plaintiff": "John Doe", "defendant": "Jane Smith"}
    template = "[plaintiff] v. [defendant]"
    
    document = await llm_service.generate_document(case_facts, template, use_groq=False)
    
    assert document == "This is a test document from Gemini."
    mock_generate.assert_called_once()
    assert llm_service.get_token_usage() > 0

@patch('app.agents.document_generator.prompt_templates.create_generation_prompt')
def test_token_tracking(mock_create_prompt, llm_service):
    mock_create_prompt.return_value = "This is a prompt."
    llm_service.token_tracker.track("This is a prompt.")
    assert llm_service.get_token_usage() > 0
