from importlib.metadata import version, PackageNotFoundError

from .ChannelData import (
	ChannelData
)
from .Compensation import (
    Compensation,
    # Backwards compatibility to access static methods as functions outside of class
	get_optimum_compensation,
	get_custom_compensation,
    load_custom_compensation_table,
    load_custom_compensation_unique_device_types
)
from .DigitizerData import (
	DigitizerData
)
from .DigitizerDataFetch import (
    DigitizerDataFetch,   
    # Backwards compatibility to access static methods as functions outside of class
	fetch_voltage_data,
	fetch_voltage_data_sampling_mode_linear,
	fetch_voltage_data_sampling_mode_logarithmic,
	fetch_voltage_data_sampling_mode_custom,
	get_new_voltage_data_estimated_complete_time,
	wait_for_new_voltage_data
)
from . import DigitizerEnums # Recommended. Access to DigitizerEnums as a module (e.g., DigitizerEnums.SamplingMode.VERY_SLOW)
from .DigitizerEnums import ( 
    # Backwards compatibility. Access to DigitizerEnums members (e.g., SamplingMode.VERY_SLOW)
	SamplingMode,
	TimeSamplingMode
)
from .DigitizerInfo import (
    DigitizerInfo
)
from .DigitizerVfCustomSequence import (
    DigitizerVfCustomSequence
)
from .DigitizerVfCustomSequenceStep import (
    DigitizerVfCustomSequenceStep
)
from .Discharge import (
    Discharge,
    # Backwards compatibility to access static methods as functions outside of class
	get_spikesafe_channel_discharge_time
)
from .EventData import (
	EventData
)
from .MemoryTableReadData import (
	MemoryTableReadData,
    # Backwards compatibility to access static methods as functions outside of class
	log_memory_table_read
)
from .Precision import (
    Precision,
    # Backwards compatibility to access static methods as functions outside of class
	get_precise_compliance_voltage_command_argument,
	get_precise_current_command_argument,
	get_precise_duty_cycle_command_argument,
	get_precise_pulse_width_offset_command_argument,
	get_precise_pulse_width_correction_command_argument,
	get_precise_time_command_argument,
	get_precise_time_milliseconds_command_argument,
	get_precise_time_microseconds_command_argument,
	get_precise_voltage_protection_ramp_dt_command_argument,
	get_precise_voltage_protection_ramp_dv_command_argument
)
from .PulseWidthCorrection import (
    PulseWidthCorrection,
    # Backwards compatibility to access static methods as functions outside of class
    get_optimum_pulse_width_correction
)
from .ReadAllEvents import (
    ReadAllEvents,
    # Backwards compatibility to access static methods as functions outside of class
	log_all_events,
	read_all_events,
	read_until_event
)
from .ScpiFormatter import (
    ScpiFormatter,
    # Backwards compatibility to access static methods as functions outside of class
	get_scpi_format_integer_for_bool,
	get_scpi_format_on_state_for_bool
)
from .SerialPortConnection import (
    SerialPortConnection
)
from . import SpikeSafeEnums # Recommended. Access to SpikeSafeEnums as a module (e.g., SpikeSafeEnums.LoadImpedance.HIGH)
from .SpikeSafeEnums import (
	LoadImpedance,
	RiseTime
) # Backwards compatibility. Access to SpikeSafeEnums members (e.g., LoadImpedance.HIGH)
from .SpikeSafeError import (
	SpikeSafeError
)
from .SpikeSafeEvents import (
	SpikeSafeEvents
)
from .SpikeSafeInfo import (
    SpikeSafeInfo
)
from .SpikeSafeInfoParser import (
    SpikeSafeInfoParser,
    # Backwards compatibility to access static methods as functions outside of class
    parse_spikesafe_info
)
from .TcpSocket import (
	TcpSocket
)
from .TemperatureData import (
	TemperatureData
)
from .Threading import (
    Threading,
    # Backwards compatibility to access static methods as functions outside of class
	wait
)

try:
    __version__ = version("spikesafe_python")
except PackageNotFoundError:
    __version__ = "unknown"