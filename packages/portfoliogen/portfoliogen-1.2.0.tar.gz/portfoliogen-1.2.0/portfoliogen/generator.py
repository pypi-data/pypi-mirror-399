"""
Core portfolio generation functionality.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
try:
    from importlib.resources import files
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files


def generate_portfolio(folder_name: str = "MyPortfolio", template: str = "developer") -> str:
    """
    Generate a portfolio project folder with HTML, CSS, and JS files.
    
    Args:
        folder_name (str): Name of the portfolio folder to create
        template (str): Template type ('developer' or 'photographer')
    
    Returns:
        str: Absolute path of the created portfolio folder
    
    Raises:
        OSError: If folder creation fails
    """
    # Validate template
    valid_templates = ["developer", "photographer"]
    if template not in valid_templates:
        raise ValueError(f"Invalid template '{template}'. Available templates: {', '.join(valid_templates)}")
    
    # Get absolute path for the portfolio folder
    portfolio_path = Path.cwd() / folder_name
    
    # Handle existing folder
    if portfolio_path.exists():
        print(f"Warning: Folder '{folder_name}' already exists. Contents may be overwritten.")
    
    try:
        # Create main portfolio directory
        portfolio_path.mkdir(exist_ok=True)
        
        # Create assets subdirectory
        assets_path = portfolio_path / "assets"
        assets_path.mkdir(exist_ok=True)
        
        # Generate and write HTML file
        html_content = _get_template_content(template, "index.html")
        _write_file(portfolio_path / "index.html", html_content)
        
        # Generate and write CSS file
        css_content = _get_template_content(template, "styles.css")
        _write_file(portfolio_path / "styles.css", css_content)
        
        # Generate and write JS file
        js_content = _get_template_content(template, "script.js")
        _write_file(portfolio_path / "script.js", js_content)
        
        # Create a placeholder in assets folder
        _write_file(assets_path / "README.md", "# Assets\n\nPlace your images and other media files here.")
        
        return str(portfolio_path.absolute())
        
    except OSError as e:
        raise OSError(f"Failed to create portfolio folder: {e}")


def _write_file(file_path: Path, content: str) -> None:
    """
    Write content to file with UTF-8 encoding.
    
    Args:
        file_path (Path): Path to the file
        content (str): Content to write
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _get_template_content(template: str, filename: str) -> str:
    """
    Read template content from source files.
    
    Args:
        template (str): Template type (e.g., 'developer', 'photographer')
        filename (str): Template filename (e.g., 'index.html')
    
    Returns:
        str: File content
    
    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    try:
        # Try to read from package resources first
        try:
            template_files = files('portfoliogen') / 'templates' / template
            template_file = template_files / filename
            content = template_file.read_text(encoding='utf-8')
            return content
        except (FileNotFoundError, ModuleNotFoundError, AttributeError):
            # Fallback to file system path (for development)
            current_dir = Path(__file__).parent
            template_file = current_dir / "templates" / template / filename
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise FileNotFoundError(f"Template file not found: {template}/{filename}")
                
    except Exception as e:
        raise FileNotFoundError(f"Could not read template {template}/{filename}: {e}")
