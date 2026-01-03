from typing import Tuple

import dns.exception
import dns.resolver


def check_domain_availability(domain: str) -> Tuple[bool, str]:
    """
    Check if a domain is available using DNS lookups.

    Args:
        domain: The domain name to check

    Returns:
        A tuple of (is_available, status_message)
        - is_available: True if domain is available (NXDOMAIN), False if taken
        - status_message: "AVAILABLE", "TAKEN", or error message
    """
    # Validate TLD by checking if it has NS records
    parts = domain.split(".")
    if len(parts) < 2:
        return None, "Invalid domain format"

    tld = parts[-1]

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5

        # Check if TLD is valid by querying its NS records
        try:
            resolver.resolve(tld, "NS")
        except dns.resolver.NXDOMAIN:
            return None, f"Invalid TLD: .{tld}"
        except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            # Some TLDs might not respond to direct queries, continue anyway
            pass

        # Try NS records first
        try:
            answers = resolver.resolve(domain, "NS")
            if answers:
                return False, "TAKEN"
        except dns.resolver.NXDOMAIN:
            # NXDOMAIN means the domain doesn't exist (available)
            return True, "AVAILABLE"
        except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            # No NS records, fall back to A record check
            pass

        # Fall back to A record check
        try:
            answers = resolver.resolve(domain, "A")
            if answers:
                return False, "TAKEN"
        except dns.resolver.NXDOMAIN:
            # NXDOMAIN means the domain doesn't exist (available)
            return True, "AVAILABLE"
        except dns.resolver.NoAnswer:
            # Domain exists but no A record - consider taken
            return False, "TAKEN"

    except dns.exception.Timeout:
        return None, "DNS query timed out"
    except Exception as e:
        return None, f"Error checking domain: {str(e)}"

    # If we get here, something unexpected happened
    return None, "Unable to determine domain status"
