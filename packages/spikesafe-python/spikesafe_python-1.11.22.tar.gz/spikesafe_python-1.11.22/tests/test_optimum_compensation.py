import pytest
import spikesafe_python

@pytest.mark.parametrize("spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds, expected_load_impedance, expected_rise_time", [
    (0.5, 0.6, None, None, None),  # set_current_amps > spikesafe_model_max_current_amps
    (0.5, 0.1, None, spikesafe_python.SpikeSafeEnums.LoadImpedance.VERY_LOW, spikesafe_python.SpikeSafeEnums.RiseTime.VERY_SLOW),  # DC mode
    (0.5, 0.1, 0.0006, spikesafe_python.SpikeSafeEnums.LoadImpedance.VERY_LOW, spikesafe_python.SpikeSafeEnums.RiseTime.VERY_SLOW),  # Pulse on time > 500us
    (0.5, 0.1, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # Valid case within range
    (10, 0.1, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # Valid case within range
    (10, 0.5, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # Valid case within range
    (10, 5, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # Valid case within range
])
def test_get_optimum_compensation(spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds, expected_load_impedance, expected_rise_time):
    if expected_load_impedance is None and expected_rise_time is None:
        with pytest.raises(ValueError):
            spikesafe_python.Compensation.get_optimum_compensation(spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds)
    else:
        load_impedance, rise_time = spikesafe_python.Compensation.get_optimum_compensation(spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds)
        assert load_impedance == expected_load_impedance
        assert rise_time == expected_rise_time

@pytest.mark.parametrize("spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds, expected_load_impedance, expected_rise_time", [
    (0.05, 0.003, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # Low current range
    (0.05, 0.005, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.MEDIUM),  # High current range
    (0.5, 0.03, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # Low current range
    (0.5, 0.05, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # High current range
    (2, 0.1, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # Low current range
    (2, 1, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.LOW, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # High current range
])
def test_get_optimum_compensation_ranges(spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds, expected_load_impedance, expected_rise_time):
    load_impedance, rise_time = spikesafe_python.Compensation.get_optimum_compensation(spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds)
    assert load_impedance == expected_load_impedance
    assert rise_time == expected_rise_time

@pytest.mark.parametrize("spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds, expected_load_impedance, expected_rise_time", [
    (100, 0, None, spikesafe_python.SpikeSafeEnums.LoadImpedance.VERY_LOW, spikesafe_python.SpikeSafeEnums.RiseTime.VERY_SLOW),  # DC mode with unsupported spikesafe_model_max_current_amps
    (100, 0, 0.0004, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.FAST),  # Unsupported spikesafe_model_max_current_amps
])
def test_get_optimum_compensation_edge_cases(spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds, expected_load_impedance, expected_rise_time):
    load_impedance, rise_time = spikesafe_python.Compensation.get_optimum_compensation(spikesafe_model_max_current_amps, set_current_amps, pulse_on_time_seconds)
    assert load_impedance == expected_load_impedance
    assert rise_time == expected_rise_time