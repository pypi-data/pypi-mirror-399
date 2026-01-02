import pytest
from unittest.mock import Mock, patch, MagicMock
from promptbuilder.llm_client.main import get_models_list
from promptbuilder.llm_client.types import Model


def test_get_models_list_all_providers():
    """Test that get_models_list returns models from all providers when no provider specified."""
    with patch('promptbuilder.llm_client.google_client.GoogleLLMClient.models_list') as mock_google, \
         patch('promptbuilder.llm_client.anthropic_client.AnthropicLLMClient.models_list') as mock_anthropic, \
         patch('promptbuilder.llm_client.openai_client.OpenaiLLMClient.models_list') as mock_openai, \
         patch('promptbuilder.llm_client.bedrock_client.BedrockLLMClient.models_list') as mock_bedrock:
        
        # Setup mock returns
        mock_google.return_value = [
            Model(full_model_name="google:gemini-1.5-flash", provider="google", model="gemini-1.5-flash", display_name="Gemini 1.5 Flash")
        ]
        mock_anthropic.return_value = [
            Model(full_model_name="anthropic:claude-3-opus-20240229", provider="anthropic", model="claude-3-opus-20240229", display_name="Claude 3 Opus")
        ]
        mock_openai.return_value = [
            Model(full_model_name="openai:gpt-4", provider="openai", model="gpt-4")
        ]
        mock_bedrock.return_value = [
            Model(full_model_name="bedrock:arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0", 
                  provider="bedrock", 
                  model="arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                  display_name="Claude 3 Sonnet")
        ]
        
        # Call the function
        result = get_models_list()
        
        # Assertions
        assert len(result) == 4
        assert all(isinstance(model, Model) for model in result)
        assert any(model.provider == "google" for model in result)
        assert any(model.provider == "anthropic" for model in result)
        assert any(model.provider == "openai" for model in result)
        assert any(model.provider == "bedrock" for model in result)
        
        # Verify all mocks were called
        mock_google.assert_called_once()
        mock_anthropic.assert_called_once()
        mock_openai.assert_called_once()
        mock_bedrock.assert_called_once()


def test_get_models_list_google_provider():
    """Test that get_models_list returns only Google models when google provider specified."""
    with patch('promptbuilder.llm_client.google_client.GoogleLLMClient.models_list') as mock_google:
        mock_google.return_value = [
            Model(full_model_name="google:gemini-1.5-flash", provider="google", model="gemini-1.5-flash", display_name="Gemini 1.5 Flash"),
            Model(full_model_name="google:gemini-1.5-pro", provider="google", model="gemini-1.5-pro", display_name="Gemini 1.5 Pro")
        ]
        
        result = get_models_list(provider="google")
        
        assert len(result) == 2
        assert all(model.provider == "google" for model in result)
        mock_google.assert_called_once()


def test_get_models_list_anthropic_provider():
    """Test that get_models_list returns only Anthropic models when anthropic provider specified."""
    with patch('promptbuilder.llm_client.anthropic_client.AnthropicLLMClient.models_list') as mock_anthropic:
        mock_anthropic.return_value = [
            Model(full_model_name="anthropic:claude-3-opus-20240229", provider="anthropic", model="claude-3-opus-20240229", display_name="Claude 3 Opus"),
            Model(full_model_name="anthropic:claude-3-sonnet-20240229", provider="anthropic", model="claude-3-sonnet-20240229", display_name="Claude 3 Sonnet")
        ]
        
        result = get_models_list(provider="anthropic")
        
        assert len(result) == 2
        assert all(model.provider == "anthropic" for model in result)
        mock_anthropic.assert_called_once()


def test_get_models_list_openai_provider():
    """Test that get_models_list returns only OpenAI models when openai provider specified."""
    with patch('promptbuilder.llm_client.openai_client.OpenaiLLMClient.models_list') as mock_openai:
        mock_openai.return_value = [
            Model(full_model_name="openai:gpt-4", provider="openai", model="gpt-4"),
            Model(full_model_name="openai:gpt-3.5-turbo", provider="openai", model="gpt-3.5-turbo")
        ]
        
        result = get_models_list(provider="openai")
        
        assert len(result) == 2
        assert all(model.provider == "openai" for model in result)
        mock_openai.assert_called_once()


def test_get_models_list_bedrock_provider():
    """Test that get_models_list returns only Bedrock models when bedrock provider specified."""
    with patch('promptbuilder.llm_client.bedrock_client.BedrockLLMClient.models_list') as mock_bedrock:
        mock_bedrock.return_value = [
            Model(full_model_name="bedrock:arn1", provider="bedrock", model="arn1", display_name="Model 1"),
            Model(full_model_name="bedrock:arn2", provider="bedrock", model="arn2", display_name="Model 2")
        ]
        
        result = get_models_list(provider="bedrock")
        
        assert len(result) == 2
        assert all(model.provider == "bedrock" for model in result)
        mock_bedrock.assert_called_once()


def test_get_models_list_invalid_provider():
    """Test that get_models_list returns empty list for invalid provider."""
    result = get_models_list(provider="invalid_provider")
    
    assert result == []
    assert isinstance(result, list)


def test_get_models_list_empty_responses():
    """Test that get_models_list handles empty responses from providers."""
    with patch('promptbuilder.llm_client.google_client.GoogleLLMClient.models_list') as mock_google, \
         patch('promptbuilder.llm_client.anthropic_client.AnthropicLLMClient.models_list') as mock_anthropic, \
         patch('promptbuilder.llm_client.openai_client.OpenaiLLMClient.models_list') as mock_openai, \
         patch('promptbuilder.llm_client.bedrock_client.BedrockLLMClient.models_list') as mock_bedrock:
        
        # All providers return empty lists
        mock_google.return_value = []
        mock_anthropic.return_value = []
        mock_openai.return_value = []
        mock_bedrock.return_value = []
        
        result = get_models_list()
        
        assert result == []
        assert isinstance(result, list)


def test_model_structure():
    """Test that Model objects have the expected structure."""
    with patch('promptbuilder.llm_client.google_client.GoogleLLMClient.models_list') as mock_google:
        mock_google.return_value = [
            Model(
                full_model_name="google:gemini-1.5-flash", 
                provider="google", 
                model="gemini-1.5-flash", 
                display_name="Gemini 1.5 Flash"
            )
        ]
        
        result = get_models_list(provider="google")
        
        assert len(result) == 1
        model = result[0]
        
        # Check all fields exist
        assert hasattr(model, 'full_model_name')
        assert hasattr(model, 'provider')
        assert hasattr(model, 'model')
        assert hasattr(model, 'display_name')
        
        # Check field values
        assert model.full_model_name == "google:gemini-1.5-flash"
        assert model.provider == "google"
        assert model.model == "gemini-1.5-flash"
        assert model.display_name == "Gemini 1.5 Flash"


def test_model_without_display_name():
    """Test that Model objects can be created without display_name (optional field)."""
    with patch('promptbuilder.llm_client.openai_client.OpenaiLLMClient.models_list') as mock_openai:
        mock_openai.return_value = [
            Model(
                full_model_name="openai:gpt-4", 
                provider="openai", 
                model="gpt-4"
            )
        ]
        
        result = get_models_list(provider="openai")
        
        assert len(result) == 1
        model = result[0]
        
        assert model.full_model_name == "openai:gpt-4"
        assert model.provider == "openai"
        assert model.model == "gpt-4"
        assert model.display_name is None
