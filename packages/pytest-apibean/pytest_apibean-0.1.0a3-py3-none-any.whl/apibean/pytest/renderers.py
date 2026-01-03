

def render_docstring(
    text: str,
    *,
    indent: int = 1,
) -> list[str]:
    """
    Render docstring as-is, preserving line breaks and formatting,
    only applying a uniform left indentation.
    """
    if not text:
        return []

    prefix = " " * indent

    lines: list[str] = []
    for line in text.strip("\n").splitlines():
        if line.strip() == "":
            lines.append("")   # preserve blank lines
        else:
            lines.append(f"{prefix}{line.rstrip()}")

    return lines
