# Contributing to Dexcom Menubar App

Thank you for your interest in contributing! This project aims to help people with diabetes manage their glucose levels more conveniently.

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Provide detailed information about the bug or feature request
- Include your macOS version and Python version
- For bugs, include steps to reproduce and error messages

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/dexcom-menubar-app.git
cd dexcom-menubar-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

### Code Guidelines

- Follow PEP 8 style guidelines
- Add comments for complex logic
- Update documentation for new features
- Test your changes before submitting

### Testing

Currently, the project doesn't have automated tests. When adding new features:
- Test manually with real Dexcom Share data
- Verify notifications work correctly
- Check error handling
- Ensure the menubar updates properly

### Security

- Never commit credentials or API keys
- Use environment variables or keychain for sensitive data
- Review code for security vulnerabilities
- Report security issues privately

## Feature Ideas

Some ideas for contributions:
- Support for mmol/L units
- Customizable glucose range thresholds
- More notification options
- Statistics and trends
- Dark mode improvements
- Accessibility improvements

## Questions?

Feel free to open an issue for any questions or discussions!

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Remember we're all here to help people with diabetes
