from __future__ import annotations


def make_bar(
    percent: float, width: int = 20, fill_char: str = "█", empty_char: str = "░"
) -> str:
    """
    Return a simple text bar for percent [0,100].
    Example (width=10, 35%): '███░░░░░░'
    """
    if percent < 0.0:
        percent = 0.0
    if percent > 100.0:
        percent = 100.0

    filled = int(round((percent / 100.0) * width))
    empty = max(0, width - filled)
    return f"{fill_char * filled}{empty_char * empty}"
