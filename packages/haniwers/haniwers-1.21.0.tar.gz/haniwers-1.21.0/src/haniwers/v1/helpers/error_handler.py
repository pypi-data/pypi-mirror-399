"""Unified error handling for CLI commands.

Provides consistent error handling patterns across all CLI commands to ensure:
- Unified exception categorization (device, configuration, file, validation)
- Consistent error messages (user-facing via print_error + logging)
- Proper exception context preservation (exception chaining with 'from e')
- Standardized exit codes (0: success, 1: error, 2: permission error)

This module consolidates error handling patterns identified in P1-7 to reduce
duplication and improve consistency across cli/*.py commands.

Examples:
    Device connection errors:
        >>> try:
        ...     device.connect()
        ... except SerialException as e:
        ...     ErrorHandler.device(e, context="DAQ")
        ...     raise typer.Exit(code=1)

    Configuration loading errors:
        >>> try:
        ...     cfg = ConfigLoader(path).config
        ... except FileNotFoundError as e:
        ...     ErrorHandler.config(e, context="Loading")
        ...     raise typer.Exit(code=1)

    File validation errors:
        >>> try:
        ...     path = validate_file_path(input_file)
        ... except FileNotFoundError as e:
        ...     ErrorHandler.file(e, context="Input validation")
        ...     raise typer.Exit(code=1)
"""

from typing import Optional, Type
from serial import SerialException
from loguru import logger

from haniwers.v1.helpers.exceptions import (
    InvalidChannelError,
    InvalidThresholdError,
    InvalidThresholdFormatError,
    InvalidCSVError,
    InvalidIDError,
)
from haniwers.v1.helpers.console import print_error, print_warning


class ErrorHandler:
    """Centralized error handling for consistent patterns across CLI commands.

    Why this matters:
        Error handling appears in 32+ try-except blocks across 6 CLI command
        files with inconsistent patterns (duplicate catches, missing specific
        exception types, inconsistent logging). This class consolidates patterns
        to ensure:
        - User-facing messages are clear and actionable
        - Logging captures full context for debugging
        - Exception types are properly classified
        - Exit codes are consistent (0 = success, 1 = error, 2 = permission)

    Design Pattern:
        Each error category has a static method that handles both user output
        (print_error) and logging (logger.error) consistently. Callers convert
        exceptions to CLI-specific types (e.g., raise typer.Exit(code=1)).

    Usage:
        >>> try:
        ...     device.connect()
        ... except SerialException as e:
        ...     ErrorHandler.device(e, context="DAQ setup")
        ...     raise typer.Exit(code=1)
    """

    @staticmethod
    def device(
        error: Exception,
        context: str = "Device operation",
        user_message: Optional[str] = None,
    ) -> None:
        """Handle device communication and connection errors.

        Recognizes and appropriately handles:
        - SerialException: Port not found, already in use, permission denied
        - Other hardware-level exceptions

        Args:
            error: Exception that occurred during device operation
            context: Context for logging (e.g., "DAQ setup", "Port test")
            user_message: Custom user-facing message (default: auto-generated)
        """
        if isinstance(error, SerialException):
            user_msg = user_message or f"Cannot connect to the device: {error}"
            logger_msg = f"Serial connection failed during {context}: {error}"
        else:
            user_msg = user_message or f"Device error: {error}"
            logger_msg = f"Device operation failed during {context}: {error}"

        print_error(user_msg)
        logger.error(logger_msg)

    @staticmethod
    def config(
        error: Exception,
        context: str = "Configuration",
        user_message: Optional[str] = None,
    ) -> None:
        """Handle configuration loading and validation errors.

        Recognizes and handles:
        - FileNotFoundError: Config file not found
        - ValueError: Invalid configuration values
        - AttributeError: Missing configuration fields
        - Other config-related exceptions

        Args:
            error: Exception that occurred during config operation
            context: Context for logging (e.g., "Loading", "Validation")
            user_message: Custom user-facing message (default: auto-generated)
        """
        if isinstance(error, FileNotFoundError):
            user_msg = user_message or f"Configuration file not found: {error}"
            logger_msg = f"Config file missing during {context}: {error}"
        elif isinstance(error, ValueError):
            user_msg = user_message or f"Invalid configuration values: {error}"
            logger_msg = f"Config validation failed during {context}: {error}"
        elif isinstance(error, AttributeError):
            user_msg = user_message or f"Configuration structure error: {error}"
            logger_msg = f"Config attribute error during {context}: {error}"
        else:
            user_msg = user_message or f"Configuration error: {error}"
            logger_msg = f"Config operation failed during {context}: {error}"

        print_error(user_msg)
        logger.error(logger_msg)

    @staticmethod
    def file(
        error: Exception,
        context: str = "File operation",
        user_message: Optional[str] = None,
    ) -> None:
        """Handle file I/O and path validation errors.

        Recognizes and handles:
        - FileNotFoundError: File doesn't exist
        - IsADirectoryError: Path is a directory, not a file
        - NotADirectoryError: Path is a file, not a directory
        - PermissionError: Access denied
        - Other file I/O exceptions

        Args:
            error: Exception that occurred during file operation
            context: Context for logging (e.g., "Input file", "Output dir")
            user_message: Custom user-facing message (default: auto-generated)
        """
        if isinstance(error, FileNotFoundError):
            user_msg = user_message or f"File not found: {error}"
            logger_msg = f"File not found during {context}: {error}"
        elif isinstance(error, IsADirectoryError):
            user_msg = user_message or f"Expected file but found directory: {error}"
            logger_msg = f"Directory found instead of file during {context}: {error}"
        elif isinstance(error, NotADirectoryError):
            user_msg = user_message or f"Expected directory but found file: {error}"
            logger_msg = f"File found instead of directory during {context}: {error}"
        elif isinstance(error, PermissionError):
            user_msg = user_message or f"Permission denied: {error}"
            logger_msg = f"Permission denied during {context}: {error}"
        else:
            user_msg = user_message or f"File operation error: {error}"
            logger_msg = f"File operation failed during {context}: {error}"

        print_error(user_msg)
        logger.error(logger_msg)

    @staticmethod
    def validation(
        error: Exception,
        context: str = "Validation",
        user_message: Optional[str] = None,
    ) -> None:
        """Handle parameter and data validation errors.

        Recognizes and handles custom validation exceptions:
        - InvalidChannelError: Channel number out of range
        - InvalidThresholdError: Threshold value out of range
        - InvalidThresholdFormatError: Threshold string format invalid
        - InvalidCSVError: CSV format or content invalid
        - InvalidIDError: ID format invalid
        - ValueError: Generic validation failure

        Args:
            error: Exception that occurred during validation
            context: Context for logging (e.g., "Threshold parsing")
            user_message: Custom user-facing message (default: auto-generated)
        """
        if isinstance(error, InvalidChannelError):
            user_msg = user_message or f"Invalid channel number: {error}"
        elif isinstance(error, InvalidThresholdError):
            user_msg = user_message or f"Invalid threshold value: {error}"
        elif isinstance(error, InvalidThresholdFormatError):
            user_msg = user_message or f"Invalid threshold format: {error}"
        elif isinstance(error, InvalidCSVError):
            user_msg = user_message or f"Invalid CSV format: {error}"
        elif isinstance(error, InvalidIDError):
            user_msg = user_message or f"Invalid ID format: {error}"
        elif isinstance(error, ValueError):
            user_msg = user_message or f"Invalid value: {error}"
        else:
            user_msg = user_message or f"Validation error: {error}"

        logger_msg = f"Validation failed during {context}: {error}"
        print_error(user_msg)
        logger.error(logger_msg)

    @staticmethod
    def data(
        error: Exception,
        context: str = "Data processing",
        user_message: Optional[str] = None,
    ) -> None:
        """Handle data processing and transformation errors.

        Handles errors during data reading, parsing, or transformation:
        - ValueError: Data conversion or format error
        - KeyError: Missing expected data field
        - IndexError: Data structure access error
        - Other data processing exceptions

        Args:
            error: Exception that occurred during data processing
            context: Context for logging (e.g., "CSV reading", "Row parsing")
            user_message: Custom user-facing message (default: auto-generated)
        """
        if isinstance(error, (KeyError, IndexError)):
            user_msg = user_message or f"Data structure error: {error}"
        elif isinstance(error, ValueError):
            user_msg = user_message or f"Data conversion error: {error}"
        else:
            user_msg = user_message or f"Data processing error: {error}"

        logger_msg = f"Data error during {context}: {error}"
        print_error(user_msg)
        logger.error(logger_msg)

    @staticmethod
    def unexpected(
        error: Exception,
        context: str = "Operation",
        user_message: Optional[str] = None,
    ) -> None:
        """Handle unexpected/unclassified exceptions.

        Used for catch-all Exception handlers that should never occur in
        normal operation. Logs full traceback for debugging.

        Args:
            error: Unexpected exception
            context: Context for logging (e.g., "DAQ execution")
            user_message: Custom user-facing message (default: generic)
        """
        user_msg = user_message or f"An unexpected error occurred: {error}"
        logger_msg = f"Unexpected error during {context}: {error}"

        print_error(user_msg)
        logger.error(logger_msg, exc_info=True)

    @staticmethod
    def permission(
        error: Exception,
        context: str = "Operation",
        user_message: Optional[str] = None,
    ) -> int:
        """Handle permission-related errors.

        Used for exceptions related to access control:
        - PermissionError: User lacks required permissions
        - Suggests remediation (add user to group, etc.)

        Returns:
            Exit code 2 (for use in typer.Exit(code=2))

        Args:
            error: Permission-related exception
            context: Context for logging (e.g., "Serial port access")
            user_message: Custom user-facing message (default: auto-generated)
        """
        if isinstance(error, PermissionError):
            user_msg = user_message or (
                f"Permission denied: {error}\nRun 'haniwers port list' to check port permissions"
            )
        else:
            user_msg = user_message or f"Access denied: {error}"

        logger_msg = f"Permission denied during {context}: {error}"
        print_error(user_msg)
        logger.error(logger_msg)

        return 2
