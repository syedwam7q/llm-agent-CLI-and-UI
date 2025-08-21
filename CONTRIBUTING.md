# Contributing to LLM Agent

Thank you for your interest in contributing to the LLM Agent project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

### Suggesting Enhancements

If you have an idea for an enhancement, please create an issue with:
- A clear, descriptive title
- A detailed description of the enhancement
- Any relevant mockups or examples
- Why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests to ensure they pass
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a Pull Request

## Development Setup

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd llm-agent
   ```

2. Install dependencies
   ```bash
   python install.py
   ```

3. Run tests
   ```bash
   pytest tests/
   ```

## Project Structure

The project follows this structure:
```
llm-agent/
├── src/                    # Source code
│   ├── main.py            # CLI entry point
│   ├── config/            # Configuration management
│   ├── core/              # Core agent logic
│   ├── tools/             # Tool implementations
│   └── ui/                # User interfaces
├── tests/                 # Test files
├── data/                  # Data storage
├── logs/                  # Application logs
└── ...
```

## Coding Standards

- Follow PEP 8 style guidelines
- Write docstrings for all functions, classes, and modules
- Include type hints where appropriate
- Write tests for new functionality

## Testing

- All new features should include tests
- Run the test suite before submitting a PR
- Ensure all tests pass

## Documentation

- Update documentation for any changes to functionality
- Document new features thoroughly
- Keep the README.md up to date

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to LLM Agent!