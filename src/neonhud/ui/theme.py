from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    primary: str
    accent: str
    warning: str
    background: str


# Default themes
CLASSIC = Theme(
    name="classic",
    primary="bold white",
    accent="green",
    warning="yellow",
    background="black",
)

CYBERPUNK = Theme(
    name="cyberpunk",
    primary="bold magenta",
    accent="cyan",
    warning="yellow",
    background="black",
)

# Registry
THEMES = {
    "classic": CLASSIC,
    "cyberpunk": CYBERPUNK,
}


def get_theme(name: str) -> Theme:
    """Fetch a theme by name, defaulting to classic."""
    return THEMES.get(name.lower(), CLASSIC)
