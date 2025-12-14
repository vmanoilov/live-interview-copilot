# Contributing to Live Interview Copilot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Chrome version, Python version)
   - Logs (backend console, browser console)

### Suggesting Enhancements

1. Check if the feature has been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach
   - Any UI/UX mockups if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly (see TESTING.md)
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## 💻 Development Setup

### Prerequisites

- Python 3.9+
- Node.js (for JavaScript linting)
- Chrome Browser

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/live-interview-copilot.git
cd live-interview-copilot

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env

# Extension setup
cd ../extension
# Load unpacked extension in Chrome
```

## 📝 Code Style

### Python

- Follow PEP 8
- Use type hints
- Add docstrings for functions
- Keep functions focused and small
- Use meaningful variable names

### JavaScript

- Use modern ES6+ syntax
- Add JSDoc comments for complex functions
- Use `const`/`let`, avoid `var`
- Keep functions pure when possible
- Use async/await for promises

### General

- Write self-documenting code
- Comment complex logic
- Update documentation for API changes
- Keep commits atomic and well-described

## 🧪 Testing

Before submitting a PR:

```bash
# Test Python syntax
cd backend
python -m py_compile *.py

# Test JavaScript syntax
cd ../extension
node -c *.js

# Manual testing
# Follow steps in TESTING.md
```

## 📦 Project Structure

```
live-interview-copilot/
├── extension/           # Chrome Extension
│   ├── manifest.json    # Extension config
│   ├── background.js    # Service worker
│   ├── offscreen.js     # Audio processing
│   └── content_script.js # UI layer
├── backend/            # Python backend
│   ├── main.py         # FastAPI app
│   ├── deepgram_client.py
│   └── groq_client.py
└── docs/               # Documentation
```

## 🎯 Areas for Contribution

### High Priority

- [ ] Response streaming for lower latency
- [ ] Better error handling and recovery
- [ ] Unit tests for backend
- [ ] Integration tests for extension
- [ ] Performance optimizations

### Medium Priority

- [ ] Multi-language transcription support
- [ ] Resume parsing from PDF/DOCX
- [ ] Custom prompt templates
- [ ] Conversation history
- [ ] Analytics dashboard

### Nice to Have

- [ ] Dark mode UI
- [ ] Custom themes
- [ ] Keyboard shortcuts
- [ ] Export transcript feature
- [ ] Multiple LLM provider support

## 🔒 Security

### Reporting Vulnerabilities

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email the maintainers privately
2. Describe the vulnerability
3. Include steps to reproduce
4. Wait for a response before disclosure

### Security Best Practices

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate all user inputs
- Keep dependencies updated
- Follow Chrome Extension security guidelines

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Help others learn and grow
- Be patient with newcomers

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## 🏷️ Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: Add streaming response support
fix: Resolve WebSocket reconnection issue
docs: Update setup instructions
refactor: Simplify audio processing logic
test: Add unit tests for Deepgram client
```

Prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

## 📚 Documentation

When adding features:

1. Update relevant .md files
2. Add inline code comments
3. Update API documentation
4. Include usage examples
5. Update troubleshooting guide

## ✅ Pull Request Checklist

Before submitting:

- [ ] Code follows project style guidelines
- [ ] All files have appropriate comments
- [ ] Documentation is updated
- [ ] Changes are tested manually
- [ ] No syntax errors
- [ ] No security vulnerabilities introduced
- [ ] API keys and secrets not committed
- [ ] Commit messages are clear

## 🙏 Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Acknowledged in project documentation

## 📞 Getting Help

Need help contributing?

- Review existing code and documentation
- Check Issues for similar questions
- Ask in pull request comments
- Contact maintainers

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making Live Interview Copilot better! 🎉
