import pytest
import os
import json
from spikesafe_python.Compensation import get_custom_compensation, load_custom_compensation_table
from spikesafe_python.SpikeSafeEnums import LoadImpedance, RiseTime

# This tests the function calls from get_custom_compensation.py

# Define a fixture to load the table
@pytest.fixture
def table():
    # Load or construct your table here
    return load_custom_compensation_table(os.path.join(os.path.dirname(__file__), 'test_compensation_files', 'valid.json'))

@pytest.mark.parametrize("file_path, expected_error_message", [
    ('error_blank.json', "Custom Compensation Table file contains invalid JSON: Expecting value: line 1 column 1 (char 0)"),
    ('error_empty_array.json', "Custom Compensation Table file schema validation error: [] should be non-empty in element []"),
    ('error_group_is_default_missing.json', "No 'is_default' true entry found for combination: 'spikesafe_model_max_current_amps' 0.5, 'device_type' laser_green"),
    ('error_group_set_current_range_overlap.json', "Set Current Range Overlap detected:"),
    ('error_invalid_json.json', "Custom Compensation Table file contains invalid JSON: Expecting ',' delimiter: line 3 column 1 (char 219)"),
    ('error_invalid_spikesafe_model_max_current_amps_minimum_value.json', "Custom Compensation Table file schema validation error: -1 is less than the minimum of 0 in element [0, 'spikesafe_model_max_current_amps']"),
    ('error_schema_incomplete.json', "Custom Compensation Table file schema validation error: 'device_type' is a required property in element [0]"),
    ('error_set_current_start_range_greater_than_end_range.json', "set_current_amps_start_range' (0.51) cannot be greater than 'set_current_amps_end_range' (0.5) in element [0]")
])
def test_load_custom_compensation_table_error(file_path, expected_error_message):
    with pytest.raises(ValueError) as exc_info:
        load_custom_compensation_table(os.path.join(os.path.dirname(__file__), 'test_compensation_files', file_path))

@pytest.mark.parametrize("custom_compensation_table, expected_error_message", [
    ([], "Invalid Custom Compensation Table format. Please ensure 'custom_compensation_table' is correctly instantiated by calling 'load_custom_compensation_table(file_path)'."),
    (None, "Invalid Custom Compensation Table format. Please ensure 'custom_compensation_table' is correctly instantiated by calling 'load_custom_compensation_table(file_path)'.")
])
def test_get_custom_compensation_table_exceptions(custom_compensation_table, expected_error_message):
    with pytest.raises(Exception) as exc_info:
        get_custom_compensation(0.5, 0.6, 'laser_green', custom_compensation_table, 0.0001)
    assert expected_error_message in str(exc_info.value)

@pytest.mark.parametrize("spikesafe_model_max_current, measurement_current, device_type, expected_error_message", [
    (0.5, 0.6, 'laser_green', "Measurement current 0.6A exceeds SpikeSafe model maximum current capability of 0.5A."),
    (0.5, 0.1, 'laser_red', "No default entry specified for spikesafe_model_max_current_amps 0.5A laser_red. Please specify a default entry."),
    (10, 0.1, 'laser_green', "No default entry specified for spikesafe_model_max_current_amps 10A laser_green. Please specify a default entry.")
])
def test_get_custom_compensation_current_value_errors(spikesafe_model_max_current, measurement_current, device_type, expected_error_message, table):
    with pytest.raises(ValueError) as exc_info:
        get_custom_compensation(spikesafe_model_max_current, measurement_current, device_type, table, 0.0001)
    assert expected_error_message in str(exc_info.value)

@pytest.mark.parametrize("spikesafe_model_max_current, measurement_current, device_type, expected_load_impedance, expected_rise_time", [
    (5, 0.126, 'laser_green', LoadImpedance.HIGH, RiseTime.FAST),  # Upper 1/3 of range
    (5, 0.1, 'laser_green', LoadImpedance.MEDIUM, RiseTime.MEDIUM),  # Middle 1/3 of range
    (5, 0.005, 'laser_green', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW),  # Lower 1/3 of range
])
def test_get_custom_compensation_range(spikesafe_model_max_current, measurement_current, device_type, expected_load_impedance, expected_rise_time, table):
    load_impedance, rise_time = get_custom_compensation(spikesafe_model_max_current, measurement_current, device_type, table, 0.0005)
    assert load_impedance == expected_load_impedance
    assert rise_time == expected_rise_time

@pytest.mark.parametrize("spikesafe_model_max_current, measurement_current, device_type, pulse_on_time_seconds, expected_load_impedance, expected_rise_time", [
    (0.5, 0.1, 'laser_green', 0.0005, LoadImpedance.MEDIUM, RiseTime.MEDIUM),  # Small pulse under 500us that requires optimum compensation
    (0.5, 0.1, 'laser_green', 0.00051, LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW),  # Large pulse over 500us that does not require compensation
    (100, 0, 'laser_green', None, LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW),  # DC mode that does not require compensation (pulse_on_time_seconds=None)
])
def test_get_custom_compensation_pulse_on_time_seconds(spikesafe_model_max_current, measurement_current, device_type, pulse_on_time_seconds, expected_load_impedance, expected_rise_time, table):
    load_impedance, rise_time = get_custom_compensation(spikesafe_model_max_current, measurement_current, device_type, table, pulse_on_time_seconds)
    assert load_impedance == expected_load_impedance
    assert rise_time == expected_rise_time