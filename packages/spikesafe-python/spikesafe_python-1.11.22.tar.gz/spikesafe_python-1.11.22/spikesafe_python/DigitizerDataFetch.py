# Goal: Read all new voltage readings from SpikeSafe PSMU Digitizer
# SCPI Command: VOLT:FETC?
# Array of voltage readings are parsed into DigitizerData class
# Example data return: b'9.9712145e-01,1.0005457e+00,3.2105038e+01\n'

from __future__ import annotations
import sys
import logging
import time
from .DigitizerData import DigitizerData
from .DigitizerEnums import TimeSamplingMode, SamplingMode
from .DigitizerVfCustomSequence import DigitizerVfCustomSequence
from .TcpSocket import TcpSocket
from .Threading import wait

log = logging.getLogger(__name__)

class DigitizerDataFetch:
    """
    Provides methods to fetch voltage data from the SpikeSafe digitizer.
    
    Methods
    -------
    fetch_voltage_data(spike_safe_socket: TcpSocket, enable_logging: bool | None = None, digitizer_number: int | None = None) -> list[DigitizerData]
        Returns an array of voltage readings from the digitizer obtained through a fetch query.
    fetch_voltage_data_sampling_mode_linear(spike_safe_socket: TcpSocket, time_sampling_mode: TimeSamplingMode, aperture_microseconds: int, reading_count: int, hardware_trigger_delay_microseconds: int = 0, pulse_period_seconds: float = 0.0, enable_logging: bool | None = None, digitizer_number: int | None = None) -> list[DigitizerData]
        Returns an array of voltage readings using linear sampling mode from the digitizer obtained through a fetch query.
    fetch_voltage_data_sampling_mode_logarithmic(spike_safe_socket: TcpSocket, time_sampling_mode: TimeSamplingMode, sampling_mode: SamplingMode, hardware_trigger_delay_microseconds: int = 0, enable_logging: bool | None = None, digitizer_number: int | None = None) -> list[DigitizerData]
        Returns an array of voltage readings using logarithmic sampling mode from the digitizer obtained through a fetch query.
    fetch_voltage_data_sampling_mode_custom(spike_safe_socket: TcpSocket, time_sampling_mode: TimeSamplingMode, custom_sequence: DigitizerVfCustomSequence, hardware_trigger_delay_microseconds: int = 0, enable_logging: bool | None = None, digitizer_number: int | None = None) -> list[DigitizerData]
        Returns an array of voltage readings using custom sampling mode from the digitizer obtained through a fetch query.
    wait_for_new_voltage_data(spike_safe_socket: TcpSocket, wait_time: float = 0.0, enable_logging: bool | None = None, timeout: float | None = None, digitizer_number: int | None = None) -> None
        Queries the SpikeSafe PSMU digitizer until it responds that it has acquired new data.
    get_new_voltage_data_estimated_complete_time(aperture_microseconds: int, reading_count: int, hardware_trigger_count: int | None = None, hardware_trigger_delay_microseconds: int | None = None) -> float
        Returns the estimated minimum possible time in seconds it will take for the SpikeSafe PSMU digitizer to acquire new voltage readings. If hardware triggering is used, this does not take into account the pulse period, so the actual time may be longer.
    """
    @staticmethod
    def fetch_voltage_data(
        spike_safe_socket: TcpSocket,
        enable_logging: bool | None = None,
        digitizer_number: int | None = None
    ) -> list[DigitizerData]:
        """Returns an array of voltage readings from the digitizer obtained through a fetch query 

        Parameters
        ----------
        spike_safe_socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        enable_logging : bool, Optional
            Overrides spike_safe_socket.enable_logging attribute (default to None will use spike_safe_socket.enable_logging value)
        digitizer_number : int, Optional
            The Digitizer number to fetch from. If None, fetches from Digitizer 1.
        
        Returns
        -------
        digitizer_data_collection: DigitizerData[]
            Contains an array of DigitizerData objects which have a defined voltage_reading and sample_number attribute

        Raises
        ------
        Exception
            On any error
        """
        try:            
            # fetch the Digitizer voltage readings
            prefix = "VOLT" if digitizer_number is None else f"VOLT{digitizer_number}"
            spike_safe_socket.send_scpi_command(f'{prefix}:FETC?', enable_logging)
            digitizer_data_string = spike_safe_socket.read_data(enable_logging)

            # set up the DigitizerData array to be returned
            digitizer_data_collection = []

            # put the fetched data in a plottable data format
            voltage_reading_strings = digitizer_data_string.split(",")
            sample = 1
            for v in voltage_reading_strings:
                data_point = DigitizerData()
                data_point.voltage_reading = float(v)
                data_point.sample_number = sample

                digitizer_data_collection.append(data_point)
                sample += 1

            return digitizer_data_collection

        except Exception as err:
            # print any error to the log file and raise error to function caller
            log.error("Error fetching digitizer voltage data: {}".format(err))                                     
            raise

    @staticmethod
    def fetch_voltage_data_sampling_mode_linear(
        spike_safe_socket: TcpSocket,
        time_sampling_mode: TimeSamplingMode,
        aperture_microseconds: int,
        reading_count: int,
        hardware_trigger_delay_microseconds: int = 0,
        pulse_period_seconds: float = 0.0,
        enable_logging: bool | None = None,
        digitizer_number: int | None = None
    ) -> list[DigitizerData]:
        """Returns an array of voltage readings using linear sampling mode from the digitizer obtained through a fetch query 

        Parameters
        ----------
        spike_safe_socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        time_sampling_mode : TimeSamplingMode
            The time sampling mode to use for the voltage data. This should be an instance of the TimeSamplingMode enum from DigitizerEnums.
        aperture_microseconds : int
            The aperture in microseconds for the voltage data
        reading_count : int
            The number of readings to fetch
        hardware_trigger_delay_microseconds : int, Optional
            The hardware trigger delay in microseconds (default to 0us)
        pulse_period_seconds : float, Optional
            The pulse period in seconds (default to 0s)
        enable_logging : bool, Optional
            Overrides spike_safe_socket.enable_logging attribute (default to None will use spike_safe_socket.enable_logging value)
        digitizer_number : int, Optional
            The Digitizer number to fetch from. If None, fetches from Digitizer 1.
        
        Returns
        -------
        digitizer_data_collection: DigitizerData[]
            Contains an array of DigitizerData objects which have a defined voltage_reading, sample_number, and time_since_start_seconds attribute

        Raises
        ------
        Exception
            On any error
        """
        try:
            # fetch the Digitizer voltage readings
            prefix = "VOLT" if digitizer_number is None else f"VOLT{digitizer_number}"
            spike_safe_socket.send_scpi_command(f'{prefix}:FETC?', enable_logging)
            digitizer_data_string = spike_safe_socket.read_data(enable_logging)
    
            # set up the DigitizerData array to be returned
            digitizer_data_collection = []

            # put the fetched data in a plottable data format
            voltage_reading_strings = digitizer_data_string.split(",")
            sample_number = 1
            for v in voltage_reading_strings:
                data_point = DigitizerData()
                data_point.voltage_reading = float(v)
                data_point.sample_number = sample_number
                data_point.time_since_start_seconds = DigitizerDataFetch.__get_sampling_mode_linear_time_since_start_seconds(time_sampling_mode, aperture_microseconds, reading_count, hardware_trigger_delay_microseconds, pulse_period_seconds, sample_number)

                digitizer_data_collection.append(data_point)
                sample_number += 1

            return digitizer_data_collection

        except Exception as err:
            # print any error to the log file and raise error to function caller
            log.error(f"Error fetching digitizer Linear sampling mode voltage data: {err}")                                     
            raise

    @staticmethod
    def fetch_voltage_data_sampling_mode_logarithmic(
        spike_safe_socket: TcpSocket,
        time_sampling_mode: TimeSamplingMode,
        sampling_mode: SamplingMode,
        hardware_trigger_delay_microseconds: int = 0,
        enable_logging: bool | None = None,
        digitizer_number: int | None = None
    ) -> list[DigitizerData]:
        """Returns an array of voltage readings using logarithmic sampling mode from the digitizer obtained through a fetch query 

        Parameters
        ----------
        spike_safe_socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        time_sampling_mode : TimeSamplingMode
            The time sampling mode to use for the voltage data. This should be an instance of the TimeSamplingMode enum from DigitizerEnums.
        sampling_mode : SamplingMode
            The sampling mode to use for the voltage data. This should be an instance of the SamplingMode enum from DigitizerEnums.
        hardware_trigger_delay_microseconds : int, Optional
            The hardware trigger delay in microseconds (default to 0us)
        enable_logging : bool, Optional
            Overrides spike_safe_socket.enable_logging attribute (default to None will use spike_safe_socket.enable_logging value)
        digitizer_number : int, Optional
            The Digitizer number to fetch from. If None, fetches from Digitizer 1.
        
        Returns
        -------
        digitizer_data_collection: DigitizerData[]
            Contains an array of DigitizerData objects which have a defined voltage_reading, sample_number, and time_since_start_seconds attribute

        Raises
        ------
        Exception
            On any error
        """
        try:
            if sampling_mode != SamplingMode.FAST_LOG and sampling_mode != SamplingMode.MEDIUM_LOG and sampling_mode != SamplingMode.SLOW_LOG:
                raise ValueError(f"{sampling_mode} sampling mode is invalid. Use sampling mode FAST_LOG, MEDIUM_LOG, or SLOW_LOG.")

            # fetch the Digitizer voltage readings
            prefix = "VOLT" if digitizer_number is None else f"VOLT{digitizer_number}"
            spike_safe_socket.send_scpi_command(f'{prefix}:FETC?', enable_logging)
            digitizer_data_string = spike_safe_socket.read_data(enable_logging)

            # set up the DigitizerData array to be returned
            digitizer_data_collection = []

            # put the fetched data in a plottable data format
            voltage_reading_strings = digitizer_data_string.split(",")
            sample_number = 1
            accumulated_time_since_start = 0
            for v in voltage_reading_strings:
                data_point = DigitizerData()
                data_point.voltage_reading = float(v)
                data_point.sample_number = sample_number
                data_point.time_since_start_seconds = DigitizerDataFetch.__get_sampling_mode_logarithmic_accumulated_time_since_start_seconds(time_sampling_mode, sampling_mode, hardware_trigger_delay_microseconds, accumulated_time_since_start, sample_number)
                digitizer_data_collection.append(data_point)

                sample_number += 1
                accumulated_time_since_start = data_point.time_since_start_seconds

            return digitizer_data_collection

        except Exception as err:
            # print any error to the log file and raise error to function caller
            log.error(f"Error fetching digitizer {sampling_mode.friendly_name()} sampling mode voltage data: {err}")                                     
            raise

    @staticmethod
    def fetch_voltage_data_sampling_mode_custom(
        spike_safe_socket: TcpSocket,
        time_sampling_mode: TimeSamplingMode,
        custom_sequence: str,
        hardware_trigger_delay_microseconds: int = 0,
        enable_logging: bool | None = None,
        digitizer_number: int | None = None
    ) -> list[DigitizerData]:
        """Returns an array of voltage readings using custom sampling mode from the digitizer obtained through a fetch query 

        Parameters
        ----------
        spike_safe_socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        time_sampling_mode : TimeSamplingMode
            The time sampling mode to use for the voltage data. This should be an instance of the TimeSamplingMode enum from DigitizerEnums.
        custom_sequence : str
            The custom sequence to use for the voltage data
        hardware_trigger_delay_microseconds : int, Optional
            The hardware trigger delay in microseconds (default to 0us)
        enable_logging : bool, Optional
            Overrides spike_safe_socket.enable_logging attribute (default to None will use spike_safe_socket.enable_logging value)
        digitizer_number : int, Optional
            The Digitizer number to fetch from. If None, fetches from Digitizer 1.
        
        Returns
        -------
        digitizer_data_collection: DigitizerData[]
            Contains an array of DigitizerData objects which have a defined voltage_reading, sample_number, and time_since_start_seconds attribute

        Raises
        ------
        Exception
            On any error
        """
        try:

            digitizer_sampling_mode_custom_sequence = DigitizerVfCustomSequence().parse_sequence(custom_sequence)

            # fetch the Digitizer voltage readings
            prefix = "VOLT" if digitizer_number is None else f"VOLT{digitizer_number}"
            spike_safe_socket.send_scpi_command(f'{prefix}:FETC?', enable_logging)
            digitizer_data_string = spike_safe_socket.read_data(enable_logging)

            # set up the DigitizerData array to be returned
            digitizer_data_collection = []

            # put the fetched data in a plottable data format
            voltage_reading_strings = digitizer_data_string.split(",")
            sample_number = 1
            accumulated_time_since_start = 0
            for v in voltage_reading_strings:
                data_point = DigitizerData()
                data_point.voltage_reading = float(v)
                data_point.sample_number = sample_number
                data_point.time_since_start_seconds = DigitizerDataFetch.__get_accumulated_custom_sample_time_since_started(time_sampling_mode, digitizer_sampling_mode_custom_sequence, hardware_trigger_delay_microseconds, accumulated_time_since_start, sample_number)
                digitizer_data_collection.append(data_point)

                sample_number += 1
                accumulated_time_since_start = data_point.time_since_start_seconds

            return digitizer_data_collection

        except Exception as err:
            # print any error to the log file and raise error to function caller
            log.error(f"Error fetching digitizer custom sampling mode voltage data: {err}")                                     
            raise

    @staticmethod
    def wait_for_new_voltage_data(
        spike_safe_socket: TcpSocket,
        wait_time: float = 0.0,
        enable_logging: bool | None = None,
        timeout: float | None = None,
        digitizer_number: int | None = None
    ) -> None:
        """Queries the SpikeSafe PSMU digitizer until it responds that it has acquired new data

        This is a useful function to call prior to sending a fetch query, because it determines whether fetched data will be freshly acquired

        Parameters
        ----------
        spike_safe_socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        wait_time: float
            Wait time in between each set of VOLT:NDAT? queries in seconds. Use get_new_voltage_data_estimated_complete_time() for the recommended value
        enable_logging : bool, Optional
            Overrides spike_safe_socket.enable_logging attribute (default to None will use spike_safe_socket.enable_logging value)
        timeout : float, Optional
            Timeout in seconds for waiting for new data. If None, wait indefinitely.
        digitizer_number : int, Optional
            The Digitizer number to fetch from. If None, fetches from Digitizer 1.
            
        Raises
        ------
        Exception
            On any error
        """
        try:
            digitizer_has_new_data = ''
            start_time = time.time()  # Record the start time
            prefix = "VOLT" if digitizer_number is None else f"VOLT{digitizer_number}"
            while True:                  
                # check for new digitizer data
                spike_safe_socket.send_scpi_command(f'{prefix}:NDAT?', enable_logging)
                digitizer_has_new_data = spike_safe_socket.read_data(enable_logging)
                if (digitizer_has_new_data == 'TRUE' or digitizer_has_new_data == 'PARTIAL'):
                    break
                elif digitizer_has_new_data == 'ERROR':
                    raise ValueError('SpikeSafe digitizer data error')
                
                if timeout is not None:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Waiting for new SpikeSafe digitizer voltage data timed out after {timeout} seconds")

                wait(wait_time)  

        except Exception as err:
            # print any error to the log file and raise error to function caller
            log.error("Error waiting for new digitizer voltage data: %s", err)
            raise

    @staticmethod
    def get_new_voltage_data_estimated_complete_time(
        aperture_microseconds: int,
        reading_count: int,
        hardware_trigger_count: int | None = None,
        hardware_trigger_delay_microseconds: int | None = None
    ) -> float:
        """
        Returns the estimated minimum possible time it will take for the SpikeSafe PSMU digitizer to acquire new voltage readings. If hardware triggering is used, this does not take into account the pulse period, so the actual time may be longer.

        Parameters
        ----------
        aperture_microseconds : int
            Aperture in microseconds
        
        reading_count : int
            Number of readings to be taken

        hardware_trigger_count : int, optional
            Number of hardware triggers to be sent
        
        hardware_trigger_delay_microseconds : int, optional
            Delay in microseconds between each hardware trigger

        Returns
        -------
        float
            Estimated fetch time in seconds

        Raises
        ------
        None

        """
        if hardware_trigger_count is None:
            hardware_trigger_count = 1  # There is always 1 software "trigger" to start the Digitizer processing new voltage data

        if hardware_trigger_delay_microseconds is None:
            hardware_trigger_delay_microseconds = 0  # Default value if not provided

        if hardware_trigger_count == 1:
            # 𝑀𝑖𝑛𝑖𝑚𝑢𝑚 𝑇𝑜𝑡𝑎𝑙 𝐴𝑐𝑞𝑢𝑖𝑠𝑖𝑡𝑖𝑜𝑛 𝑇𝑖𝑚𝑒 = 𝑇𝑟𝑖𝑔𝑔𝑒𝑟 𝐶𝑜𝑢𝑛𝑡 (𝑇𝑟𝑖𝑔𝑔𝑒𝑟 𝐷𝑒𝑙𝑎𝑦+𝐴𝑝𝑒𝑟𝑡𝑢𝑟𝑒 𝑇𝑖𝑚𝑒×𝑅𝑒𝑎𝑑𝑖𝑛𝑔 𝐶𝑜𝑢𝑛𝑡)
            estimated_complete_time_seconds = (hardware_trigger_count * (hardware_trigger_delay_microseconds + aperture_microseconds * reading_count)) / 100000
        else:
            retrigger_time_microseconds = 600
            # 𝑀𝑖𝑛𝑖𝑚𝑢𝑚 𝑇𝑜𝑡𝑎𝑙 𝐴𝑐𝑞𝑢𝑖𝑠𝑖𝑡𝑖𝑜𝑛 𝑇𝑖𝑚𝑒 = 𝑇𝑟𝑖𝑔𝑔𝑒𝑟 𝐶𝑜𝑢𝑛𝑡 (𝑇𝑟𝑖𝑔𝑔𝑒𝑟 𝐷𝑒𝑙𝑎𝑦 + Retrigger Time + 𝐴𝑝𝑒𝑟𝑡𝑢𝑟𝑒 𝑇𝑖𝑚𝑒 × 𝑅𝑒𝑎𝑑𝑖𝑛𝑔 𝐶𝑜𝑢𝑛𝑡) - Retrigger Time (ignore time last trigger)
            estimated_complete_time_seconds = (hardware_trigger_count * (hardware_trigger_delay_microseconds + retrigger_time_microseconds + aperture_microseconds * reading_count) - retrigger_time_microseconds) / 100000

        # wait time cannot be less than 0s
        estimated_complete_time_seconds = max(estimated_complete_time_seconds, 0)

        return estimated_complete_time_seconds

    @staticmethod
    def __get_sampling_mode_linear_time_since_start_seconds(time_sampling_mode, aperture_microseconds, reading_count, hardware_trigger_delay_microseconds, pulse_period_seconds, sample_number):
        time_since_start_seconds = 0
        current_trigger = (int)((sample_number - 1) / (reading_count)) + 1
        trigger_delay_seconds = hardware_trigger_delay_microseconds / 1000000.0
        aperture_seconds = aperture_microseconds / 1000000.0

        if time_sampling_mode == TimeSamplingMode.MIDDLE_OF_TIME:
            if sample_number == 1:
                time_since_start_seconds = (aperture_seconds / 2.0) + (trigger_delay_seconds * current_trigger)
            else:
                time_since_start_seconds = aperture_seconds * sample_number - aperture_seconds / 2 + (trigger_delay_seconds * current_trigger)
        elif time_sampling_mode == TimeSamplingMode.END_OF_TIME:
            time_since_start_seconds = ((sample_number - 1) * aperture_seconds) + (trigger_delay_seconds * current_trigger)

        if (sample_number > 1):
            time_since_start_seconds += (pulse_period_seconds * (current_trigger - 1))

        return round(time_since_start_seconds, 6)

    @staticmethod
    def __get_sampling_mode_logarithmic_accumulated_time_since_start_seconds(time_sampling_mode, sampling_mode, hardware_trigger_delay_microseconds, accumulated_time_since_start, sample_number):
        if sampling_mode == SamplingMode.FAST_LOG:
            aperture = DigitizerDataFetch.__get_fast_log_sample_aperture(sample_number)
            previous_aperture = DigitizerDataFetch.__get_fast_log_sample_aperture(sample_number - 1)
            new_step_first_sample_numbers = [1, 101, 181, 271, 361, 451]
            accumulated_time_since_start = DigitizerDataFetch.__get_accumulated_log_sample_time_since_started(time_sampling_mode, sample_number, accumulated_time_since_start, aperture, previous_aperture, new_step_first_sample_numbers)
        elif sampling_mode == SamplingMode.MEDIUM_LOG:
            aperture = DigitizerDataFetch.__get_medium_log_sample_aperture(sample_number)
            previous_aperture = DigitizerDataFetch.__get_medium_log_sample_aperture(sample_number - 1)
            new_step_first_sample_numbers = [1, 51, 126, 201, 276, 351, 426]
            accumulated_time_since_start = DigitizerDataFetch.__get_accumulated_log_sample_time_since_started(time_sampling_mode, sample_number, accumulated_time_since_start, aperture, previous_aperture, new_step_first_sample_numbers)
        elif sampling_mode == SamplingMode.SLOW_LOG:
            aperture = DigitizerDataFetch.__get_slow_log_sample_aperture(sample_number)
            previous_aperture = DigitizerDataFetch.__get_slow_log_sample_aperture(sample_number - 1)
            new_step_first_sample_numbers = [1, 51, 141, 231, 321, 366, 411, 456]
            accumulated_time_since_start = DigitizerDataFetch.__get_accumulated_log_sample_time_since_started(time_sampling_mode, sample_number, accumulated_time_since_start, aperture, previous_aperture, new_step_first_sample_numbers)

        if sample_number == 1:
            trigger_delay_seconds = hardware_trigger_delay_microseconds / 1000000.0
            accumulated_time_since_start += trigger_delay_seconds 

        return round(accumulated_time_since_start, 6)

    @staticmethod
    def __get_fast_log_sample_aperture(sample_number):
        if sample_number <= 100:
            return 0.0000020
        elif sample_number <= 180:
            return 0.000010
        elif sample_number <= 270:
            return 0.00010
        elif sample_number <= 360:
            return 0.0010
        elif sample_number <= 450:
            return 0.010
        elif sample_number <= 525:
            return 0.10
        else:
            return 0

    @staticmethod
    def __get_medium_log_sample_aperture(sample_number):
        if sample_number <= 50:
            return 0.0000020
        elif sample_number <= 125:
            return 0.0000120
        elif sample_number <= 200:
            return 0.000120
        elif sample_number <= 275:
            return 0.00120
        elif sample_number <= 350:
            return 0.0120
        elif sample_number <= 425:
            return 0.120
        elif sample_number <= 500:
            return 1.20
        else:
            return 0

    @staticmethod
    def __get_slow_log_sample_aperture(sample_number):
        if sample_number <= 50:
            return 0.0000020
        elif sample_number <= 140:
            return 0.000010
        elif sample_number <= 230:
            return 0.00010
        elif sample_number <= 320:
            return 0.0010
        elif sample_number <= 365:
            return 0.020
        elif sample_number <= 410:
            return 0.20
        elif sample_number <= 455:
            return 2.0
        elif sample_number <= 500:
            return 20.0
        else:
            return 0

    @staticmethod
    def __get_accumulated_log_sample_time_since_started(time_sampling_mode, sample_number, accumulated_time_since_start, aperture, previous_aperture, new_step_first_sample_numbers):
        is_first_sample_in_step = sample_number in new_step_first_sample_numbers

        return DigitizerDataFetch.__calculate_accumulated_time_of_sampling_time(
            time_sampling_mode,
            sample_number, 
            accumulated_time_since_start, 
            aperture, 
            previous_aperture, 
            is_first_sample_in_step
        )

    @staticmethod
    def __get_accumulated_custom_sample_time_since_started(time_sampling_mode, digitizer_sampling_mode_custom_sequence, hardware_trigger_delay_microseconds, accumulated_time_since_start, sample_number):
        aperture = digitizer_sampling_mode_custom_sequence.get_aperture_for_sample_number_in_seconds(sample_number)
        previous_aperture = digitizer_sampling_mode_custom_sequence.get_aperture_for_sample_number_in_seconds(sample_number - 1) if sample_number > 1 else 0
        is_first_sample_in_step = digitizer_sampling_mode_custom_sequence.is_first_sample_in_step(sample_number)

        accumulated_time_since_start = DigitizerDataFetch.__calculate_accumulated_time_of_sampling_time(time_sampling_mode, sample_number, accumulated_time_since_start, aperture, previous_aperture, is_first_sample_in_step)

        if sample_number == 1:
            trigger_delay_seconds = hardware_trigger_delay_microseconds / 1000000.0
            accumulated_time_since_start += trigger_delay_seconds 

        return round(accumulated_time_since_start, 6)

    @staticmethod
    def __calculate_accumulated_time_of_sampling_time(time_sampling_mode, sample_number, accumulated_time_since_start, aperture, previous_aperture, is_first_sample_in_step):
        if time_sampling_mode == TimeSamplingMode.MIDDLE_OF_TIME:
            if sample_number == 1:
                # Reset summed time since start on new fetch
                return aperture / 2
            elif is_first_sample_in_step:
                # Reset sample time on first sample of new step
                return accumulated_time_since_start + previous_aperture / 2 + aperture / 2
            else:
                # Regular sample
                return accumulated_time_since_start + aperture
        elif time_sampling_mode == TimeSamplingMode.END_OF_TIME:
            if sample_number == 1:
                # Reset summed time since start on new fetch
                return aperture
            else:
                # Regular sample
                return accumulated_time_since_start + aperture
            

def fetch_voltage_data(
    spike_safe_socket: TcpSocket,
    enable_logging: bool | None = None,
    digitizer_number: int | None = None
) -> list[DigitizerData]:
    """
    Obsolete: Use DigitizerDataFetch.fetch_voltage_data() instead.
    """
    return DigitizerDataFetch.fetch_voltage_data(spike_safe_socket, enable_logging, digitizer_number=digitizer_number)

def fetch_voltage_data_sampling_mode_linear(
    spike_safe_socket: TcpSocket,
    time_sampling_mode: TimeSamplingMode,
    aperture_microseconds: int,
    reading_count: int,
    hardware_trigger_delay_microseconds: int = 0,
    pulse_period_seconds: float = 0.0,
    enable_logging: bool | None = None,
    digitizer_number: int | None = None
) -> list[DigitizerData]:
    """
    Obsolete: Use DigitizerDataFetch.fetch_voltage_data_sampling_mode_linear() instead.
    """
    return DigitizerDataFetch.fetch_voltage_data_sampling_mode_linear(spike_safe_socket, time_sampling_mode, aperture_microseconds, reading_count, hardware_trigger_delay_microseconds, pulse_period_seconds, enable_logging, digitizer_number=digitizer_number)

def fetch_voltage_data_sampling_mode_logarithmic(
    spike_safe_socket: TcpSocket,
    time_sampling_mode: TimeSamplingMode,
    sampling_mode: SamplingMode,
    hardware_trigger_delay_microseconds: int = 0,
    enable_logging: bool | None = None,
    digitizer_number: int | None = None
) -> list[DigitizerData]:
    """
    Obsolete: Use DigitizerDataFetch.fetch_voltage_data_sampling_mode_logarithmic() instead.
    """
    return DigitizerDataFetch.fetch_voltage_data_sampling_mode_logarithmic(spike_safe_socket, time_sampling_mode, sampling_mode, hardware_trigger_delay_microseconds, enable_logging, digitizer_number=digitizer_number)

def fetch_voltage_data_sampling_mode_custom(
    spike_safe_socket: TcpSocket,
    time_sampling_mode: TimeSamplingMode,
    custom_sequence: DigitizerVfCustomSequence,
    hardware_trigger_delay_microseconds: int = 0,
    enable_logging: bool | None = None,
    digitizer_number: int | None = None
) -> list[DigitizerData]:
    """
    Obsolete: Use DigitizerDataFetch.fetch_voltage_data_sampling_mode_custom() instead.
    """
    return DigitizerDataFetch.fetch_voltage_data_sampling_mode_custom(spike_safe_socket, time_sampling_mode, custom_sequence, hardware_trigger_delay_microseconds, enable_logging, digitizer_number=digitizer_number)

def get_new_voltage_data_estimated_complete_time(
    aperture_microseconds: int,
    reading_count: int,
    hardware_trigger_count: int | None = None,
    hardware_trigger_delay_microseconds: int | None = None
) -> float:
    """
    Obsolete: Use DigitizerDataFetch.get_new_voltage_data_estimated_complete_time() instead.
    """
    return DigitizerDataFetch.get_new_voltage_data_estimated_complete_time(aperture_microseconds, reading_count, hardware_trigger_count, hardware_trigger_delay_microseconds)

def wait_for_new_voltage_data(
    spike_safe_socket: TcpSocket,
    wait_time: float = 0.0,
    enable_logging: bool | None = None,
    timeout: float | None = None,
    digitizer_number: int | None = None
) -> None:
    """
    Obsolete: Use DigitizerDataFetch.wait_for_new_voltage_data() instead.
    """
    return DigitizerDataFetch.wait_for_new_voltage_data(spike_safe_socket, wait_time, enable_logging, timeout, digitizer_number=digitizer_number)