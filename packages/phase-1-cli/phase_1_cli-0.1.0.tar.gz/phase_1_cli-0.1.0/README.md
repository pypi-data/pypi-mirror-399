# Modern Terminal Todo Application

A beautiful, interactive command-line todo application built with Python, featuring both a Text User Interface (TUI) and traditional CLI commands.

## Features

- **Interactive TUI** - Full-featured text-based user interface with keyboard navigation
- **CLI Commands** - Quick task management from the command line
- **ASCII Art Banner** - Beautiful pyfiglet-powered branding
- **Rich Formatting** - Colorful output with rich tables and formatting
- **Keyboard Shortcuts** - Efficient navigation and task management
- **Task Statistics** - Real-time progress tracking

## Installation

### From PyPI

```bash
pip install phase-1-cli
```

### From Source

```bash
git clone <repository-url>
cd phase-1-cli
pip install -e .
```

## Usage

### Interactive TUI Mode

Launch the full interactive interface:

```bash
phase-1-cli ui
# or simply
phase-1-cli
```

**Keyboard Shortcuts:**
- `a` - Add new task
- `e` - Edit selected task
- `d` - Delete selected task
- `space` - Toggle task completion
- `q` - Quit application
- Arrow keys - Navigate tasks

### CLI Commands

Quick task management from the command line:

```bash
# Add a new task
phase-1-cli add "Buy groceries" --desc "Milk, eggs, bread"
todo add "Call doctor"

# List all tasks
phase-1-cli list
todo list --pending    # Show only pending tasks
todo list --completed  # Show only completed tasks

# Mark task as complete
phase-1-cli complete 1

# Delete a task
phase-1-cli delete 2 --yes  # Skip confirmation

# Show statistics
phase-1-cli stats
```

## Features in Detail

### Text User Interface (TUI)

The TUI provides a rich, interactive experience with:
- **ASCII Art Header** - Eye-catching "TODO APP" banner
- **Live Statistics Panel** - Shows total, pending, completed tasks and progress percentage
- **Data Table** - Clean display of all tasks with status indicators
- **Modal Dialogs** - User-friendly forms for adding and editing tasks
- **Confirmation Dialogs** - Safe deletion with confirmation prompts

### CLI Interface

Fast command-line operations for:
- Quick task addition without launching the TUI
- Listing tasks with filtering options
- Batch operations and scripting support
- Integration with shell scripts and automation

### Task Management

- **Task Properties**: ID, title, description, completion status, creation timestamp
- **Validation**: Prevents empty task titles
- **Statistics**: Automatic calculation of totals, pending, completed, and progress percentage

## Technology Stack

- **Textual** - Modern TUI framework for rich terminal interfaces
- **Typer** - Beautiful CLI with automatic help generation
- **Rich** - Rich text and beautiful formatting in the terminal
- **Pyfiglet** - ASCII art text generation
- **Pydantic** - Data validation and settings management

## Architecture

The application follows clean architecture principles:

- **Data Models** - Business logic decoupled from UI (`Task`, `TaskManager`)
- **UI Components** - Reusable screens and dialogs (`AddTaskScreen`, `EditTaskScreen`, `ConfirmDialog`)
- **CLI Commands** - Separate Typer commands for command-line operations
- **Main Application** - Textual app with reactive UI updates

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd phase-1-cli

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Project Structure

```
phase-1-cli/
├── src/
│   └── phase_1_cli/
│       └── main.py          # Main application code
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Requirements

- Python >= 3.11
- Dependencies:
  - pydantic >= 2.12.5
  - pyfiglet >= 1.0.2
  - rich >= 14.2.0
  - textual >= 6.11.0
  - typer >= 0.15.1

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

**Marjan Ahmed**
- Email: marjan.ahmed08@yahoo.com

## Changelog

### Version 0.1.0 (Initial Release)

- Interactive TUI with full keyboard navigation
- CLI commands for quick task management
- ASCII art banners with pyfiglet
- Rich table formatting for task lists
- Task statistics and progress tracking
- Add, edit, delete, and toggle tasks
- Confirmation dialogs for destructive actions
- Demo tasks for first-time users

## Roadmap

Future enhancements planned:
- [ ] Task persistence (JSON/SQLite storage)
- [ ] Task priorities and categories
- [ ] Due dates and reminders
- [ ] Search and filter functionality
- [ ] Export tasks to various formats
- [ ] Task notes and attachments
- [ ] Multi-user support
- [ ] Configuration file support
- [ ] Themes and customization

## Support

For bug reports and feature requests, please use the GitHub issue tracker.

---

Made with Python and love for the terminal.
