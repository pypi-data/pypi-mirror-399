import unittest

from package import check_domain_availability


class TestIsFree(unittest.TestCase):
    def test_taken_domain(self):
        """Test that google.com is taken."""
        is_available, message = check_domain_availability("google.com")
        self.assertFalse(is_available)
        self.assertEqual(message, "TAKEN")

    def test_available_domain(self):
        """Test that a nonsense domain is available."""
        # Using a very unlikely domain name
        is_available, message = check_domain_availability(
            "thisdomainshoulddefinitelynotexist12345678.com"
        )
        self.assertTrue(is_available)
        self.assertEqual(message, "AVAILABLE")

    def test_invalid_domain(self):
        """Test handling of invalid domain format."""
        is_available, message = check_domain_availability("invalid..domain")
        # Should return None (error) or handle gracefully
        self.assertIsNone(is_available)
        self.assertTrue("Invalid" in message or "Error" in message)
