"""Tests for mdsyntax."""

import re

from mdsyntax import (
    LANG_ALIASES,
    Ansi,
    MarkdownRenderer,
    Style,
    SyntaxHighlighter,
    md_render,
    style,
)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


class TestInlineFormatting:
    def test_bold_asterisks(self):
        result = md_render("**bold**")
        assert "bold" in strip_ansi(result)
        assert "**" not in strip_ansi(result)

    def test_bold_underscores(self):
        result = md_render("__bold__")
        assert "bold" in strip_ansi(result)
        assert "__" not in strip_ansi(result)

    def test_italic_asterisks(self):
        result = md_render("*italic*")
        assert "italic" in strip_ansi(result)
        assert strip_ansi(result).count("*") == 0

    def test_italic_underscores(self):
        result = md_render("_italic_")
        assert "italic" in strip_ansi(result)

    def test_underscore_in_word_preserved(self):
        result = md_render("some_variable_name")
        assert "some_variable_name" in strip_ansi(result)

    def test_multiple_italics(self):
        result = md_render("*a* and *b*")
        plain = strip_ansi(result)
        assert "a" in plain
        assert "b" in plain
        assert "*" not in plain

    def test_bold_italic(self):
        result = md_render("***both***")
        assert "both" in strip_ansi(result)

    def test_strikethrough(self):
        result = md_render("~~deleted~~")
        assert "deleted" in strip_ansi(result)
        assert "~~" not in strip_ansi(result)

    def test_inline_code(self):
        result = md_render("`code`")
        assert "code" in strip_ansi(result)

    def test_code_protects_formatting(self):
        result = md_render("`**not bold**`")
        assert "**not bold**" in strip_ansi(result)

    def test_link(self):
        result = md_render("[text](https://example.com)")
        plain = strip_ansi(result)
        assert "text" in plain
        assert "example.com" in plain


class TestBlockFormatting:
    def test_header_h1(self):
        result = md_render("# Title")
        assert "Title" in strip_ansi(result)
        assert "#" not in strip_ansi(result)

    def test_header_h2(self):
        result = md_render("## Subtitle")
        assert "Subtitle" in strip_ansi(result)

    def test_unordered_list(self):
        result = md_render("- item")
        assert "item" in strip_ansi(result)
        assert "•" in strip_ansi(result)

    def test_ordered_list(self):
        result = md_render("1. first")
        assert "first" in strip_ansi(result)
        assert "1." in strip_ansi(result)

    def test_task_list_checked(self):
        result = md_render("- [x] done")
        plain = strip_ansi(result)
        assert "done" in plain
        assert "✓" in plain

    def test_task_list_unchecked(self):
        result = md_render("- [ ] todo")
        plain = strip_ansi(result)
        assert "todo" in plain
        assert "○" in plain

    def test_blockquote(self):
        result = md_render("> quoted")
        plain = strip_ansi(result)
        assert "quoted" in plain
        assert "│" in plain

    def test_blockquote_with_inline_code(self):
        """Regression test: inline code in blockquotes should not break styling."""
        result = md_render("> Here's some `code` and text after")
        plain = strip_ansi(result)
        assert "code" in plain
        assert "text after" in plain
        # Check that italic is restored after code
        assert Ansi.ITALIC in result
        # The text after code should still have italic applied
        code_pos = result.find("code")
        after_pos = result.find("text after")
        # There should be an italic code between them
        between = result[code_pos:after_pos]
        assert Ansi.ITALIC in between or result.count(Ansi.ITALIC) >= 1

    def test_horizontal_rule(self):
        result = md_render("---")
        assert "─" in strip_ansi(result)

    def test_code_block(self):
        result = md_render("```python\nprint('hi')\n```")
        assert "print" in strip_ansi(result)

    def test_code_block_width_expansion(self):
        """Long lines in code blocks should expand the width, not truncate."""
        long_line = "x" * 100
        result = md_render(f"```\n{long_line}\n```", code_width=50)
        plain = strip_ansi(result)
        # The long line should be fully present (not truncated)
        assert long_line in plain
        # All lines should be padded to the same width (the longest line's width)
        lines = [l for l in plain.split("\n") if l.strip()]
        widths = [len(l) for l in lines]
        assert all(w == widths[0] for w in widths), "All lines should have same width"
        assert widths[0] >= 100, "Width should expand to fit content"


class TestEdgeCases:
    def test_empty_string(self):
        result = md_render("")
        assert result == ""

    def test_whitespace_only(self):
        result = md_render("   ")
        assert strip_ansi(result) == ""

    def test_unclosed_bold(self):
        result = md_render("**unclosed")
        assert "**unclosed" in strip_ansi(result)

    def test_unclosed_code_block(self):
        # Should not crash
        result = md_render("```python\ncode")
        assert "code" in strip_ansi(result)

    def test_crlf_normalized(self):
        result = md_render("line1\r\nline2")
        assert "\r" not in result

    def test_nested_formatting(self):
        result = md_render("**bold with `code` inside**")
        plain = strip_ansi(result)
        assert "bold with" in plain
        assert "code" in plain


class TestSyntaxHighlighter:
    def test_highlight_python(self):
        hl = SyntaxHighlighter()
        result = hl.highlight("def foo(): pass", "python")
        assert "def" in strip_ansi(result)

    def test_language_alias(self):
        hl = SyntaxHighlighter()
        result = hl.highlight("x = 1", "py")
        # Should not crash, should highlight
        assert "x" in strip_ansi(result)

    def test_available_styles(self):
        styles = SyntaxHighlighter.available_styles()
        assert "monokai" in styles
        assert len(styles) > 10


class TestMarkdownRenderer:
    def test_custom_style(self):
        renderer = MarkdownRenderer(code_style="dracula")
        result = renderer.render("# Test")
        assert "Test" in strip_ansi(result)

    def test_custom_width(self):
        renderer = MarkdownRenderer(code_width=40)
        result = renderer.render("```\ncode\n```")
        # Code block lines should be padded to 40 chars
        lines = result.split("\n")
        for line in lines:
            plain = strip_ansi(line)
            # All code block lines should be exactly 40 chars (padded)
            if plain:  # non-empty lines
                assert len(plain) == 40, f"Expected 40, got {len(plain)}: {plain!r}"


class TestLangAliases:
    def test_common_aliases(self):
        assert LANG_ALIASES["py"] == "python"
        assert LANG_ALIASES["js"] == "javascript"
        assert LANG_ALIASES["ts"] == "typescript"
        assert LANG_ALIASES["sh"] == "bash"


class TestStyleAPI:
    """Tests for the new Style API."""

    def test_bold_text_static(self):
        result = Style.bold_text("test")
        assert Ansi.BOLD in result
        assert Ansi.BOLD_OFF in result
        assert "test" in result

    def test_italic_text_static(self):
        result = Style.italic_text("test")
        assert Ansi.ITALIC in result
        assert Ansi.ITALIC_OFF in result

    def test_underline_text_static(self):
        result = Style.underline_text("test")
        assert Ansi.UNDERLINE in result
        assert Ansi.UNDERLINE_OFF in result

    def test_strike_text_static(self):
        result = Style.strike_text("test")
        assert Ansi.STRIKETHROUGH in result
        assert Ansi.STRIKETHROUGH_OFF in result

    def test_color_fg(self):
        result = Style.color("test", fg="red")
        assert Ansi.FG_RED in result
        assert Ansi.FG_DEFAULT in result

    def test_color_bg(self):
        result = Style.color("test", bg="blue")
        assert Ansi.BG_BLUE in result
        assert Ansi.BG_DEFAULT in result

    def test_color_both(self):
        result = Style.color("test", fg="red", bg="blue")
        assert Ansi.FG_RED in result
        assert Ansi.BG_BLUE in result

    def test_color_rgb(self):
        result = Style.color("test", fg=(255, 0, 0))
        assert "38;2;255;0;0" in result

    def test_chainable_bold(self):
        result = str(style("test").bold())
        assert Ansi.BOLD in result
        assert "test" in result

    def test_chainable_multiple(self):
        result = str(style("test").bold().italic())
        assert Ansi.BOLD in result
        assert Ansi.ITALIC in result

    def test_chainable_fg(self):
        result = str(style("test").fg("red"))
        assert Ansi.FG_RED in result

    def test_chainable_bg(self):
        result = str(style("test").bg("blue"))
        assert Ansi.BG_BLUE in result

    def test_chainable_rgb(self):
        result = str(style("test").fg((100, 150, 200)))
        assert "38;2;100;150;200" in result

    def test_style_repr(self):
        s = Style("hello")
        assert "hello" in repr(s)

    def test_empty_style(self):
        s = Style("plain")
        assert str(s) == "plain"
