import json
from xml.etree import ElementTree as ET

from ..exceptions import APIError
from ..models import ApiError, ApiErrors, SimpleError


def check_for_xml_errors(response_text: str | None) -> None:
    """Check if an XML response contains an error and raise APIError if found.

    This function checks for various error formats that the Commerce API might return:
    1. Simple error: <Error><Message>...</Message></Error>
    2. Single error with code: <error code="..."><message>...</message></error>
    3. Multiple errors: <errors><error>...</error></errors>
    4. Errors embedded in responses (e.g., in availability-query, productservice-response)

    Args:
        response_text: The XML response text from the API

    Raises:
        APIError: If an error is found in the response

    Note:
        Only call this function for XML responses. Check Content-Type header first.
    """
    if response_text is None or not response_text.strip():
        return

    try:
        # Parse the XML
        root = ET.fromstring(response_text)

        # Check for simple error format: <Error><Message>...</Message></Error>
        if root.tag == "Error":
            try:
                error_obj = SimpleError.from_xml(response_text)
                raise APIError(
                    message=error_obj.message,
                    response_text=response_text,
                )
            except Exception:
                # If parsing fails, raise a generic error
                message_elem = root.find("Message")
                if message_elem is not None and message_elem.text:
                    raise APIError(
                        message=message_elem.text,
                        response_text=response_text,
                    )

        # Check for multiple errors format: <errors><error>...</error></errors>
        elif root.tag == "errors":
            try:
                errors_obj = ApiErrors.from_xml(response_text)
                if errors_obj.errors:
                    # Raise first error found
                    first_error = errors_obj.errors[0]
                    raise APIError(
                        message=first_error.message.text,
                        code=first_error.code,
                        sku=first_error.message.sku,
                        response_text=response_text,
                    )
            except APIError:
                raise
            except Exception:
                pass

        # Check for single error element as root: <error code="..."><message>...</message></error>
        elif root.tag == "error":
            try:
                api_error = ApiError.from_xml(response_text)
                raise APIError(
                    message=api_error.message.text,
                    code=api_error.code,
                    sku=api_error.message.sku,
                    response_text=response_text,
                )
            except APIError:
                raise
            except Exception:
                pass

        # Check for errors embedded in other response types
        else:
            # Look for <error> child elements
            error_elem = root.find(".//error")
            if error_elem is not None:
                code = error_elem.get("code")
                message_elem = error_elem.find("message")
                if message_elem is not None:
                    message = message_elem.text or "Unknown error"
                    sku = message_elem.get("sku")
                    raise APIError(
                        message=message,
                        code=code,
                        sku=sku,
                        response_text=response_text,
                    )

    except APIError:
        # Re-raise Commerce API errors
        raise
    except ET.ParseError:
        # If XML parsing fails, it's not a valid XML response
        # Don't raise an error, let the caller handle it
        pass
    except Exception:
        # Catch any other exceptions during error checking
        # Don't let error checking itself cause failures
        pass


def check_for_json_errors(response_text: str | None) -> None:
    """Check if a JSON response contains an error and raise APIError if found.

    This function checks for error formats that the Catalog API might return:
    1. Simple format: {"errorCode":"403", "errorMessage":"..."}
    2. Nested format: {"error":{"code":404, "message":"...", "status":"..."}}

    Args:
        response_text: The JSON response text from the API

    Raises:
        APIError: If an error is found in the response

    Note:
        Only call this function for JSON responses. Check Content-Type header first.
    """
    if response_text is None or not response_text.strip():
        return

    try:
        data = json.loads(response_text)

        # Check for simple error format: {"errorCode":"403", "errorMessage":"..."}
        if "errorCode" in data and "errorMessage" in data:
            raise APIError(
                message=data["errorMessage"],
                code=str(data["errorCode"]),
                response_text=response_text,
            )

        # Check for nested error format: {"error":{"code":404, "message":"..."}}
        if "error" in data and isinstance(data["error"], dict):
            error = data["error"]
            message = error.get("message", "Unknown error")
            code = error.get("code")
            raise APIError(
                message=message,
                code=str(code) if code is not None else None,
                response_text=response_text,
            )

    except APIError:
        # Re-raise API errors
        raise
    except json.JSONDecodeError:
        # If JSON parsing fails, it's not a valid JSON response
        # Don't raise an error, let the caller handle it
        pass
    except Exception:
        # Catch any other exceptions during error checking
        # Don't let error checking itself cause failures
        pass
