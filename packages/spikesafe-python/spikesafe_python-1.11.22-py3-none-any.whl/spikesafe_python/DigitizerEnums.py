from enum import Enum

class TimeSamplingMode(Enum):
    """
    Enum for time sampling mode for the Digitizer

    Methods
    -------
    friendly_name() -> str
        Returns a user-friendly name for the enum value.
    """
    MIDDLE_OF_TIME = 1
    END_OF_TIME = 2

    def friendly_name(self) -> str:
        """
        Returns a user-friendly name for the enum value.
        
        Returns
        -------
        str
            User-friendly name for the enum value.
        """
        return self.name.capitalize()

class SamplingMode(Enum):
    """
    Enum for sampling mode for the Digitizer

    Methods
    -------
    friendly_name() -> str
        Returns a user-friendly name for the enum value.
    """
    LINEAR = "LINEAR"
    FAST_LOG = "FASTLOG"
    MEDIUM_LOG = "MEDIUMLOG"
    SLOW_LOG = "SLOWLOG"
    CUSTOM = "CUSTOM"

    def friendly_name(self) -> str:
        """
        Returns a user-friendly name for the enum value.
        
        Returns
        -------
        str
            User-friendly name for the enum value.
        """

        # Define friendly names for each enum member
        friendly_names: dict[SamplingMode, str] = {
            SamplingMode.LINEAR: "Linear",
            SamplingMode.FAST_LOG: "Fast Log",
            SamplingMode.MEDIUM_LOG: "Medium Log",
            SamplingMode.SLOW_LOG: "Slow Log",
            SamplingMode.CUSTOM: "Custom",
        }
        return friendly_names.get(self, self.name)