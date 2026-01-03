"""
Command-line interface for godaddycheck.
"""

import sys
import argparse
import json
from typing import Optional
from .client import GoDaddyClient


def format_price(price: Optional[float], currency: str = "USD") -> str:
    """Format price for display."""
    if price is None:
        return "N/A"
    return f"{currency} ${price:.2f}"


def cmd_check(args):
    """Handle check command."""
    try:
        client = GoDaddyClient()
        result = client.check(args.domain, check_type=args.type)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            domain = result.get("domain", args.domain)
            available = result.get("available", False)
            price = result.get("price")
            currency = result.get("currency", "USD")

            status = "Available" if available else "Taken"
            print(f"\nDomain: {domain}")
            print(f"Status: {status}")
            if available and price is not None:
                print(f"Price: {format_price(price, currency)}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_suggest(args):
    """Handle suggest command."""
    try:
        client = GoDaddyClient()
        results = client.suggest(args.query, limit=args.limit)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\nFound {len(results)} suggestions for '{args.query}':\n")
            print("Note: Use 'godaddycheck check <domain>' to check availability and pricing.\n")

            for i, result in enumerate(results, 1):
                domain = result.get("domain", "N/A")
                print(f"{i}. {domain}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_tlds(args):
    """Handle tlds command."""
    try:
        client = GoDaddyClient()
        results = client.tlds()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\nFound {len(results)} TLDs:\n")

            display_count = args.limit if args.limit else len(results)
            for i, tld in enumerate(results[:display_count], 1):
                name = tld.get("name", "N/A")
                tld_type = tld.get("type", "N/A")
                print(f"{i}. .{name} (type: {tld_type})")

            if args.limit and len(results) > args.limit:
                print(f"\n... and {len(results) - args.limit} more")
                print("(Use --limit 0 to show all)")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GoDaddy domain availability checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  godaddycheck check example.com
  godaddycheck check example.com --type FULL
  godaddycheck suggest tech --limit 5
  godaddycheck tlds --limit 20
  godaddycheck check example.com --json

Environment variables:
  GODADDY_API_KEY     - Your GoDaddy API key
  GODADDY_API_SECRET  - Your GoDaddy API secret
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    subparsers.required = True

    # Check command
    parser_check = subparsers.add_parser("check", help="Check domain availability")
    parser_check.add_argument("domain", help="Domain name to check (e.g., example.com)")
    parser_check.add_argument(
        "--type",
        choices=["FAST", "FULL"],
        default="FAST",
        help="Check type (default: FAST)"
    )
    parser_check.add_argument("--json", action="store_true", help="Output as JSON")
    parser_check.set_defaults(func=cmd_check)

    # Suggest command
    parser_suggest = subparsers.add_parser("suggest", help="Get domain suggestions")
    parser_suggest.add_argument("query", help="Keyword for suggestions")
    parser_suggest.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of suggestions (default: 10)"
    )
    parser_suggest.add_argument("--json", action="store_true", help="Output as JSON")
    parser_suggest.set_defaults(func=cmd_suggest)

    # TLDs command
    parser_tlds = subparsers.add_parser("tlds", help="List available TLDs")
    parser_tlds.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of TLDs to show (0 = all, default: 20)"
    )
    parser_tlds.add_argument("--json", action="store_true", help="Output as JSON")
    parser_tlds.set_defaults(func=cmd_tlds)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
