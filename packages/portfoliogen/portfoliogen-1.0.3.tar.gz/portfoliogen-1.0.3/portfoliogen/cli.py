"""
Command-line interface for PortfolioGen.
"""

import argparse
import sys
from .generator import generate_portfolio


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
        choices=["default", "minimal", "modern", "dark"],
        default="default",
        help="Portfolio template to use (default: default)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Generate the portfolio
        portfolio_path = generate_portfolio(args.folder_name, args.template)
        
        # Print success message with absolute path
        print(f"✅ Portfolio successfully created!")
        print(f"📁 Location: {portfolio_path}")
        print(f"🌐 Open index.html in your browser to view your portfolio.")
        
        # Additional template info if not default
        if args.template != "default":
            print(f"🎨 Template: {args.template}")
            
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