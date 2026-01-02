from .DigitizerInfo import DigitizerInfo

class SpikeSafeInfo:
    """
    Class to hold the information of a SpikeSafe.

    Attributes
    ----------
    ip_address : str | None
        IP address of the SpikeSafe
    idn : str | None
        Identification string of the SpikeSafe
    board_type : str | None
        Board of the SpikeSafe
    spikesafe_type : str | None
        Type of the SpikeSafe
    zin_number : str | None
        ZIN number of the SpikeSafe
    version : str | None
        Ethernet Processor version of the SpikeSafe
    dsp_version : str | None
        DSP version of the SpikeSafe
    cpld_version : str | None
        CPLD version of the SpikeSafe
    serial_number : str | None
        Serial number of the SpikeSafe
    hardware_version : str | None
        Hardware version of the SpikeSafe
    last_calibration_date : str | None
        Last calibration date of the SpikeSafe
    minimum_compliance_voltage : float | None
        Minimum compliance voltage of the SpikeSafe in volts
    maximum_compliance_voltage : float | None
        Maximum compliance voltage of the SpikeSafe in volts
    minimum_set_current : float | None
        Minimum set current of the SpikeSafe in amps
    maximum_set_current : float | None
        Maximum set current of the SpikeSafe in amps
    minimum_pulse_width : float | None
        Minimum pulse width of the SpikeSafe in seconds
    maximum_pulse_width : float | None
        Maximum pulse width of the SpikeSafe in seconds
    minimum_pulse_width_offset : float | None
        Minimum pulse width offset of the SpikeSafe in microseconds
    maximum_pulse_width_offset : float | None
        Maximum pulse width offset of the SpikeSafe in microseconds
    has_digitizer : bool
        Whether the SpikeSafe has a digitizer
    digitizer_infos : list[DigitizerInfo]
        List of DigitizerInfo objects
    has_switch : bool
        Whether the SpikeSafe has a switch
    supports_discharge_query : bool
        Whether the SpikeSafe supports discharge query
    supports_multiple_digitizer_commands : bool
        Whether the SpikeSafe supports multiple digitizer commands
    supports_pulse_width_correction : bool
        Whether the SpikeSafe supports pulse width correction
    """

    ip_address: str | None
    idn: str | None
    board_type: str | None
    spikesafe_type: str | None
    zin_number: str | None
    version: str | None
    dsp_version: str | None
    cpld_version: str | None
    serial_number: str | None
    hardware_version: str | None
    last_calibration_date: str | None

    minimum_compliance_voltage: float | None
    maximum_compliance_voltage: float | None
    minimum_set_current: float | None
    maximum_set_current: float | None
    minimum_pulse_width: float | None
    maximum_pulse_width: float | None
    minimum_pulse_width_offset: float | None
    maximum_pulse_width_offset: float | None

    has_digitizer: bool
    digitizer_infos: list[DigitizerInfo]

    has_switch: bool

    supports_discharge_query: bool
    supports_multiple_digitizer_commands: bool
    supports_pulse_width_correction: bool

    def __init__(self) -> None:
        self.ip_address = None
        self.idn = None
        self.board_type = None
        self.spikesafe_type = None
        self.zin_number = None
        self.version = None
        self.dsp_version = None
        self.cpld_version = None
        self.serial_number = None
        self.hardware_version = None
        self.last_calibration_date = None

        self.minimum_compliance_voltage = None
        self.maximum_compliance_voltage = None
        self.minimum_set_current = None
        self.maximum_set_current = None
        self.minimum_pulse_width = None
        self.maximum_pulse_width = None
        self.minimum_pulse_width_offset = None
        self.maximum_pulse_width_offset = None

        self.has_digitizer = False
        self.digitizer_infos = []

        self.has_switch = False

        self.supports_discharge_query = False
        self.supports_multiple_digitizer_commands = False
        self.supports_pulse_width_correction = False