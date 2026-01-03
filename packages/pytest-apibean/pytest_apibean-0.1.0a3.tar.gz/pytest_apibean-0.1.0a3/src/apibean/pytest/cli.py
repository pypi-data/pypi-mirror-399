from typing import Iterable, Optional


def render(
    *,
    title: str,
    lines: Iterable[str],
    footer: Optional[str] = None,
    width: int = 79,
):
    """
    Render a unified CLI output block for pytest-apibean commands.

    This function is intentionally implemented using plain stdout printing
    to ensure it works reliably during early pytest lifecycle phases
    (e.g. pytest_cmdline_main), without depending on terminal plugins.

    Args:
        title: Section title displayed at the top.
        lines: Iterable of content lines to display.
        footer: Optional footer line displayed at the bottom.
        width: Total width of the rendered separator line.
    """

    sep = "=" * width

    print()
    print(sep)
    print(f"{title}".center(width))
    print(sep)
    print()

    for line in lines:
        print(line)

    if footer:
        print()
        print(footer)

    print()


def render_kv(
    *,
    title: str,
    items: dict,
    footer: Optional[str] = None,
):
    lines = [f"{k}: {v}" for k, v in items.items()]
    render(title=title, lines=lines, footer=footer)


def row(icon: str, label: str, value: str = "") -> str:
    return f"{icon} {label:<18} {value}"
