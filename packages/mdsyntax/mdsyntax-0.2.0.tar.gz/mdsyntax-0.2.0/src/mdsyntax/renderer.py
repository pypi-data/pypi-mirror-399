"""
Terminal markdown renderer with syntax highlighting.
"""

from __future__ import annotations

import os
import re
import shutil
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Literal

from colorama import just_fix_windows_console
from pygments import highlight
from pygments.formatters import Terminal256Formatter, TerminalTrueColorFormatter
from pygments.lexers import TextLexer, get_lexer_by_name, guess_lexer
from pygments.styles import get_all_styles, get_style_by_name

just_fix_windows_console()


class Ansi:
    """ANSI escape codes not exposed by colorama."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    BOLD_OFF = "\033[22m"
    DIM = "\033[2m"
    DIM_OFF = "\033[22m"
    ITALIC = "\033[3m"
    ITALIC_OFF = "\033[23m"
    UNDERLINE = "\033[4m"
    UNDERLINE_OFF = "\033[24m"
    STRIKETHROUGH = "\033[9m"
    STRIKETHROUGH_OFF = "\033[29m"

    # Foreground colors
    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_WHITE = "\033[37m"
    FG_DEFAULT = "\033[39m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_DEFAULT = "\033[49m"

    @staticmethod
    def rgb_fg(r: int, g: int, b: int) -> str:
        """24-bit foreground color."""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def rgb_bg(r: int, g: int, b: int) -> str:
        """24-bit background color."""
        return f"\033[48;2;{r};{g};{b}m"


# Color name mapping
_COLOR_MAP: dict[str, str] = {
    "black": Ansi.FG_BLACK,
    "red": Ansi.FG_RED,
    "green": Ansi.FG_GREEN,
    "yellow": Ansi.FG_YELLOW,
    "blue": Ansi.FG_BLUE,
    "magenta": Ansi.FG_MAGENTA,
    "cyan": Ansi.FG_CYAN,
    "white": Ansi.FG_WHITE,
}

_BG_COLOR_MAP: dict[str, str] = {
    "black": Ansi.BG_BLACK,
    "red": Ansi.BG_RED,
    "green": Ansi.BG_GREEN,
    "yellow": Ansi.BG_YELLOW,
    "blue": Ansi.BG_BLUE,
    "magenta": Ansi.BG_MAGENTA,
    "cyan": Ansi.BG_CYAN,
    "white": Ansi.BG_WHITE,
}

ColorName = Literal[
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"
]


# =============================================================================
# Styling API
# =============================================================================


class Style:
    """
    Fluent API for styling terminal text.

    Usage:
        from mdsyntax import Style

        # Direct methods
        print(Style.bold("important"))
        print(Style.italic("emphasis"))
        print(Style.color("warning", fg="red"))

        # Chainable
        s = Style("hello")
        print(s.bold().italic())
        print(s.fg("red").bg("white").underline())

        # Combine styles
        print(Style.bold(Style.italic("both")))
    """

    def __init__(self, text: str = ""):
        self._text = text
        self._codes: list[str] = []
        self._reset_codes: list[str] = []

    def __str__(self) -> str:
        if not self._codes:
            return self._text
        prefix = "".join(self._codes)
        suffix = "".join(reversed(self._reset_codes))
        return f"{prefix}{self._text}{suffix}"

    def __repr__(self) -> str:
        return f"Style({self._text!r})"

    def _add(self, on: str, off: str) -> Style:
        """Add a style code pair."""
        new = Style(self._text)
        new._codes = self._codes + [on]
        new._reset_codes = self._reset_codes + [off]
        return new

    # Style methods
    def bold(self) -> Style:
        return self._add(Ansi.BOLD, Ansi.BOLD_OFF)

    def dim(self) -> Style:
        return self._add(Ansi.DIM, Ansi.DIM_OFF)

    def italic(self) -> Style:
        return self._add(Ansi.ITALIC, Ansi.ITALIC_OFF)

    def underline(self) -> Style:
        return self._add(Ansi.UNDERLINE, Ansi.UNDERLINE_OFF)

    def strikethrough(self) -> Style:
        return self._add(Ansi.STRIKETHROUGH, Ansi.STRIKETHROUGH_OFF)

    def fg(self, color: ColorName | tuple[int, int, int]) -> Style:
        """Set foreground color by name or RGB tuple."""
        if isinstance(color, tuple):
            code = Ansi.rgb_fg(*color)
        else:
            code = _COLOR_MAP.get(color, Ansi.FG_DEFAULT)
        return self._add(code, Ansi.FG_DEFAULT)

    def bg(self, color: ColorName | tuple[int, int, int]) -> Style:
        """Set background color by name or RGB tuple."""
        if isinstance(color, tuple):
            code = Ansi.rgb_bg(*color)
        else:
            code = _BG_COLOR_MAP.get(color, Ansi.BG_DEFAULT)
        return self._add(code, Ansi.BG_DEFAULT)

    # Static convenience methods
    @staticmethod
    def bold_text(text: str) -> str:
        return f"{Ansi.BOLD}{text}{Ansi.BOLD_OFF}"

    @staticmethod
    def dim_text(text: str) -> str:
        return f"{Ansi.DIM}{text}{Ansi.DIM_OFF}"

    @staticmethod
    def italic_text(text: str) -> str:
        return f"{Ansi.ITALIC}{text}{Ansi.ITALIC_OFF}"

    @staticmethod
    def underline_text(text: str) -> str:
        return f"{Ansi.UNDERLINE}{text}{Ansi.UNDERLINE_OFF}"

    @staticmethod
    def strike_text(text: str) -> str:
        return f"{Ansi.STRIKETHROUGH}{text}{Ansi.STRIKETHROUGH_OFF}"

    @staticmethod
    def color(
        text: str,
        fg: ColorName | tuple[int, int, int] | None = None,
        bg: ColorName | tuple[int, int, int] | None = None,
    ) -> str:
        """Apply foreground and/or background color."""
        prefix = ""
        suffix = ""

        if fg is not None:
            if isinstance(fg, tuple):
                prefix += Ansi.rgb_fg(*fg)
            else:
                prefix += _COLOR_MAP.get(fg, "")
            suffix = Ansi.FG_DEFAULT + suffix

        if bg is not None:
            if isinstance(bg, tuple):
                prefix += Ansi.rgb_bg(*bg)
            else:
                prefix += _BG_COLOR_MAP.get(bg, "")
            suffix = Ansi.BG_DEFAULT + suffix

        return f"{prefix}{text}{suffix}"


# Convenience function
def style(text: str = "") -> Style:
    """Create a Style object for fluent chaining."""
    return Style(text)


# =============================================================================
# Syntax Highlighting
# =============================================================================


LANG_ALIASES: dict[str, str] = {
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "sh": "bash",
    "shell": "bash",
    "yml": "yaml",
    "md": "markdown",
    "c++": "cpp",
    "c#": "csharp",
}


def _detect_true_color() -> bool:
    """Check if terminal supports 24-bit color."""
    colorterm = os.environ.get("COLORTERM", "")
    return colorterm in ("truecolor", "24bit")


def _get_style_bg(style_name: str) -> str:
    """Extract background color from pygments style as ANSI escape."""
    try:
        style = get_style_by_name(style_name)
        bg = style.background_color
        if bg and bg.startswith("#") and len(bg) == 7:
            r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
            return f"\033[48;2;{r};{g};{b}m"
    except Exception:
        pass
    return "\033[48;5;236m"  # fallback gray


def _visible_len(s: str) -> int:
    """Length of string excluding ANSI escape sequences."""
    return len(re.sub(r"\033\[[0-9;]*m", "", s))


def _truncate_to_width(text: str, width: int, indicator: str = "…") -> str:
    """Truncate string to visible width, accounting for ANSI codes."""
    if _visible_len(text) <= width:
        return text

    # We need to truncate while preserving ANSI codes
    result = []
    visible_count = 0
    target = width - len(indicator)
    i = 0

    while i < len(text) and visible_count < target:
        if text[i] == "\033":
            # Capture entire ANSI sequence
            end = text.find("m", i)
            if end != -1:
                result.append(text[i : end + 1])
                i = end + 1
                continue
        result.append(text[i])
        visible_count += 1
        i += 1

    return "".join(result) + indicator


def _pad_to_width(text: str, width: int) -> str:
    """Pad string to width, accounting for ANSI codes."""
    padding = width - _visible_len(text)
    return text + " " * max(0, padding)


def _fit_to_width(text: str, width: int) -> str:
    """Truncate if too long, then pad to exact width."""
    truncated = _truncate_to_width(text, width)
    return _pad_to_width(truncated, width)


def _max_visible_width(lines: list[str]) -> int:
    """Get the maximum visible width across all lines."""
    if not lines:
        return 0
    return max(_visible_len(line) for line in lines)


class SyntaxHighlighter:
    """Syntax highlighter using pygments."""

    def __init__(self, style: str = "monokai", true_color: bool | None = None):
        """
        Args:
            style: Pygments style name (monokai, dracula, gruvbox-dark, one-dark, etc.)
            true_color: Use 24-bit color. None = auto-detect from COLORTERM env var.
        """
        if true_color is None:
            true_color = _detect_true_color()

        formatter_cls = (
            TerminalTrueColorFormatter if true_color else Terminal256Formatter
        )
        self.formatter = formatter_cls(style=style)
        self.style = style

    def highlight(self, code: str, language: str = "") -> str:
        """Highlight code and return ANSI-formatted string."""
        lexer = self._get_lexer(code, language)
        return highlight(code, lexer, self.formatter).rstrip("\n")

    def _get_lexer(self, code: str, language: str):
        language = LANG_ALIASES.get(language.lower(), language.lower())

        if language:
            try:
                return get_lexer_by_name(language)
            except Exception:
                pass

        try:
            return guess_lexer(code)
        except Exception:
            return TextLexer()

    @staticmethod
    def available_styles() -> list[str]:
        """Return list of available pygments style names."""
        return list(get_all_styles())


# =============================================================================
# Markdown Rendering
# =============================================================================


@dataclass
class MarkdownRenderer:
    """Renders markdown to ANSI-formatted terminal output."""

    code_style: str = "monokai"
    code_width: int | None = None  # None = terminal width
    true_color: bool | None = None  # None = auto-detect

    _highlighter: SyntaxHighlighter = field(init=False, repr=False)
    _code_bg: str = field(init=False, repr=False)

    def __post_init__(self):
        self._highlighter = SyntaxHighlighter(
            style=self.code_style, true_color=self.true_color
        )
        self._code_bg = _get_style_bg(self.code_style)

    def render(self, text: str) -> str:
        """Render markdown text to ANSI-formatted string."""
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return "\n".join(self._render_blocks(text))

    def _render_blocks(self, text: str) -> Iterator[str]:
        """Process block-level elements."""
        lines = text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Code block
            if stripped.startswith("```"):
                lang = stripped[3:].strip()
                code_lines = []
                i += 1

                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1

                yield from self._render_code_block(code_lines, lang)
                i += 1  # skip closing ```
                continue

            yield self._render_line(line)
            i += 1

    def _get_code_width(self) -> int:
        if self.code_width:
            return self.code_width
        return shutil.get_terminal_size().columns

    def _render_code_block(self, code_lines: list[str], language: str) -> Iterator[str]:
        """Render a fenced code block with syntax highlighting."""
        bg = self._code_bg
        reset = Ansi.RESET

        # Highlight code first to measure actual output width
        highlighted_lines: list[str] = []
        if code_lines:
            code = "\n".join(code_lines)
            highlighted = self._highlighter.highlight(code, language)
            highlighted_lines = highlighted.split("\n")

        # Calculate width: use the largest of terminal width, specified width, or content width
        terminal_width = shutil.get_terminal_size().columns
        content_width = (
            _max_visible_width(highlighted_lines) if highlighted_lines else 0
        )
        label = f" {language}" if language else ""
        label_width = len(label)

        if self.code_width:
            # User specified a width - use it as minimum, but expand if content is wider
            width = max(self.code_width, content_width, label_width)
        else:
            # No specified width - use terminal width, but expand if content is wider
            width = max(terminal_width, content_width, label_width)

        # Header with language label
        yield f"{bg}{Ansi.FG_WHITE}{Ansi.DIM}{_pad_to_width(label, width)}{reset}"

        # Highlighted code
        for hl_line in highlighted_lines:
            yield f"{bg}{_pad_to_width(hl_line, width)}{reset}"

        # Footer line for visual separation
        yield f"{bg}{' ' * width}{reset}"

    def _render_line(self, line: str) -> str:
        """Render a single line of markdown."""
        stripped = line.strip()

        if not stripped:
            return ""

        # Horizontal rule
        if re.match(r"^[-*_]{3,}$", stripped):
            return f"{Ansi.DIM}{Ansi.FG_WHITE}{'─' * 50}{Ansi.RESET}"

        # Headers
        if m := re.match(r"^(#{1,6})\s+(.+)$", stripped):
            return self._render_header(len(m.group(1)), m.group(2))

        # Blockquotes
        if stripped.startswith(">"):
            content = stripped.lstrip(">").strip()
            rendered = self._render_inline(content, parent_styles=[Ansi.ITALIC])
            grey = Ansi.rgb_fg(180, 180, 180)
            return f"{grey}│ {Ansi.ITALIC}{rendered}{Ansi.ITALIC_OFF}{Ansi.RESET}"

        # Task lists
        if m := re.match(r"^[-*]\s+\[([ xX])\]\s+(.+)$", stripped):
            checked = m.group(1).lower() == "x"
            marker = f"{Ansi.FG_GREEN}✓" if checked else f"{Ansi.FG_RED}○"
            return f"  {marker} {self._render_inline(m.group(2))}{Ansi.RESET}"

        # Unordered lists
        if m := re.match(r"^[-*+]\s+(.+)$", stripped):
            indent = len(line) - len(line.lstrip())
            return f"{' ' * indent}{Ansi.FG_GREEN}• {Ansi.FG_DEFAULT}{self._render_inline(m.group(1))}"

        # Ordered lists
        if m := re.match(r"^(\d+)\.\s+(.+)$", stripped):
            indent = len(line) - len(line.lstrip())
            return f"{' ' * indent}{Ansi.FG_GREEN}{m.group(1)}. {Ansi.FG_DEFAULT}{self._render_inline(m.group(2))}"

        return self._render_inline(line)

    def _render_header(self, level: int, text: str) -> str:
        """Render a header with level-appropriate styling."""
        colors = [
            Ansi.FG_CYAN,
            Ansi.FG_BLUE,
            Ansi.FG_MAGENTA,
            Ansi.FG_GREEN,
            Ansi.FG_YELLOW,
            Ansi.FG_WHITE,
        ]
        color = colors[min(level, 6) - 1]

        # Visual prefix for h1-h3
        prefix = "█" * (4 - level) + " " if level <= 3 else ""

        rendered_text = self._render_inline(text)
        return f"{color}{Ansi.BOLD}{prefix}{rendered_text}{Ansi.RESET}"

    def _render_inline(self, text: str, parent_styles: list[str] | None = None) -> str:
        """Render inline markdown elements."""
        parent_styles = parent_styles or []
        restore = "".join(parent_styles)

        # Order matters: process from most specific to least specific

        # Inline code first (protects contents from further processing)
        code_spans: list[str] = []

        def extract_code(m):
            # Use targeted reset: just reset bg/fg, then restore parent styles
            code_content = f"{Ansi.BG_BLACK}{Ansi.FG_YELLOW} {m.group(1)} {Ansi.BG_DEFAULT}{Ansi.FG_DEFAULT}{restore}"
            code_spans.append(code_content)
            return f"\x00CODE{len(code_spans) - 1}\x00"

        text = re.sub(r"`([^`]+)`", extract_code, text)

        # Bold + italic (must come before bold and italic)
        text = re.sub(
            r"\*\*\*(.+?)\*\*\*",
            lambda m: f"{Ansi.BOLD}{Ansi.ITALIC}{m.group(1)}{Ansi.ITALIC_OFF}{Ansi.BOLD_OFF}",
            text,
        )

        # Bold
        text = re.sub(
            r"\*\*(.+?)\*\*",
            lambda m: f"{Ansi.BOLD}{m.group(1)}{Ansi.BOLD_OFF}",
            text,
        )
        text = re.sub(
            r"__(.+?)__",
            lambda m: f"{Ansi.BOLD}{m.group(1)}{Ansi.BOLD_OFF}",
            text,
        )

        # Italic with asterisks (works anywhere)
        text = re.sub(
            r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
            lambda m: f"{Ansi.ITALIC}{m.group(1)}{Ansi.ITALIC_OFF}",
            text,
        )

        # Italic with underscores (only at word boundaries)
        text = re.sub(
            r"(?<!\w)_(?!_)(.+?)(?<!_)_(?!\w)",
            lambda m: f"{Ansi.ITALIC}{m.group(1)}{Ansi.ITALIC_OFF}",
            text,
        )

        # Strikethrough
        text = re.sub(
            r"~~(.+?)~~",
            lambda m: f"{Ansi.STRIKETHROUGH}{m.group(1)}{Ansi.STRIKETHROUGH_OFF}",
            text,
        )

        # Links - use targeted resets
        text = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda m: f"{Ansi.UNDERLINE}{Ansi.FG_BLUE}{m.group(1)}{Ansi.UNDERLINE_OFF}{Ansi.FG_DEFAULT}{Ansi.DIM} ({m.group(2)}){Ansi.DIM_OFF}{restore}",
            text,
        )

        # Restore code spans
        for i, code in enumerate(code_spans):
            text = text.replace(f"\x00CODE{i}\x00", code)

        return text


def md_print(
    text: str,
    *,
    code_style: str = "monokai",
    code_width: int | None = None,
    true_color: bool | None = None,
) -> None:
    """
    Print markdown-formatted text to the terminal.

    Args:
        text: Markdown text to render.
        code_style: Pygments style for code blocks.
        code_width: Width for code blocks (None = terminal width).
        true_color: Use 24-bit color (None = auto-detect).
    """
    renderer = MarkdownRenderer(
        code_style=code_style,
        code_width=code_width,
        true_color=true_color,
    )
    print(renderer.render(text))


def md_render(
    text: str,
    *,
    code_style: str = "monokai",
    code_width: int | None = None,
    true_color: bool | None = None,
) -> str:
    """
    Render markdown text to ANSI-formatted string.

    Args:
        text: Markdown text to render.
        code_style: Pygments style for code blocks.
        code_width: Width for code blocks (None = terminal width).
        true_color: Use 24-bit color (None = auto-detect).

    Returns:
        ANSI-formatted string ready for terminal output.
    """
    renderer = MarkdownRenderer(
        code_style=code_style,
        code_width=code_width,
        true_color=true_color,
    )
    return renderer.render(text)
