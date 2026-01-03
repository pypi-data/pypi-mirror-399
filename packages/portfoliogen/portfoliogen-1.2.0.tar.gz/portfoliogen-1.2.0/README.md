# PortfolioGen

A Python package that automatically generates professional portfolio websites with HTML, CSS, and JavaScript files. Choose from multiple templates designed for different professions and use cases.

## Features

- 🚀 **Easy to use**: Simple CLI and Python API
- 🎨 **Multiple Templates**: Developer and Photography portfolio templates
- 📱 **Responsive Design**: Mobile-first, works on all devices
- 🔧 **Customizable**: Custom folder names and template selection
- 📦 **Pip installable**: Standard Python package installation
- 🌐 **UTF-8 encoding**: Proper file encoding for international characters
- ⚡ **Modern Features**: Smooth animations, interactive components
- 📋 **Template Listing**: Easy discovery of available templates

## Installation

### From PyPI
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

List available templates:
```bash
portfoliogen --list
```

Generate a developer portfolio (default):
```bash
portfoliogen MyDeveloperPortfolio
```

Generate a photography portfolio:
```bash
portfoliogen -t photographer MyPhotographyPortfolio
```

Generate with specific template:
```bash
portfoliogen -t developer MyDevPortfolio
```

Show help:
```bash
portfoliogen --help
```

### Python API

```python
from portfoliogen import generate_portfolio

# Generate developer portfolio (default)
portfolio_path = generate_portfolio("MyPortfolio")
print(f"Portfolio created at: {portfolio_path}")

# Generate photography portfolio
portfolio_path = generate_portfolio("MyPhotos", template="photographer")

# Generate with custom name and template
portfolio_path = generate_portfolio("MyAwesomePortfolio", template="developer")
```

## Templates

### 🖥️ Developer Template
Perfect for software developers, programmers, and tech professionals:
- **Features**: Project showcase, skills section, GitHub integration
- **Sections**: Hero, About, Skills, Projects, Experience, Contact
- **Style**: Clean, modern, tech-focused design
- **Colors**: Professional blue and gray palette

### 📸 Photographer Template  
Designed for photographers, artists, and creative professionals:
- **Features**: Image gallery, testimonials, service pricing
- **Sections**: Hero, Portfolio Gallery, About, Services, Testimonials, Contact
- **Style**: Elegant, visual-focused with smooth animations
- **Colors**: Warm orange and sophisticated dark palette
- **Interactive**: Lightbox gallery, testimonial slider, contact form

## Generated Structure

When you run PortfolioGen, it creates the following structure:

```
MyPortfolio/
├── index.html          # Main HTML file with portfolio structure
├── styles.css          # CSS styles with responsive design
├── script.js           # JavaScript with animations and interactions
├── assets/             # Folder for images and media
│   └── README.md       # Placeholder file with instructions
```

## Template Features

### Developer Template
- **Responsive Grid Layout**: Projects displayed in clean grid
- **Smooth Scrolling**: Navigation with smooth scroll effects
- **Skills Visualization**: Progress bars and skill indicators
- **Contact Form**: Functional contact form with validation
- **Social Links**: GitHub, LinkedIn, Twitter integration

### Photographer Template
- **Image Gallery**: Filterable portfolio with categories
- **Lightbox Viewer**: Full-screen image viewing with navigation
- **Testimonial Slider**: Client testimonials with smooth transitions
- **Service Cards**: Pricing and service information
- **Mobile Optimized**: Touch-friendly navigation and interactions
- **Performance**: Optimized images and animations

## CLI Commands

```bash
# List all available templates
portfoliogen --list

# Generate with developer template (default)
portfoliogen MyPortfolio

# Generate with photographer template
portfoliogen -t photographer MyPhotos

# Generate with custom folder name
portfoliogen "My Amazing Portfolio" -t developer

# Show version
portfoliogen --version

# Show help
portfoliogen --help
```

## Customization Tips

### Developer Portfolio
- Add your projects to the portfolio section
- Update skills and technologies in the about section  
- Link to your GitHub, LinkedIn, and other profiles
- Replace placeholder content with your information

### Photography Portfolio
- Replace sample images with your own photos
- Update contact information in the contact section
- Customize services and pricing to match your offerings
- Add your social media links (Instagram, Facebook, etc.)

## Development

### Setting up development environment

```bash
git clone https://github.com/sameer-lamichhane/portfoliogen.git
cd portfoliogen
pip install -e .
```

### Testing the package locally

```bash
# Test CLI
python -m portfoliogen --list
python -m portfoliogen TestPortfolio -t photographer

# Test Python API
python -c "from portfoliogen import generate_portfolio; print(generate_portfolio('Test', 'developer'))"
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

### v1.2.0
- ✨ Added Photography template with gallery and testimonials
- 🎨 Enhanced Developer template with better responsive design
- 📋 Added `--list` command to show available templates
- 🔧 Improved CLI with better help and template validation
- 📱 Mobile-optimized designs for both templates
- ⚡ Performance improvements and smooth animations

### v1.0.0
- Initial release
- Basic portfolio generation
- CLI and Python API
- Default template
- UTF-8 encoding support
- Error handling for existing folders

## Roadmap

- [ ] Additional templates (minimal, corporate, creative)
- [ ] Custom color scheme options
- [ ] Image optimization and compression
- [ ] Live preview server
- [ ] Template customization wizard
- [ ] Integration with popular CSS frameworks
- [ ] Dark mode variants
- [ ] Multi-language support

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/sameer-lamichhane/portfoliogen/issues) page
2. Create a new issue with detailed information
3. Contact: [GitHub Profile](https://github.com/sameer-lamichhane)

## Examples

### Quick Start
```bash
# Install the package
pip install portfoliogen

# List available templates
portfoliogen --list

# Create a developer portfolio
portfoliogen MyDevPortfolio

# Create a photography portfolio
portfoliogen -t photographer MyPhotoSite
```

**Made with ❤️ by [Sameer Lamichhane](https://github.com/sameer-lamichhane)**