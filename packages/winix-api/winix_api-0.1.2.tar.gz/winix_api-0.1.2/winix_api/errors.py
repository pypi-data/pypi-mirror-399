RESPONSE_ERRORS = {
    "no data": {"x": True, "display_name": "no data (invalid or unregistered device?)"},
    "parameter(s) not valid : device id": {"x": True},
    "device not registered": {"x": True},
    "device not connected": {"x": True},
}


def is_response_error(possible_error: str) -> bool:
    return possible_error in RESPONSE_ERRORS


def get_error_message(possible_error: str) -> str:
    error = RESPONSE_ERRORS.get(possible_error)
    if not error or not error.get("display_name"):
        return possible_error
    return error["display_name"]
