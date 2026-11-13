from unittest.mock import MagicMock, patch
import base64
from app.video_tools import generate_exercise_video


@patch("app.video_tools.storage.Client")
@patch("app.video_tools.genai.Client")
def test_generate_exercise_video(mock_genai_client_cls, mock_storage_client_cls):
    mock_genai_client = MagicMock()
    mock_genai_client_cls.return_value = mock_genai_client

    mock_interaction = MagicMock()
    mock_video_content = MagicMock()
    mock_video_content.mime_type = "video/mp4"
    mock_video_content.data = base64.b64encode(b"fake-mp4-video-bytes").decode("utf-8")
    mock_interaction.output_video = mock_video_content

    mock_genai_client.interactions.create.return_value = mock_interaction

    mock_storage_client = MagicMock()
    mock_storage_client_cls.return_value = mock_storage_client
    mock_bucket = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_tool_context = MagicMock()

    res = generate_exercise_video("A short kettlebell swing demo", tool_context=mock_tool_context)

    assert res["status"] == "success"
    assert "https://storage.googleapis.com/fitpulse-coach-media-qwiklabs-gcp-04-ec0b87ee001f/" in res["public_url"]
    assert res["mime_type"] == "video/mp4"
    assert mock_tool_context.save_artifact.called
    assert mock_blob.upload_from_string.called
