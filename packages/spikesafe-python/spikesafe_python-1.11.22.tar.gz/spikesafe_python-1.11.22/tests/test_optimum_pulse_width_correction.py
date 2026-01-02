import pytest
import spikesafe_python

@pytest.mark.parametrize("model_max_current, set_current, load_impedance, rise_time, expected", [
    (10, 4, spikesafe_python.SpikeSafeEnums.LoadImpedance.VERY_LOW, spikesafe_python.SpikeSafeEnums.RiseTime.VERY_SLOW, '2.476'),  # Add expected value
    (0.05, 0.0039, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '11.289'),   # test 50mA low range first entry
    (0.5, 0.0159, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.943'),     # test 500mA low range first entry < 0.016 max_test_current
    (0.5, 0.0160, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.924'),     # test 500mA low range first entry = 0.016 max_test_current
    (0.5, 0.0161, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.924'),     # test 500mA low range first entry > 0.016 max_test_current
    (0.5, 0.038, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.924'),      # test 500mA low range second entry = 0.038 max_test_current
    (0.5, 0.470, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.495'),      # test high 500mA range first entry < 0.470 max_test_current
    (0.5, 0.471, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.496'),      # test high 500mA range first entry = 0.471 max_test_current
    (0.5, 0.472, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.496'),      # test high 500mA range first entry > 0.472 max_test_current
    (0.5, 0.5, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.496'),        # test high model_max_current 500mA range = 0.5 set_current_amps
    (5, 0.001, spikesafe_python.SpikeSafeEnums.LoadImpedance.VERY_LOW, spikesafe_python.SpikeSafeEnums.RiseTime.VERY_SLOW, '50.000'),   # test calculated >50us correction coerced to 50us
    (0.5, 0.0438, spikesafe_python.SpikeSafeEnums.LoadImpedance.MEDIUM, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '0.000'),   # test calculated negative correction coerced to 0
    (25, 21, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, '1.250'),          # test invalid 25A model
])
def test_get_optimum_pulse_width_correction_value(model_max_current, set_current, load_impedance, rise_time, expected):
    correction_value = spikesafe_python.PulseWidthCorrection.get_optimum_pulse_width_correction(model_max_current, set_current, load_impedance, rise_time)
    assert correction_value == expected

@pytest.mark.parametrize("model_max_current, set_current, load_impedance, rise_time, expected_error_message", [
    (0.05, 0.051, spikesafe_python.SpikeSafeEnums.LoadImpedance.HIGH, spikesafe_python.SpikeSafeEnums.RiseTime.FAST, 'Measurement current 0.051A exceeds SpikeSafe model maximum current capability of 0.05A.'),   # test set_current > model_max_current
])
def test_test_get_optimum_pulse_width_correction_exceptions(model_max_current, set_current, load_impedance, rise_time, expected_error_message):
    with pytest.raises(ValueError) as exc_info:
        spikesafe_python.PulseWidthCorrection.get_optimum_pulse_width_correction(model_max_current, set_current, load_impedance, rise_time)
    assert expected_error_message in str(exc_info.value)