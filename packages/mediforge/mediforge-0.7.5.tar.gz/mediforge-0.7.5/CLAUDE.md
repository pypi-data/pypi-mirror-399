# CLAUDE.md

## Project Overview

Mediforge is a Python CLI toolkit for media processing. It replaces complex GUI applications (Shotcut, Ardour) for linear media operations by orchestrating ffmpeg and ImageMagick through human-readable YAML scenario files.

**Full specification:** `docs/mediforge-implementation.md`

Read the implementation document before starting any development work. It contains complete architecture, data models, API definitions, and phased implementation plan.

---

## Quick Reference

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run specific test file
pytest tests/test_timecode.py -v

# Type checking
mypy src/mediforge

# Linting
ruff check src/mediforge

# Test CLI
mediforge --help
mediforge info <file>
```

---

## Development Rules

### Code Style

- Python 3.11+ features permitted (type hints, match statements, etc.)
- Use type annotations for all function signatures
- Docstrings: Google style, required for public APIs
- Line length: 100 characters
- Formatting: ruff

### Project Structure

```
mediforge/
├── src/mediforge/       # Package source
│   ├── core/            # Timecode, models, parsing, errors
│   ├── backends/        # FFmpeg command construction
│   ├── plugins/         # CLI command implementations
│   ├── config/          # Presets and configuration
│   └── utils/           # Logging, temp files
├── tests/               # Pytest tests
│   └── fixtures/        # Test media files and scenarios
└── docs/                # Documentation
```

### Dependencies

Core runtime:
- `click` — CLI framework
- `pydantic` — Validation
- `ruamel.yaml` — YAML parsing with line numbers
- `rich` — Terminal output

External tools (must be installed on system):
- `ffmpeg` / `ffprobe` ≥ 5.0

### Testing Requirements

- All new code requires tests
- Use pytest fixtures for shared setup
- Integration tests for CLI commands use subprocess
- Test fixtures: minimal media files generated with ffmpeg (see spec)
- Coverage target: 80%+

---

## Implementation Phases

Implement in order. Each phase must pass tests before proceeding.

### Phase 1: Foundation
Files: `cli.py`, `core/timecode.py`, `core/errors.py`, `core/probe.py`, `plugins/info/`

Deliverable: `mediforge info <file>` works

### Phase 2: Video Composition
Files: `core/models.py`, `core/scenario.py`, `backends/ffmpeg.py`, `backends/executor.py`, `plugins/video/compose.py`, `utils/tempfiles.py`

Deliverable: `mediforge video compose scenario.yaml -o out.mp4` works with images and videos, fade effects, `--dry-run`, `--preview`

### Phase 2b: Advanced Video
Updates to `backends/ffmpeg.py` for crossfades, speed adjustment, `--progress`

### Phase 3: Audio Composition
Files: `plugins/audio/compose.py`

Deliverable: `mediforge audio compose scenario.yaml -o out.wav` works

### Phase 4: Audio Tools
Files: `plugins/audio/normalize.py`, `plugins/audio/master.py`, `config/defaults.py`, `config/loader.py`

Deliverable: `mediforge audio normalize` and `mediforge audio master` work with presets

### Phase 5: Muxing
Files: `plugins/mux/`

Deliverable: `mediforge mux video.mp4 audio.wav -o output.mp4` works

---

## Key Technical Decisions

### Timecode Handling
- External format: `H:MM:SS.mmm` strings in YAML
- Internal format: `Decimal` for precision
- All conversions via `core/timecode.py`

### Error Reporting
- Use `ruamel.yaml` to preserve line numbers during parsing
- Validation errors must include file path, line number, and context snippet
- FFmpeg errors: capture stderr, show last 10 lines, preserve temp directory

### FFmpeg Command Construction
- Build commands as `list[str]`, never shell strings
- Use `subprocess.run()` with `capture_output=True`
- For complex compositions, build filter graphs programmatically via `FilterGraph` class
- Two-pass loudness normalization: first pass analyzes, second pass applies

### Temporary Files
- Create in system temp with `mediforge-` prefix
- Delete on success unless `--keep-temp`
- Always preserve on error
- Log temp directory path at debug level

### Plugin System
- Each plugin is a subpackage under `plugins/`
- Must expose `register(parent: click.Group)` function
- Discovery via `pkgutil.iter_modules()`

---

## Common Patterns

### Adding a New Command

1. Create module in appropriate plugin directory
2. Define click command with options
3. Import and register in plugin's `__init__.py`
4. Add tests

```python
# plugins/audio/newcmd.py
import click

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True)
@click.pass_context
def newcmd(ctx, input_file, output):
    """Command description."""
    log_level = ctx.obj.get('log_level', 'warning')
    # Implementation
```

### Validation with Source Location

```python
from mediforge.core.errors import ValidationError, SourceLocation

def validate_something(value, line_num, file_path):
    if not valid:
        raise ValidationError(
            message="Description of problem",
            location=SourceLocation(file=file_path, line=line_num),
            expected="what was expected",
            found=str(value),
        )
```

### FFmpeg Execution

```python
from mediforge.backends.executor import CommandExecutor

executor = CommandExecutor(dry_run=dry_run)
result = executor.execute(
    command=['ffmpeg', '-i', str(input_path), ...],
    stage="video encoding",
    temp_dir=temp_path,
)
```

---

## Verification Commands

After each phase, verify:

```bash
# Phase 1
mediforge --help
mediforge --log-level=debug info tests/fixtures/sample_video.mp4

# Phase 2
mediforge video compose tests/fixtures/scenarios/valid_video.yaml -o /tmp/out.mp4
mediforge video compose scenario.yaml -o /tmp/out.mp4 --dry-run
mediforge video compose scenario.yaml -o /tmp/out.mp4 --preview --keep-temp

# Phase 3
mediforge audio compose tests/fixtures/scenarios/valid_audio.yaml -o /tmp/out.wav

# Phase 4
mediforge audio normalize input.wav -o output.wav --lufs=-14
mediforge audio master input.wav -o output.wav --preset=streaming

# Phase 5
mediforge mux video.mp4 audio.wav -o final.mp4
```

---

## Do Not

- Do not use `shell=True` in subprocess calls
- Do not hardcode paths; use `Path` objects
- Do not suppress exceptions in context managers
- Do not use `print()` for logging; use the logging module
- Do not implement features beyond current phase scope
- Do not skip tests

---

## Reference Files

- **Full specification:** `docs/mediforge-implementation.md`
- **Scenario format examples:** `tests/fixtures/scenarios/`
- **Test fixtures generation:** See "Test Fixtures" section in spec
