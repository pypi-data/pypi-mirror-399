import sys

from .main import check_domain_availability


def main():
    """CLI entry point for isfree."""
    if len(sys.argv) != 2:
        print("Usage: isfree <domain>", file=sys.stderr)
        sys.exit(2)

    domain = sys.argv[1]
    is_available, message = check_domain_availability(domain)

    if is_available is None:
        # Error occurred
        print(f"\033[33m⚠\033[0m {message}", file=sys.stderr)
        sys.exit(2)
    elif is_available:
        # Domain is available
        print(f"\033[32m✓\033[0m {domain} is available")
        sys.exit(0)
    else:
        # Domain is taken
        print(f"\033[31m✗\033[0m {domain} is taken")
        sys.exit(1)


if __name__ == "__main__":
    main()
