# PortfolioGen

A Python package that automatically generates portfolio project folders with HTML, CSS, and JavaScript files.

## Features

- 🚀 **Easy to use**: Simple CLI and Python API
- 📁 **Complete structure**: Generates HTML, CSS, JS, and assets folder
- 🎨 **Template support**: Multiple templates (extensible for future themes)
- 🔧 **Customizable**: Custom folder names and template selection
- 📦 **Pip installable**: Standard Python package installation
- 🌐 **UTF-8 encoding**: Proper file encoding for international characters
- ⚡ **Error handling**: Graceful handling of existing folders

## Installation

### From PyPI (when published)
```bash
pip install portfoliogen
```

### From source
```bash
git clone https://github.com/sameer-lamichhane/portfoliogen.git
cd portfoliogen
pip install -e .
```

## Usage

### Command Line Interface

Generate a portfolio with default name "MyPortfolio":
```bash
portfoliogen
```

Generate a portfolio with custom name:
```bash
portfoliogen MyAwesomePortfolio
```

Generate with specific template:
```bash
portfoliogen MyPortfolio --template modern
```

Show help:
```bash
portfoliogen --help
```

### Python API

```python
from portfoliogen import generate_portfolio

# Generate with default settings
portfolio_path = generate_portfolio()
print(f"Portfolio created at: {portfolio_path}")

# Generate with custom name
portfolio_path = generate_portfolio("MyCustomPortfolio")

# Generate with template (future feature)
portfolio_path = generate_portfolio("MyPortfolio", template="modern")
```

## Generated Structure

When you run PortfolioGen, it creates the following structure:

```
MyPortfolio/
├── index.html          # Main HTML file with portfolio structure
├── styles.css          # CSS styles with responsive design
├── script.js           # JavaScript with smooth scrolling and animations
├── assets/             # Folder for images and media
│   └── README.md       # Placeholder file
```

## Templates

Currently supported templates:
- `default`: Clean, professional portfolio layout
- `minimal`: (Coming soon) Minimalist design
- `modern`: (Coming soon) Modern, trendy layout
- `dark`: (Coming soon) Dark theme portfolio

## File Contents

### HTML Features
- Responsive design with mobile-first approach
- Navigation with smooth scrolling
- Sections for About, Projects, and Contact
- Semantic HTML structure
- Meta tags for SEO

### CSS Features
- Modern CSS Grid and Flexbox layouts
- Smooth animations and transitions
- Responsive breakpoints
- Professional color scheme
- Hover effects and interactions

### JavaScript Features
- Smooth scrolling navigation
- Scroll-based header effects
- Intersection Observer for animations
- Utility functions for dynamic content
- Modern ES6+ syntax

## Development

### Setting up development environment

```bash
git clone https://github.com/sameer-lamichhane/portfoliogen.git
cd portfoliogen
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Code formatting

```bash
black portfoliogen/
flake8 portfoliogen/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Basic portfolio generation
- CLI and Python API
- Default template
- UTF-8 encoding support
- Error handling for existing folders

## Roadmap

- [ ] Additional templates (minimal, modern, dark)
- [ ] Custom CSS/JS injection
- [ ] Image optimization
- [ ] Live preview server
- [ ] Template customization options
- [ ] Integration with popular CSS frameworks

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/sameer-lamichhane/portfoliogen/issues) page
2. Create a new issue with detailed information
3. Contact: your.email@examp