# core/renderers.py

from rest_framework.renderers import JSONRenderer
from rest_framework import status
from http import HTTPStatus

class CoreRenderer(JSONRenderer):
    """
    A clean, consistent JSON renderer for DRF APIs.

    Response shape:
    {
        "success": true/false,
        "status_code": 200,
        "version": "1.0.0",
        "message": "OK" | "User not found" | ...,
        "data": {...} | null,
        "error": {...} | null
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')
        request = renderer_context.get('request')

        status_code = getattr(response, 'status_code', 200)
        is_success = status.is_success(status_code)
        try:
            description = HTTPStatus(status_code).phrase
        except ValueError:
            description = 'Error'

        # Default structure
        response_data = {
            "success": is_success,
            "status_code": status_code,
            "version": "1.0.0",
            "message": description,
            "data": None,
            "error": None,
        }

        if is_success:
            response_data["data"] = data
        else:
            # Try to extract a human-friendly message or fallback
            if isinstance(data, dict):
                detail = data.get('detail')
                response_data["message"] = detail or description
            response_data["error"] = data

        return super().render(response_data, accepted_media_type, renderer_context)
