"""Unit tests for Fonts."""

import pytest
import responses
from indox_client import Indox


class TestFonts:
    """Test Fonts methods."""

    @responses.activate
    def test_supported_formats(self):
        responses.add(
            responses.GET,
            "https://indox.org/docs/api/v1/fonts/formats/",
            json={
                "service": "fonts",
                "engines": {
                    "fonttools": {
                        "group": "font",
                        "credits": 1,
                        "inputs": ["ttf", "otf", "woff", "woff2"],
                        "outputs": ["ttf", "otf", "woff", "woff2"]
                    }
                },
                "total_formats": 4,
                "total_routes": 8
            },
            status=200,
        )
        client = IndoxClient(api_key="test-key")
        result = client.docs.supported_formats()
        assert result["service"] == "fonts"
        assert "fonttools" in result["engines"]

    @responses.activate
    def test_get_format_outputs(self):
        responses.add(
            responses.GET,
            "https://indox.org/docs/api/v1/fonts/formats/ttf/",
            json={
                "input": "ttf",
                "outputs": [
                    {"output": "otf", "engine": "fonttools", "credits": 1},
                    {"output": "woff", "engine": "fonttools", "credits": 1}
                ],
                "count": 2
            },
            status=200,
        )
        client = IndoxClient(api_key="test-key")
        result = client.docs.get_format_outputs("ttf")
        assert result["input"] == "ttf"
        assert result["count"] == 2
        assert len(result["outputs"]) == 2

    @responses.activate
    def test_upload(self):
        responses.add(
            responses.POST,
            "https://indox.org/docs/api/v1/fonts/upload/",
            json={
                "success": True,
                "s3_key": "test-key",
                "filename": "test.ttf",
                "format": "ttf",
                "size_bytes": 1234
            },
            status=200,
        )
        client = IndoxClient(api_key="test-key")

        # Create a dummy file for testing
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as f:
            f.write(b'\x00\x01\x00\x00' + b'\x00' * 100)
            temp_file = f.name

        try:
            result = client.docs.upload(file_path=temp_file)
            assert result["success"] is True
            assert result["s3_key"] == "test-key"
        finally:
            os.unlink(temp_file)

    @responses.activate
    def test_convert(self):
        responses.add(
            responses.POST,
            "https://indox.org/docs/api/v1/fonts/convert/",
            json={
                "id": "conv-123",
                "status": "pending",
                "download_url": "https://example.com/download"
            },
            status=200,
        )
        client = IndoxClient(api_key="test-key")
        result = client.docs.convert(
            s3_key="test-s3-key",
            target_format="otf"
        )
        assert result["id"] == "conv-123"
        assert result["status"] == "pending"

    @responses.activate
    def test_validate(self):
        responses.add(
            responses.POST,
            "https://indox.org/docs/api/v1/fonts/validate/",
            json={
                "valid": True,
                "input": "ttf",
                "output": "otf",
                "engine": "fonttools",
                "credits": 1
            },
            status=200,
        )
        client = IndoxClient(api_key="test-key")

        # Create a dummy file for testing
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as f:
            f.write(b'\x00\x01\x00\x00' + b'\x00' * 100)
            temp_file = f.name

        try:
            result = client.docs.validate(file_path=temp_file, target_format="otf")
            assert result["valid"] is True
            assert result["input"] == "ttf"
            assert result["output"] == "otf"
        finally:
            os.unlink(temp_file)

    @responses.activate
    def test_get_conversion(self):
        responses.add(
            responses.GET,
            "https://indox.org/docs/api/v1/fonts/conversion/conv-123/",
            json={
                "id": "conv-123",
                "status": "completed",
                "success": True,
                "download_url": "https://example.com/download",
                "engine_used": "fonttools"
            },
            status=200,
        )
        client = IndoxClient(api_key="test-key")
        result = client.docs.get_conversion("conv-123")
        assert result["id"] == "conv-123"
        assert result["status"] == "completed"
        assert result["success"] is True