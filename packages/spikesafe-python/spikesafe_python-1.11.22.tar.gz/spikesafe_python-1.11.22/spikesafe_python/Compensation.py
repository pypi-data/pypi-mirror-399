import json
import jsonschema
from jsonschema import validate
import logging
import os
from .SpikeSafeEnums import LoadImpedance, RiseTime

log = logging.getLogger(__name__)

class Compensation:
    """
    Provides a collection of helper functions you can use to help with SpikeSafe compensation settings.
    
    Attributes
    ----------
    custom_compensation_table_schema : dict
        JSON schema to validate a custom compensation table
    
    Methods
    -------
    get_optimum_compensation(spikesafe_model_max_current_amps: float, set_current_amps: float, pulse_on_time_seconds: float | None = None, enable_logging: bool = False) -> tuple[LoadImpedance, RiseTime]
        Returns the optimum compensation for a given set current, and optionally a given pulse on time.
    get_custom_compensation(spikesafe_model_max_current_amps: float, set_current_amps: float, device_type: str, custom_compensation_table: list[dict], pulse_on_time_seconds: float | None = None, enable_logging: bool = False) -> tuple[LoadImpedance, RiseTime]
        Returns the custom compensation for a given set current, device type, and custom compensation table, and optionally a given pulse on time.
    load_custom_compensation_table(file_path: str) -> list[dict]
        Loads a custom compensation table from a file path.
    load_custom_compensation_unique_device_types(custom_compensation_table: list[dict]) -> list[str]
        Returns a list of unique device types in a custom compensation table.
    """

    # Dictionary string constants
    low_current_range_maximum = 'low_current_range_maximum'
    load_impedance_high_range_1 = 'load_impedance_high_range_1'
    rise_time_high_range_1 = 'rise_time_high_range_1'
    load_impedance_high_range_2 = 'load_impedance_high_range_2'
    rise_time_high_range_2 = 'rise_time_high_range_2'
    load_impedance_high_range_3 = 'load_impedance_high_range_3'
    rise_time_high_range_3 = 'rise_time_high_range_3'
    load_impedance_low_range_1 = 'load_impedance_low_range_1'
    rise_time_low_range_1 = 'rise_time_low_range_1'
    load_impedance_low_range_2 = 'load_impedance_low_range_2'
    rise_time_low_range_2 = 'rise_time_low_range_2'

    @staticmethod
    def get_optimum_compensation(
        spikesafe_model_max_current_amps: float,
        set_current_amps: float,
        pulse_on_time_seconds: float | None = None,
        enable_logging: bool = False
    ) -> tuple[LoadImpedance, RiseTime]:
        """
        Returns the optimum compensation for a given set current, and optionally a given pulse on time

        Parameters
        ----------
        spikesafe_model_max_current_amps : float
            Maximum current of the SpikeSafe model
        set_current_amps : float
            Current to be set on SpikeSafe
        pulse_on_time_seconds : float, optional
            Pulse On Time to be set on SpikeSafe
        enable_logging : bool, optional
            Enables logging (default is False)
        
        Returns
        -------
        LoadImpedance
            Load Impedance compensation value. This should be an instance of the LoadImpedance IntEnum from SpikeSafeEnums.
        RiseTime
            Rise Time compensation value. This should be an instance of the RiseTime IntEnum from SpikeSafeEnums.

        Remarks
        -------
        This function assumes the set current is operating on the optimized current range. If operating on the high range with a set current normally programmed on the low range, the compensation values will not be optimal. See online specification for range limits.

        If Load Impedance is returned as Medium or High, it is best practice to increase the Compliance Voltage setting by 5V to 30V. This helps the current amplifier to overcome inductance. If Compliance Voltage is not increased, then a Low Side Over Current or an Unstable Waveform error may occur.

        If an Operating Mode is used to sweep through steps of currents where the compensation settings are the same across the sweep, such as Pulse Sweep or Multiple Pulse Burst, it is recommended use the optimum compensation settings targeting the Stop Current.

        Raises
        ------
        ValueError
            If set_current_amps is greater than spikesafe_model_max_current_amps
        """

        if set_current_amps > spikesafe_model_max_current_amps:
            raise ValueError(f'Measurement current {set_current_amps}A exceeds SpikeSafe model maximum current capability of {spikesafe_model_max_current_amps}A.')

        # Non-pulsing, or DC based modes, do not require compensation
        if pulse_on_time_seconds is None:
            if enable_logging:
                log.warning("DC based modes do not require compensation, defaulting to LoadImpedance.VERY_LOW and RiseTime.VERY_SLOW")
            return LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW

        # Optimum compensation is intended for Pulse On Time of 500us or less
        optimum_compensation_minimum_pulse_on_time_seconds = 0.0005
        if pulse_on_time_seconds is not None and pulse_on_time_seconds > optimum_compensation_minimum_pulse_on_time_seconds:
            if enable_logging:
                log.warning(f"Compensation is intended for Pulse On Time of {optimum_compensation_minimum_pulse_on_time_seconds}s or less, defaulting to LoadImpedance.VERY_LOW and RiseTime.VERY_SLOW")
            return LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW

        # Dictionary to store values for different model max currents
        model_params = {
            0.05: {
                Compensation.low_current_range_maximum: 0.004,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.MEDIUM,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.VERY_LOW, Compensation.rise_time_high_range_3: RiseTime.SLOW,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            0.5: {
                Compensation.low_current_range_maximum: 0.04,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            2: {
                Compensation.low_current_range_maximum: 0.2,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            3: {
                Compensation.low_current_range_maximum: 0.2,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            4: {
                Compensation.low_current_range_maximum: 0.2,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            5: {
                Compensation.low_current_range_maximum: 0.2,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            8: {
                Compensation.low_current_range_maximum: 0.4,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            # Tested for Mini 10A, but will also be used for PSMU HC 10A
            10: {
                Compensation.low_current_range_maximum: 0.4,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            16: {
                Compensation.low_current_range_maximum: 0.8,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            20: {
                Compensation.low_current_range_maximum: 0.8,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            32: {
                Compensation.low_current_range_maximum: 1.6,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            40: {
                Compensation.low_current_range_maximum: 1.6,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            60: {
                Compensation.low_current_range_maximum: 3.2,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            },
            80: {
                Compensation.low_current_range_maximum: 3.2,
                Compensation.load_impedance_high_range_1: LoadImpedance.MEDIUM, Compensation.rise_time_high_range_1: RiseTime.FAST,
                Compensation.load_impedance_high_range_2: LoadImpedance.LOW, Compensation.rise_time_high_range_2: RiseTime.FAST,
                Compensation.load_impedance_high_range_3: LoadImpedance.LOW, Compensation.rise_time_high_range_3: RiseTime.MEDIUM,
                Compensation.load_impedance_low_range_1: LoadImpedance.HIGH, Compensation.rise_time_low_range_1: RiseTime.FAST,
                Compensation.load_impedance_low_range_2: LoadImpedance.MEDIUM, Compensation.rise_time_low_range_2: RiseTime.FAST
            }
        }

        if spikesafe_model_max_current_amps not in model_params:
            if enable_logging:
                log.warning(f"{spikesafe_model_max_current_amps}A SpikeSafe Model not defined for optimum compensation, defaulting to LoadImpedance.MEDIUM and RiseTime.FAST")
            return LoadImpedance.MEDIUM, RiseTime.FAST

        model_params_current = model_params[spikesafe_model_max_current_amps]

        if Compensation.__is_high_range__(set_current_amps, model_params_current):
            load_impedance, rise_time = Compensation.__use_high_range_compensation__(spikesafe_model_max_current_amps, set_current_amps, model_params_current)
        else:
            load_impedance, rise_time = Compensation.__use_low_range_compensation__(set_current_amps, model_params_current)

        if enable_logging:
            log.info(f"Optimum compensation for {set_current_amps}A on {spikesafe_model_max_current_amps}A SpikeSafe model is LoadImpedance.{load_impedance} and RiseTime.{rise_time}.")
        return load_impedance, rise_time

    @staticmethod
    def get_custom_compensation(
        spikesafe_model_max_current_amps: float,
        set_current_amps: float,
        device_type: str,
        custom_compensation_table: list[dict],
        pulse_on_time_seconds: float | None = None,
        enable_logging: bool = False
    ) -> tuple[LoadImpedance, RiseTime]:
        """
        Returns the custom compensation values for a given set_current_amps and device_type based on a custom_compensation_table, and optionally a given pulse on time

        Parameters
        ----------
        spikesafe_model_max_current_amps : float
            Maximum current of the SpikeSafe model
        set_current_amps : float
            Current to be set on SpikeSafe
        device_type : str
            Device type of the DUT
        custom_compensation_table : list
            Custom compensation table to be used for compensation. This should be the result of calling the load_custom_compensation_table(file_path) function conforming to the custom_compensation_table_schema.
        pulse_on_time_seconds : float, optional
            Pulse On Time to be set on SpikeSafe (default is None)
        enable_logging : bool, optional
            Enables logging (default is False)

        Returns
        -------
        LoadImpedance
            Load Impedance compensation value. This should be an instance of the LoadImpedance IntEnum from SpikeSafeEnums.
        RiseTime
            Rise Time compensation value. This should be an instance of the RiseTime IntEnum from SpikeSafeEnums.

        Raises
        ------
        ValueError
            If set_current_amps is greater than spikesafe_model_max_current_amps
        """
        # Validate the custom_compensation_table against the JSON schema
        try:
            validate(instance=custom_compensation_table, schema=Compensation.custom_compensation_table_schema)
        except Exception:
            raise Exception("Invalid Custom Compensation Table format. Please ensure 'custom_compensation_table' is correctly instantiated by calling 'load_custom_compensation_table(file_path)'.")

        # Check if the set_current_amps exceeds the model's max current capability
        if set_current_amps > spikesafe_model_max_current_amps:
            raise ValueError(f'Measurement current {set_current_amps}A exceeds SpikeSafe model maximum current capability of {spikesafe_model_max_current_amps}A.')

        # Non-pulsing or DC-based modes do not require compensation
        if pulse_on_time_seconds is None or pulse_on_time_seconds > 0.0005:
            return LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW

        # Preprocess the custom compensation table into a dictionary
        compensation_dict = Compensation.__preprocess_compensation_table(custom_compensation_table)

        # Find the default entry
        default_load_impedance = None
        default_rise_time = None

        if (spikesafe_model_max_current_amps, device_type) in compensation_dict:
            for entry in compensation_dict[(spikesafe_model_max_current_amps, device_type)]:
                if entry.get('is_default', True):
                    default_load_impedance = entry['load_impedance']
                    default_rise_time = entry['rise_time']
                    break  # Once default is found, stop the search

        # Raise an error if no default entry was found
        if default_load_impedance is None or default_rise_time is None:
            raise ValueError(f'No default entry specified for spikesafe_model_max_current_amps {spikesafe_model_max_current_amps}A {device_type}. Please specify a default entry.')

        # Find the target entry based on set_current_amps range
        target_load_impedance = default_load_impedance  # Start with default values
        target_rise_time = default_rise_time

        for entry in compensation_dict.get((spikesafe_model_max_current_amps, device_type), []):
            # Check if set_current_amps is within the start and end range
            if (set_current_amps >= entry['set_current_amps_start_range'] and set_current_amps < entry['set_current_amps_end_range']) or set_current_amps == entry['spikesafe_model_max_current_amps']:
                target_load_impedance = entry['load_impedance']
                target_rise_time = entry['rise_time']
                break  # Exit the loop once the first match is found

        # Use the target entry if found, otherwise return the default entry
        # Convert from string to IntEnum before returning
        if enable_logging:
            log.info(f"Custom compensation for {set_current_amps}A on {spikesafe_model_max_current_amps}A SpikeSafe model and device type '{device_type}' is LoadImpedance.{target_load_impedance} and RiseTime.{target_rise_time}.")
        return LoadImpedance[target_load_impedance], RiseTime[target_rise_time]

    @staticmethod
    def load_custom_compensation_table(file_path: str) -> list[dict]:
        """
        Returns a custom compensation table from a JSON file

        Parameters
        ----------
        file_path : str
            Path to the JSON file containing the custom compensation table
        
        Returns
        -------
        list
            Custom compensation table as a list of dictionaries conforming to the custom_compensation_table_schema
        
        Raises
        ------
        FileNotFoundError
            If the file does not exist
        IOError
            If an error occurs while loading the file
        ValueError
            If the file contains invalid JSON, schema validation error, or custom compensation table validation error
        """
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try to load the file and parse the JSON
        try:
            with open(file_path, 'r') as file:
                custom_compensation_table = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Custom Compensation Table file contains invalid JSON: {str(e)}")
        except Exception as e:
            raise IOError(f"An error occurred while loading the Custom Compensation Table file: {str(e)}")

        # Validate the JSON against the schema
        try:        
            validate(instance=custom_compensation_table, schema=Compensation.custom_compensation_table_schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Custom Compensation Table file schema validation error: {e.message} in element {list(e.path)}")
        except jsonschema.SchemaError as e:
            raise ValueError(f"Custom Compensation Table file schema definition error: {e.message}")

        Compensation.__validate_custom_compensation_table(custom_compensation_table)
        
        return custom_compensation_table

    @staticmethod
    def load_custom_compensation_unique_device_types(custom_compensation_table: list[dict]) -> list[str]:
        """
        Returns the unique device types from a custom compensation table

        Parameters
        ----------
        custom_compensation_table : list
            Custom compensation table to be used for compensation. This should be the result of calling the load_custom_compensation_table(file_path) function conforming to the custom_compensation_table_schema

        Returns
        -------
        list
            List of unique device types in the custom compensation table
        """
        device_types = {entry['device_type'] for entry in custom_compensation_table}
        return list(device_types)

    # Helper function to determine if high current range should be used
    @staticmethod
    def __is_high_range__(set_current_amps, model_params_current):
        if set_current_amps > model_params_current[Compensation.low_current_range_maximum]:
            return True
        else:
            return False

    # Helper function to use high current range compensation settings
    @staticmethod
    def __use_high_range_compensation__(spikesafe_model_max_current_amps, set_current_amps, model_params_current):
        range_ratio = set_current_amps / spikesafe_model_max_current_amps
        if range_ratio < 0.5:
            return model_params_current[Compensation.load_impedance_high_range_1], model_params_current[Compensation.rise_time_high_range_1]
        elif range_ratio < 0.7:
            return model_params_current[Compensation.load_impedance_high_range_2], model_params_current[Compensation.rise_time_high_range_2]
        else:
            return model_params_current[Compensation.load_impedance_high_range_3], model_params_current[Compensation.rise_time_high_range_3]

    # Helper function to use low current range compensation settings
    @staticmethod
    def __use_low_range_compensation__(set_current_amps, model_params_current):
        range_ratio = set_current_amps / model_params_current[Compensation.low_current_range_maximum]
        if range_ratio < 0.7:
            return model_params_current[Compensation.load_impedance_low_range_1], model_params_current[Compensation.rise_time_low_range_1]
        else:
            return model_params_current[Compensation.load_impedance_low_range_2], model_params_current[Compensation.rise_time_low_range_2]

    # Define the schema for validation
    custom_compensation_table_schema = {
        "type": "array",
        "minItems": 1,
        "items": {
            "type": "object",
            "properties": {
                "spikesafe_model_max_current_amps": {
                    "type": "number",
                    "minimum": 0
                },
                "device_type": {"type": "string"},
                "is_default": {"type": "boolean"},
                "set_current_amps_start_range": {
                    "type": "number",
                    "minimum": 0
                },
                "set_current_amps_end_range": {
                    "type": "number",
                    "minimum": 0
                },
                "load_impedance": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW", "VERY_LOW"]
                },
                "rise_time": {
                    "type": "string",
                    "enum": ["FAST", "MEDIUM", "LOW", "VERY_SLOW"]
                },
            },
            "required": [
                "spikesafe_model_max_current_amps", 
                "device_type", 
                "is_default", 
                "set_current_amps_start_range", 
                "set_current_amps_end_range", 
                "load_impedance", 
                "rise_time"
            ]
        }
    }

    @staticmethod
    def __preprocess_compensation_table(custom_compensation_table):
        compensation_dict = {}
        for entry in custom_compensation_table:
            key = (entry['spikesafe_model_max_current_amps'], entry['device_type'])
            if key not in compensation_dict:
                compensation_dict[key] = []
            compensation_dict[key].append(entry)
        return compensation_dict

    @staticmethod
    def __validate_custom_compensation_table(custom_compensation_table):
        # Group entries by unique combination of "spikesafe_model_max_current_amps" and "device_type"
        # e.g. (5.0, "laser_green"): [
        #        (0, { "spikesafe_model_max_current_amps": 5.0, "device_type": "laser_green" ... }),
        #        (1, { "spikesafe_model_max_current_amps": 5.0, "device_type": "laser_green" ... }),
        #        ...],
        grouped_entries = {}

        # Perform validations on each element
        for index, entry in enumerate(custom_compensation_table):
            Compensation.__validate_element_set_current_ranges(entry, index)

            # Group by max current and device type
            combination_key = (entry["spikesafe_model_max_current_amps"], entry["device_type"])

            # Check if the combination_key already exists in grouped_entries
            if combination_key not in grouped_entries:
                grouped_entries[combination_key] = []  # Initialize with an empty list if it does not exist

            # Append the current index and entry to the list for this combination_key
            grouped_entries[combination_key].append((index, entry))

        # Perform validations on each group
        for (spikesafe_model_max_current_amps, device_type), entries in grouped_entries.items():
            Compensation.__validate_group_has_is_default(entries, spikesafe_model_max_current_amps, device_type)
            Compensation.__validate_group_set_current_ranges(entries, spikesafe_model_max_current_amps, device_type)

    @staticmethod
    def __validate_element_set_current_ranges(entry, index):
        # Validation Rule: Validate that set_current_amps_start_range is less than or equal to set_current_amps_end_range
        if entry['set_current_amps_start_range'] > entry['set_current_amps_end_range']:
            raise ValueError(
                f"'set_current_amps_start_range' ({entry['set_current_amps_start_range']}) cannot be greater than "
                f"'set_current_amps_end_range' ({entry['set_current_amps_end_range']}) in element [{index}]"
            )

    @staticmethod
    def __validate_group_has_is_default(entries, spikesafe_model_max_current_amps, device_type):
        # Validation Rule: Ensure each group has exactly one "is_default" set to True
        
        # Initialize a list to store entries with "is_default" set to True
        defaults = []

        # Iterate through each entry to check for the "is_default" flag
        for index, entry in entries:  # entry is a tuple (index, entry)
            if entry['is_default']:  # Access the dictionary part of the tuple
                defaults.append(entry)  # Append the dictionary to defaults

        num_defaults = len(defaults)
        
        if num_defaults == 0:
            raise ValueError(f"No 'is_default' true entry found for combination: "
                            f"'spikesafe_model_max_current_amps' {spikesafe_model_max_current_amps}, 'device_type' {device_type}")
        
        if num_defaults > 1:
            raise ValueError(f"Multiple 'is_default' true entries found for combination: "
                            f"'spikesafe_model_max_current_amps' {spikesafe_model_max_current_amps}, 'device_type' {device_type}")

    @staticmethod
    def __validate_group_set_current_ranges(entries, spikesafe_model_max_current_amps, device_type):
        # Validation Rule: Ensure that the ranges do not overlap
        # Sort entries by set_current_amps_start_range to validate range continuity
        sorted_entries = sorted(entries, key=lambda x: x[1]['set_current_amps_start_range'])

        for i in range(1, len(sorted_entries)):
            prev_index, prev_entry = sorted_entries[i - 1]
            current_index, current_entry = sorted_entries[i]

            # Check if the previous end range is greater than the current start range (overlap)
            if prev_entry['set_current_amps_end_range'] > current_entry['set_current_amps_start_range']:
                raise ValueError(
                    f"Set Current Range Overlap detected: 'set_current_amps_start_range' ({current_entry['set_current_amps_start_range']}) "
                    f"overlaps with element {prev_index} 'set_current_amps_end_range' ({prev_entry['set_current_amps_end_range']}) "
                    f"in element [{current_index}] for device_type: {device_type}, max current: {spikesafe_model_max_current_amps}"
                )

            # Optionally, check for gaps in the range
            # if prev_entry['set_current_amps_end_range'] < current_entry['set_current_amps_start_range']:
            #     print(f"Warning: Gap detected between element {prev_index} end range ({prev_entry['set_current_amps_end_range']}) "
            #           f"and element {current_index} start range ({current_entry['set_current_amps_start_range']}) "
            #           f"for device_type: {device_type}, max current: {max_current}")


def get_optimum_compensation(
    spikesafe_model_max_current_amps: float,
    set_current_amps: float,
    pulse_on_time_seconds: float | None = None,
    enable_logging: bool = False
) -> tuple[LoadImpedance, RiseTime]:
    """
    Obsolete: Use Compensation.get_optimum_compensation() instead.
    """
    return Compensation.get_optimum_compensation(spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds, enable_logging)

def get_custom_compensation(
    spikesafe_model_max_current_amps: float,
    set_current_amps: float,
    device_type: str,
    custom_compensation_table: list[dict],
    pulse_on_time_seconds: float | None = None,
    enable_logging: bool = False
) -> tuple[LoadImpedance, RiseTime]:
    """
    Obsolete: Use Compensation.get_custom_compensation() instead.
    """
    return Compensation.get_custom_compensation(spikesafe_model_max_current_amps, set_current_amps, device_type, custom_compensation_table, pulse_on_time_seconds, enable_logging)

def load_custom_compensation_table(file_path: str) -> list[dict]:
    """
    Obsolete: Use Compensation.load_custom_compensation_table() instead.
    """
    return Compensation.load_custom_compensation_table(file_path)

def load_custom_compensation_unique_device_types(custom_compensation_table: list[dict]) -> list[str]:
    """
    Obsolete: Use Compensation.load_custom_compensation_unique_device_types() instead.
    """
    return Compensation.load_custom_compensation_unique_device_types(custom_compensation_table)