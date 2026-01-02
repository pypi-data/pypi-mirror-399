class DigitizerInfo:
    """
    Class to represent the information of a Digitizer in a SpikeSafe.

    Attributes
    ----------
    number : int | None = None
        Digitizer number
    version : str | None = None
        Digitizer version
    serial_number : str | None = None
        Digitizer serial number
    hardware_version : str | None = None
        Digitizer hardware version
    last_calibration_date : str | None = None
        Digitizer last calibration date
    minimum_aperture : float | None = None
        Minimum aperture of the Digitizer in microseconds
    maximum_aperture : float | None = None
        Maximum aperture of the Digitizer in microseconds
    minimum_trigger_delay : float | None = None
        Minimum trigger delay of the Digitizer in microseconds
    maximum_trigger_delay : float | None = None
        Maximum trigger delay of the Digitizer in microseconds
    voltage_ranges : list[int]
        List of voltage ranges supported by the Digitizer
    """

    number: int | None = None
    version: str | None = None
    serial_number: str | None = None
    hardware_version: str | None = None
    last_calibration_date: str | None = None

    minimum_aperture: float | None = None
    maximum_aperture: float | None = None
    minimum_trigger_delay: float | None = None
    maximum_trigger_delay: float | None = None
    voltage_ranges: list[int] = []

    def __init__(self) -> None:
        self.number = None
        self.version = None
        self.serial_number = None
        self.hardware_version = None
        self.last_calibration_date = None

        self.minimum_aperture = None
        self.maximum_aperture = None
        self.minimum_trigger_delay = None
        self.maximum_trigger_delay = None
        self.voltage_ranges = []