"""MAC address formatting utilities for device identification.

What is MAC address formatting?
    MAC addresses from ESP32 devices need to be converted to a filesystem-safe
    format for use in filenames. This module handles that conversion.

Why do we need this?
    - ESP32 MAC addresses are returned in colon-separated format: AA:BB:CC:DD:EE:FF
    - Filenames need filesystem-safe characters (no colons on some systems)
    - We standardize to lowercase hex without colons: aabbccddee00f
    - Provides consistent format across all device identification features

Example:
    ```python
    from haniwers.v1.helpers.mac_address import format_mac_address

    # Convert ESP32 format to filename format
    mac = format_mac_address("AA:BB:CC:DD:EE:FF")
    print(mac)  # Output: "aabbccddee00f"

    # Handle invalid inputs gracefully
    mac = format_mac_address(None)
    print(mac)  # Output: "unknown"

    mac = format_mac_address("")
    print(mac)  # Output: "unknown"
    ```
"""


def format_mac_address(mac: str | None) -> str:
    """Convert MAC address to filesystem-safe filename format.

    What this does:
        Takes a MAC address in any format and converts it to lowercase hex
        without colons, suitable for use in filenames. Returns fallback
        identifier "unknown" for invalid inputs.

    Args:
        mac (str | None): MAC address in various formats
            - Standard format: "AA:BB:CC:DD:EE:FF" (colon-separated)
            - Alternative format: "AABBCCDDEEEF" (no colons)
            - None or empty: Returns "unknown" fallback
            - Any other format: Attempts to extract hex digits

    Returns:
        str: Formatted MAC address
            - Valid MAC: 12 lowercase hex characters (e.g., "aabbccddeeef")
            - Invalid/None/Empty: "unknown" (fallback identifier)

    How it works:
        1. Check for None or empty string → return "unknown"
        2. Remove all colons and hyphens from input
        3. Convert remaining characters to lowercase
        4. Validate result has 12 hex characters
        5. Return formatted MAC or "unknown" if invalid

    When to use:
        - Converting esptool MAC output to filename format
        - Ensuring consistent MAC format across all modules
        - Fallback when MAC retrieval fails

    Raises:
        Nothing (always returns valid string, never raises exceptions)

    Examples:
        ```python
        # Standard colon-separated format (common from esptool)
        format_mac_address("AA:BB:CC:DD:EE:FF")
        # Returns: "aabbccddeeef"

        # Hyphen-separated format
        format_mac_address("AA-BB-CC-DD-EE-FF")
        # Returns: "aabbccddeeef"

        # Already formatted
        format_mac_address("aabbccddeeef")
        # Returns: "aabbccddeeef"

        # Uppercase input (converts to lowercase)
        format_mac_address("AA:BB:CC:DD:EE:FF")
        # Returns: "aabbccddeeef"

        # Invalid inputs return fallback
        format_mac_address(None)
        # Returns: "unknown"

        format_mac_address("")
        # Returns: "unknown"

        format_mac_address("invalid")
        # Returns: "unknown"
        ```
    """
    # Handle None or empty input
    if not mac:
        return "unknown"

    # Remove separators (colons, hyphens) and convert to lowercase
    cleaned = mac.replace(":", "").replace("-", "").lower()

    # Validate: must be 12 hex characters
    if len(cleaned) != 12:
        return "unknown"

    # Validate: all characters must be hexadecimal digits
    try:
        int(cleaned, 16)  # Try to parse as hexadecimal
    except ValueError:
        # Not valid hex
        return "unknown"

    return cleaned
