"""
Command-line interface for PortfolioGen.
"""

import argparse
import sys
import os
from .generator import generate_portfolio


def list_templates():
    """List available templates."""
    print("📋 Available Templates:")
    print("  • developer   - Clean developer portfolio with project showcase")
    print("  • photographer - Professional photography portfolio with gallery")
    print()
    print("💡 Usage: portfoliogen -t <template> <folder_name>")
    print("📖 Example: portfoliogen -t photographer MyPhotographyPortfolio")


def main():
    """
    Main CLI entry point for portfoliogen.
    """
    parser = argparse.ArgumentParser(
        description="Generate a portfolio project folder with HTML, CSS, and JS files.",
        prog="portfoliogen"
    )
    
    parser.add_argument(
        "folder_name",
        nargs="?",
        default="MyPortfolio",
        help="Name of the portfolio folder to create (default: MyPortfolio)"
    )
    
    parser.add_argument(
        "-t", "--template",
        choices=["developer", "photographer"],
        default="developer",
        help="Portfolio template to use (default: developer)"
    )
    
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available templates"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.2.0"
    )
    
    args = parser.parse_args()
    
    # Handle list command
    if args.list:
        list_templates()
        return
    
    try:
        # Generate the portfolio
        portfolio_path = generate_portfolio(args.folder_name, args.template)
        
        # Print success message with absolute path
        print(f"✅ Portfolio successfully created!")
        print(f"📁 Location: {portfolio_path}")
        print(f"🎨 Template: {args.template}")
        print(f"🌐 Open index.html in your browser to view your portfolio.")
        
        # Template-specific tips
        if args.template == "photographer":
            print()
            print("📸 Photography Portfolio Tips:")
            print("  • Replace sample images with your own photos")
            print("  • Update contact information in the contact section")
            print("  • Customize services and pricing to match your offerings")
        elif args.template == "developer":
            print()
            print("💻 Developer Portfolio Tips:")
            print("  • Add your projects to the portfolio section")
            print("  • Update skills and technologies in the about section")
            print("  • Link to your GitHub, LinkedIn, and other profiles")
            
    except OSError as e:
        print(f"❌ Error creating portfolio: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()