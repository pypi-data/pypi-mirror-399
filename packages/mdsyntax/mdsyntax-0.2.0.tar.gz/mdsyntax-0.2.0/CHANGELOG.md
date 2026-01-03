# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-XX-XX

### Added

- New `Style` class for styling arbitrary text
  - Static methods: `Style.bold_text()`, `Style.italic_text()`, `Style.color()`, etc.
  - Chainable API: `style("text").bold().italic().fg("red")`
- RGB color support via `Style.color(text, fg=(255, 0, 0))`
- `Ansi` class now exported for direct access to ANSI codes

### Changed

- Switched from `colorama.init(autoreset=True)` to `colorama.just_fix_windows_console()` for better compatibility
- Code blocks now expand width to fit long lines instead of truncating
- Use targeted ANSI resets instead of full reset for better style preservation

### Fixed

- Inline code in blockquotes no longer breaks italic styling for subsequent text
- Code block width now properly constrains content

## [0.1.0] - 2025-01-XX

### Added

- Initial release
- Markdown rendering with ANSI formatting
- Syntax highlighting for code blocks (powered by Pygments)
- Support for headers, bold, italic, strikethrough, inline code
- Support for lists (ordered, unordered, task lists)
- Support for blockquotes and horizontal rules
- Support for links
- CLI tool (`mdsyntax`)
- Auto-detection of 24-bit true color support
- Configurable code block styling and width
