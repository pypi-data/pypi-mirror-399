def convert_http_header_to_django(header: str) -> str:
    uppercase_header = header.upper().replace("-", "_")

    if uppercase_header.startswith("X"):
        return f"HTTP_{uppercase_header}"

    return uppercase_header
