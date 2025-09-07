# Trello Sprint Generator

A powerful tool to automatically generate Trello cards from markdown sprint files. Perfect for converting detailed sprint planning documents into organized Trello boards with tasks, milestones, and acceptance criteria.

## 🚀 Quick Start

### 🖥️ GUI Mode (Recommended)
```bash
# Clone the repository
git clone https://github.com/TalesAugusto1/trello-task-creator.git
cd trello-task-creator

# Install dependencies
pip install -r requirements.txt

# Launch the GUI
python gui.py
# or
make gui
```

### 💻 Command Line Mode
```bash
# Test connection
python main.py --test-connection

# Generate cards from example
python main.py --file examples/example_sprint.md --board-id YOUR_BOARD_ID --dry-run
```

## 📁 Project Structure

```
trello-task-creator/
├── src/                    # Source code package
│   ├── cli.py             # Command-line interface
│   ├── config.py          # Configuration management
│   ├── models.py          # Data models
│   ├── trello_client.py   # Trello API client
│   ├── markdown_parser.py # Markdown parsing
│   ├── sprint_generator.py# Card generation
│   └── utils.py           # Utility functions
├── tests/                 # Test suite
├── config/                # Configuration files
│   ├── trello_config.json.template
│   └── secrets.env        # Your API credentials (create this)
├── examples/              # Example files
│   └── example_sprint.md  # Sample sprint file
├── docs/                  # Documentation
│   └── README.md          # Detailed documentation
├── main.py               # CLI entry point
├── gui.py                # GUI entry point
├── setup.py              # Package setup
├── Makefile              # Development commands
└── requirements.txt      # Dependencies
```

## 📚 Documentation

- **[Complete Documentation](docs/README.md)** - Detailed setup and usage guide
- **[Examples](examples/)** - Sample sprint files and usage examples
- **[Configuration](config/)** - Configuration templates and setup

## 🛠️ Development

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run all checks
make check

# Format code
make format
```

## 📄 License

MIT License - feel free to use and modify as needed.

---

**Need help?** Check the [detailed documentation](docs/README.md) or [examples](examples/) directory.
