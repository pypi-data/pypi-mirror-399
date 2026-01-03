"""Configuration override and validation helper.

This module provides a unified interface for applying CLI option overrides
to configuration objects with automatic validation. It eliminates the need
for repetitive _apply_overrides() functions and manual validation in each
command file.

Usage Example:
    from haniwers.v1.config.overrider import ConfigOverrider

    # Load base configuration
    loader = ConfigLoader(config_path)
    cfg = loader.config

    # Apply CLI overrides with automatic validation
    overrider = ConfigOverrider(cfg)
    overrider.apply_device_overrides(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        label=device_label,
    )
    overrider.apply_sampler_overrides(
        workspace=workspace,
        filename_prefix=filename_prefix,
        events_per_file=events_per_file,
    )

    # Validate all configurations at once
    overrider.validate("device", "sampler")

Benefits:
    - Single responsibility: Override and validate in one place
    - DRY principle: No duplicate override logic across commands
    - Type safety: Leverages Pydantic validation
    - Clear error messages: Unified error handling
    - Maintainability: Changes to override logic only need to be made once
"""

from pathlib import Path
from typing import Any, Optional

from pydantic import ValidationError

from haniwers.v1.config.model import (
    DeviceConfig,
    HaniwersConfig,
    MockerConfig,
    SamplerConfig,
    SensorConfig,
)
from haniwers.v1.log.logger import logger as base_logger

# Bind context for all operations in this module
logger = base_logger.bind(context="config.overrider")


class ConfigOverrider:
    """Apply CLI option overrides to configuration with automatic validation.

    This class centralizes the logic for applying CLI option overrides to
    configuration objects. It provides type-safe overriding with automatic
    Pydantic validation, eliminating repetitive code in command handlers.

    Attributes:
        config: The HaniwersConfig object to override
        _override_log: List of applied overrides for debugging

    Example:
        >>> loader = ConfigLoader("config.toml")
        >>> cfg = loader.config
        >>> overrider = ConfigOverrider(cfg)
        >>> overrider.apply_device_overrides(port="/dev/ttyUSB0")
        >>> overrider.validate("device", "sampler")
    """

    def __init__(self, config: HaniwersConfig) -> None:
        """Initialize ConfigOverrider.

        Args:
            config: HaniwersConfig object to apply overrides to
        """
        self.config = config
        self._override_log: list[tuple[str, str, Any]] = []

    def _apply_override(self, config_obj: Any, key: str, value: Any, section: str) -> None:
        """Apply a single override if value is not None.

        Args:
            config_obj: Configuration object (e.g., cfg.device)
            key: Attribute name to override
            value: New value (override only if not None)
            section: Section name for logging (e.g., "device", "sampler")
        """
        if value is not None:
            old_value = getattr(config_obj, key, None)
            setattr(config_obj, key, value)
            self._override_log.append((section, key, value))
            logger.debug(f"Override [{section}.{key}]: {old_value} → {value}")

    def apply_device_overrides(
        self,
        port: Optional[str] = None,
        baudrate: Optional[int] = None,
        timeout: Optional[float] = None,
        label: Optional[str] = None,
    ) -> None:
        """Apply CLI overrides to DeviceConfig.

        Args:
            port: Serial port path (e.g., /dev/ttyUSB0)
            baudrate: Serial communication speed (e.g., 9600)
            timeout: Serial read timeout in seconds
            label: Device configuration label
        """
        logger.debug("Applying DeviceConfig overrides")
        self._apply_override(self.config.device, "port", port, "device")
        self._apply_override(self.config.device, "baudrate", baudrate, "device")
        self._apply_override(self.config.device, "timeout", timeout, "device")
        self._apply_override(self.config.device, "label", label, "device")

    def apply_sampler_overrides(
        self,
        workspace: Optional[Path] = None,
        filename_prefix: Optional[str] = None,
        filename_suffix: Optional[str] = None,
        events_per_file: Optional[int] = None,
        number_of_files: Optional[int] = None,
        duration: Optional[float] = None,
        stream_mode: Optional[bool] = None,
        mode: Optional[str] = None,
        label: Optional[str] = None,
    ) -> None:
        """Apply CLI overrides to SamplerConfig.

        Args:
            workspace: Output directory for data files
            filename_prefix: Output filename prefix
            filename_suffix: Output filename suffix
            events_per_file: Number of events per output file
            number_of_files: Maximum number of output files
            duration: Measurement duration in seconds
            stream_mode: Enable continuous streaming
            mode: Data collection mode (count_based or time_based)
            label: Sampler configuration label
        """
        logger.debug("Applying SamplerConfig overrides")
        # Convert Path to str if provided
        workspace_str = str(workspace) if workspace else None
        self._apply_override(self.config.sampler, "workspace", workspace_str, "sampler")
        self._apply_override(self.config.sampler, "filename_prefix", filename_prefix, "sampler")
        self._apply_override(self.config.sampler, "filename_suffix", filename_suffix, "sampler")
        self._apply_override(self.config.sampler, "events_per_file", events_per_file, "sampler")
        self._apply_override(self.config.sampler, "number_of_files", number_of_files, "sampler")
        self._apply_override(self.config.sampler, "duration", duration, "sampler")
        self._apply_override(self.config.sampler, "stream_mode", stream_mode, "sampler")
        self._apply_override(self.config.sampler, "mode", mode, "sampler")
        self._apply_override(self.config.sampler, "label", label, "sampler")

        # Auto-switch mode to time_based if duration is provided
        if duration is not None and mode is None:
            self._apply_override(self.config.sampler, "mode", "time_based", "sampler")

    def apply_mocker_overrides(
        self,
        label: Optional[str] = None,
        csv_path: Optional[Path] = None,
        shuffle: Optional[bool] = None,
        speed: Optional[float] = None,
        jitter: Optional[float] = None,
        loop: Optional[bool] = None,
    ) -> None:
        """Apply CLI overrides to MockerConfig.

        Args:
            label: Mocker configuration label
            csv_path: CSV file to replay
            shuffle: Randomize event order
            speed: Playback speed multiplier
            jitter: Timing jitter for random generation
            loop: Repeat CSV data when reaching end
        """
        logger.debug("Applying MockerConfig overrides")
        self._apply_override(self.config.mocker, "label", label, "mocker")
        # Convert Path to str if provided
        csv_path_str = str(csv_path) if csv_path else None
        self._apply_override(self.config.mocker, "csv_path", csv_path_str, "mocker")
        self._apply_override(self.config.mocker, "shuffle", shuffle, "mocker")
        self._apply_override(self.config.mocker, "speed", speed, "mocker")
        self._apply_override(self.config.mocker, "jitter", jitter, "mocker")
        self._apply_override(self.config.mocker, "loop", loop, "mocker")

    def apply_sensor_overrides(
        self,
        thresholds: Optional[dict[int, int]] = None,
        centers: Optional[dict[int, int]] = None,
        center: Optional[int] = None,
        nsteps: Optional[int] = None,
        step_size: Optional[int] = None,
        threshold: Optional[int] = None,
    ) -> None:
        """Apply CLI overrides to SensorConfig objects.

        This method supports multiple override modes:
        1. Selective threshold override: Use thresholds dict to set both threshold
           and center values for specific channels (e.g., {1: 280, 3: 320})
        2. Selective center override: Use centers dict to set only center values
           for specific channels (e.g., {1: 280, 2: 320})
        3. Global parameter override: Apply nsteps/step_size/threshold to all sensors
        4. Global center override: Apply same center value to all sensors

        Args:
            thresholds: Dict mapping channel ID to threshold value.
                       Sets both threshold and center to the same value.
                       Example: {1: 280, 2: 320, 3: 300}
                       Only specified channels will be updated
            centers: Dict mapping channel ID to center value.
                    Sets only the center value for scanning.
                    Example: {1: 300, 2: 350}
                    Only specified channels will be updated
            center: Center threshold value for all sensors
                   Overrides centers dict if both specified
            nsteps: Number of steps from center (applied to all sensors)
            step_size: Step size between measurements (applied to all sensors)
            threshold: Current detection threshold (applied to all sensors)

        Raises:
            KeyError: If channel ID in thresholds/centers dict doesn't exist in config

        Example:
            >>> # Override specific channels with threshold and center
            >>> overrider.apply_sensor_overrides(
            ...     thresholds={1: 280, 3: 320},
            ...     nsteps=10,
            ...     step_size=1
            ... )
            >>>
            >>> # Override specific channels with only center values
            >>> overrider.apply_sensor_overrides(
            ...     centers={1: 300, 2: 350},
            ...     nsteps=5
            ... )
            >>>
            >>> # Override all channels with same center value
            >>> overrider.apply_sensor_overrides(
            ...     center=300,
            ...     nsteps=5
            ... )
            >>>
            >>> # Set threshold for all channels
            >>> overrider.apply_sensor_overrides(
            ...     threshold=500
            ... )
        """
        logger.debug("Applying SensorConfig overrides")

        # Mode 1: Selective channel override using thresholds dict
        # Sets both threshold (current value) and center (scan center point)
        if thresholds is not None:
            for ch_id, vth in thresholds.items():
                ch_key = f"ch{ch_id}"
                if ch_key not in self.config.sensors:
                    raise KeyError(
                        f"Channel '{ch_key}' not found in sensors config. "
                        f"Available channels: {list(self.config.sensors.keys())}"
                    )
                self._apply_override(
                    self.config.sensors[ch_key], "threshold", vth, f"sensors.{ch_key}"
                )

        # Mode 2: Selective channel override using centers dict
        # Sets only center value (scan center point) for specified channels
        if centers is not None:
            for ch_id, center_val in centers.items():
                ch_key = f"ch{ch_id}"
                if ch_key not in self.config.sensors:
                    raise KeyError(
                        f"Channel '{ch_key}' not found in sensors config. "
                        f"Available channels: {list(self.config.sensors.keys())}"
                    )
                self._apply_override(
                    self.config.sensors[ch_key], "center", center_val, f"sensors.{ch_key}"
                )

        # Mode 3: Global center override (applied to all sensors)
        if center is not None:
            for ch_key in self.config.sensors:
                self._apply_override(
                    self.config.sensors[ch_key], "center", center, f"sensors.{ch_key}"
                )

        # Apply nsteps to all sensors (if specified)
        if nsteps is not None:
            for ch_key in self.config.sensors:
                self._apply_override(
                    self.config.sensors[ch_key], "nsteps", nsteps, f"sensors.{ch_key}"
                )

        # Apply step_size to all sensors (if specified)
        if step_size is not None:
            for ch_key in self.config.sensors:
                self._apply_override(
                    self.config.sensors[ch_key],
                    "step_size",
                    step_size,
                    f"sensors.{ch_key}",
                )

        # Apply threshold to all sensors (if specified)
        if threshold is not None:
            for ch_key in self.config.sensors:
                self._apply_override(
                    self.config.sensors[ch_key],
                    "threshold",
                    threshold,
                    f"sensors.{ch_key}",
                )

    def validate_device(self) -> DeviceConfig:
        """Validate DeviceConfig after overrides.

        Returns:
            Validated DeviceConfig object

        Raises:
            ValidationError: If validation fails
        """
        try:
            validated = DeviceConfig.model_validate(self.config.device.model_dump())
            logger.debug("DeviceConfig validation: PASS")
            return validated
        except ValidationError as e:
            logger.error(f"DeviceConfig validation failed: {e}")
            raise

    def validate_sampler(self) -> SamplerConfig:
        """Validate SamplerConfig after overrides.

        Returns:
            Validated SamplerConfig object

        Raises:
            ValidationError: If validation fails
        """
        try:
            validated = SamplerConfig.model_validate(self.config.sampler.model_dump())
            logger.debug("SamplerConfig validation: PASS")
            return validated
        except ValidationError as e:
            logger.error(f"SamplerConfig validation failed: {e}")
            raise

    def validate_mocker(self) -> MockerConfig:
        """Validate MockerConfig after overrides.

        Returns:
            Validated MockerConfig object

        Raises:
            ValidationError: If validation fails
        """
        try:
            validated = MockerConfig.model_validate(self.config.mocker.model_dump())
            logger.debug("MockerConfig validation: PASS")
            return validated
        except ValidationError as e:
            logger.error(f"MockerConfig validation failed: {e}")
            raise

    def validate_sensors(self) -> dict[str, SensorConfig]:
        """Validate all SensorConfig objects after overrides.

        Validates each sensor in the sensors dictionary (typically ch1, ch2, ch3).

        Returns:
            Dictionary of validated SensorConfig objects with same keys

        Raises:
            ValidationError: If any sensor validation fails
        """
        try:
            validated_sensors = {}
            for ch_key, sensor in self.config.sensors.items():
                validated = SensorConfig.model_validate(sensor.model_dump())
                validated_sensors[ch_key] = validated
                logger.debug(f"SensorConfig[{ch_key}] validation: PASS")
            logger.debug("All SensorConfig validations: PASS")
            return validated_sensors
        except ValidationError as e:
            logger.error(f"SensorConfig validation failed: {e}")
            raise

    def validate(self, *sections: str) -> None:
        """Validate specified configuration sections.

        This flexible method allows commands to validate only the sections
        they actually use, avoiding unnecessary validation errors.

        Args:
            *sections: Section names to validate
                      Valid values: "device", "sampler", "mocker", "sensors"
                      If no sections specified, validates all sections.

        Raises:
            ValidationError: If any validation fails
            ValueError: If invalid section name provided

        Example:
            >>> # Validate only device and sampler
            >>> overrider.validate("device", "sampler")
            >>>
            >>> # Validate sensors for threshold scanning
            >>> overrider.validate("device", "sensors")
            >>>
            >>> # Validate all sections
            >>> overrider.validate()
        """
        if not sections:
            # No sections specified: validate all
            sections = ("device", "sampler", "mocker", "sensors")

        logger.debug(f"Validating configurations: {', '.join(sections)}")

        validators = {
            "device": self.validate_device,
            "sampler": self.validate_sampler,
            "mocker": self.validate_mocker,
            "sensors": self.validate_sensors,
        }

        for section in sections:
            if section not in validators:
                raise ValueError(
                    f"Invalid section: {section}. Valid options: {', '.join(validators.keys())}"
                )
            validators[section]()

        logger.debug(f"Validation successful: {', '.join(sections)}")

    def validate_all(self) -> None:
        """Validate all configuration sections.

        Validates device, sampler, mocker, and sensor configurations.
        This is a convenience method equivalent to validate() with no args.

        Raises:
            ValidationError: If any validation fails
        """
        self.validate()

    def get_override_summary(self) -> str:
        """Get a summary of all applied overrides.

        Returns:
            Formatted string showing all overrides for debugging

        Example:
            >>> overrider.get_override_summary()
            'Overrides applied:\\n  device.port = /dev/ttyUSB0\\n  sampler.workspace = data/'
        """
        if not self._override_log:
            return "No overrides applied"

        summary_lines = ["Overrides applied:"]
        for section, key, value in self._override_log:
            summary_lines.append(f"  {section}.{key} = {value}")

        return "\n".join(summary_lines)
