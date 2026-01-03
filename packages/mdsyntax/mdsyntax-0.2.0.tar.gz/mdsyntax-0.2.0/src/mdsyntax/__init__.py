"""
mdsyntax: Render markdown with syntax highlighting in the terminal.

Usage:
    >>> from mdsyntax import md_print, md_render
    >>> md_print("# Hello **world**")
    >>> output = md_render("Some `code` here")

    # Styling API
    >>> from mdsyntax import Style, style
    >>> print(Style.bold_text("important"))
    >>> print(style("hello").italic().fg("red"))
"""

from mdsyntax.renderer import (
    LANG_ALIASES,
    Ansi,
    MarkdownRenderer,
    Style,
    SyntaxHighlighter,
    md_print,
    md_render,
    style,
)

__version__ = "0.2.0"
__all__ = [
    "md_print",
    "md_render",
    "MarkdownRenderer",
    "SyntaxHighlighter",
    "LANG_ALIASES",
    "Style",
    "style",
    "Ansi",
    "__version__",
]
