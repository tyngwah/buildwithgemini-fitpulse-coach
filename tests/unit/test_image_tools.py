from unittest.mock import MagicMock, patch
from app.image_tools import generate_fitness_image


@patch("app.image_tools.storage.Client")
@patch("app.image_tools.genai.Client")
def test_generate_fitness_image(mock_genai_client_cls, mock_storage_client_cls):
    mock_genai_client = MagicMock()
    mock_genai_client_cls.return_value = mock_genai_client

    mock_part = MagicMock()
    mock_part.inline_data.data = b"fake-image-bytes"
    mock_part.inline_data.mime_type = "image/png"

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]
    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]
    mock_genai_client.models.generate_content.return_value = mock_response

    mock_storage_client = MagicMock()
    mock_storage_client_cls.return_value = mock_storage_client
    mock_bucket = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_tool_context = MagicMock()

    res = generate_fitness_image("Gold medal for running 10k", tool_context=mock_tool_context)

    assert res["status"] == "success"
    assert "https://storage.googleapis.com/fitpulse-coach-media-qwiklabs-gcp-04-ec0b87ee001f/" in res["public_url"]
    assert mock_tool_context.save_artifact.called
    assert mock_blob.upload_from_string.called
