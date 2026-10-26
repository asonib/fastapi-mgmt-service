"""Tests for the Summary Service logic and OpenAI client integration."""

import pytest
from unittest import mock
from app.exception.handlers import AppException
from app.service.summary_service import generate_llm_summary


def _make_app_exception(status_code: int, message: str = "Error") -> AppException:
    """Instantiate AppException safely without relying on keyword argument names."""
    try:
        return AppException(status_code, message)
    except TypeError:
        exc = AppException.__new__(AppException)
        exc.status_code = status_code
        return exc


@pytest.mark.asyncio
@mock.patch("app.service.summary_service.openai.OpenAI")
@mock.patch("app.service.summary_service.get_openai_client_configs")
@mock.patch("app.service.summary_service.validate_summary_payload")
async def test_generate_llm_summary_success(
    mock_validate, mock_get_configs, mock_openai
):
    """Test summary service successfully generates and strips LLM summary."""
    input_text = "Sample long text to be summarized."
    mock_get_configs.return_value = {
        "api_key": "fake-openai-key",
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": input_text}],
    }

    mock_choice = mock.MagicMock()
    mock_choice.message.content = "  Concise summary output.  "
    mock_response = mock.MagicMock()
    mock_response.choices = [mock_choice]

    mock_client_instance = mock.MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client_instance

    result = await generate_llm_summary(input_text)

    mock_validate.assert_called_once_with(input_text)
    mock_get_configs.assert_called_once_with(input_text)
    mock_openai.assert_called_once_with(api_key="fake-openai-key")
    mock_client_instance.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": input_text}],
    )
    assert result == "Concise summary output."


@pytest.mark.asyncio
@mock.patch("app.service.summary_service.openai.OpenAI")
@mock.patch("app.service.summary_service.get_openai_client_configs")
@mock.patch("app.service.summary_service.validate_summary_payload")
async def test_generate_llm_summary_with_custom_base_url(
    mock_validate, mock_get_configs, mock_openai
):
    """Test summary service passes base_url to OpenAI client when present in config."""
    input_text = "Sample text for custom endpoint."
    mock_get_configs.return_value = {
        "api_key": "fake-key",
        "base_url": "https://custom.llm.provider/v1",
        "model": "custom-model",
        "messages": [{"role": "user", "content": input_text}],
    }

    mock_choice = mock.MagicMock()
    mock_choice.message.content = "Custom endpoint summary."
    mock_response = mock.MagicMock()
    mock_response.choices = [mock_choice]

    mock_client_instance = mock.MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client_instance

    result = await generate_llm_summary(input_text)

    mock_openai.assert_called_once_with(
        api_key="fake-key",
        base_url="https://custom.llm.provider/v1",
    )
    assert result == "Custom endpoint summary."


@pytest.mark.asyncio
@mock.patch("app.service.summary_service.get_openai_client_configs")
@mock.patch("app.service.summary_service.validate_summary_payload")
async def test_generate_llm_summary_validation_error(
    mock_validate, mock_get_configs
):
    """Test summary service aborts immediately if payload validation fails."""
    mock_validate.side_effect = _make_app_exception(400, "Empty text")

    with pytest.raises(AppException) as exc_info:
        await generate_llm_summary("")

    assert exc_info.value.status_code == 400
    mock_get_configs.assert_not_called()


@pytest.mark.asyncio
@mock.patch("app.service.summary_service.handle_summary_provider_error")
@mock.patch("app.service.summary_service.settings")
@mock.patch("app.service.summary_service.openai.OpenAI")
@mock.patch("app.service.summary_service.get_openai_client_configs")
@mock.patch("app.service.summary_service.validate_summary_payload")
async def test_generate_llm_summary_fallback_when_no_api_key(
    mock_validate,
    mock_get_configs,
    mock_openai,
    mock_settings,
    mock_handle_error,
):
    """Test summary service returns mock fallback string on error when API key is unset."""
    input_text = "A" * 150
    mock_settings.OPENAI_API_KEY = ""
    mock_get_configs.return_value = {
        "api_key": "",
        "model": "gpt-4o-mini",
        "messages": [],
    }
    mock_openai.side_effect = Exception("OpenAI client initialization error")

    result = await generate_llm_summary(input_text)

    assert result == f"[Mock Summary Provider]: {'A' * 100}..."
    mock_handle_error.assert_not_called()


@pytest.mark.asyncio
@mock.patch("app.service.summary_service.handle_summary_provider_error")
@mock.patch("app.service.summary_service.settings")
@mock.patch("app.service.summary_service.openai.OpenAI")
@mock.patch("app.service.summary_service.get_openai_client_configs")
@mock.patch("app.service.summary_service.validate_summary_payload")
async def test_generate_llm_summary_provider_error_delegation(
    mock_validate,
    mock_get_configs,
    mock_openai,
    mock_settings,
    mock_handle_error,
):
    """Test summary service delegates upstream exceptions when API key is configured."""
    input_text = "Valid input text."
    mock_settings.OPENAI_API_KEY = "valid-api-key"
    mock_get_configs.return_value = {
        "api_key": "valid-api-key",
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": input_text}],
    }

    api_error = RuntimeError("Upstream rate limit exceeded")
    mock_client_instance = mock.MagicMock()
    mock_client_instance.chat.completions.create.side_effect = api_error
    mock_openai.return_value = mock_client_instance

    mock_handle_error.side_effect = _make_app_exception(502, "LLM Provider Error")

    with pytest.raises(AppException) as exc_info:
        await generate_llm_summary(input_text)

    assert exc_info.value.status_code == 502
    mock_handle_error.assert_called_once_with(api_error)