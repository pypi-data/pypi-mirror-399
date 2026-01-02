import math
import pytest
from unittest.mock import MagicMock, patch
from spikesafe_python.DigitizerDataFetch import fetch_voltage_data_sampling_mode_custom, fetch_voltage_data_sampling_mode_linear, fetch_voltage_data_sampling_mode_logarithmic
from spikesafe_python.DigitizerEnums import SamplingMode, TimeSamplingMode
from spikesafe_python.DigitizerData import DigitizerData

def test_fetch_voltage_data_sampling_mode_linear_middle_of_time():
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()
    
    # Mock the behavior of send_scpi_command (assuming no return is needed)
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = "1.0,2.0,3.0"  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_linear(
        spike_safe_socket=mock_socket,
        time_sampling_mode=TimeSamplingMode.MIDDLE_OF_TIME,
        aperture_microseconds=2,
        reading_count=3,
        hardware_trigger_delay_microseconds=0,
        pulse_period_seconds=0
    )

    # Assertions
    assert len(digitizer_data) == 3  # Should return 3 samples
    assert digitizer_data[0].voltage_reading == 1.0
    assert digitizer_data[1].voltage_reading == 2.0
    assert digitizer_data[2].voltage_reading == 3.0

    # Check that time_since_start_seconds is correct
    # The time calculations depend on your implementation of __get_sampling_mode_linear_time_since_start_seconds
    assert digitizer_data[0].time_since_start_seconds == 0.000001
    assert digitizer_data[1].time_since_start_seconds == 0.000003
    assert digitizer_data[2].time_since_start_seconds == 0.000005

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()

def test_fetch_voltage_data_sampling_mode_linear_end_of_time():
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()
    
    # Mock the behavior of send_scpi_command (assuming no return is needed)
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = "1.0,2.0,3.0"  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_linear(
        spike_safe_socket=mock_socket,
        time_sampling_mode=TimeSamplingMode.END_OF_TIME,
        aperture_microseconds=2,
        reading_count=3,
        hardware_trigger_delay_microseconds=0,
        pulse_period_seconds=0
    )

    # Assertions
    assert len(digitizer_data) == 3  # Should return 3 samples
    assert digitizer_data[0].voltage_reading == 1.0
    assert digitizer_data[1].voltage_reading == 2.0
    assert digitizer_data[2].voltage_reading == 3.0

    # Check that time_since_start_seconds is correct
    # The time calculations depend on your implementation of __get_sampling_mode_linear_time_since_start_seconds
    assert digitizer_data[0].time_since_start_seconds == 0.0
    assert digitizer_data[1].time_since_start_seconds == 0.000002
    assert digitizer_data[2].time_since_start_seconds == 0.000004

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()

def test_fetch_voltage_data_sampling_mode_linear_middle_of_time_single_reading_per_trigger():
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()
    
    # Mock the behavior of send_scpi_command (assuming no return is needed)
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = "1.0,2.0,3.0"  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_linear(
        spike_safe_socket=mock_socket,
        time_sampling_mode=TimeSamplingMode.MIDDLE_OF_TIME,
        aperture_microseconds=600,
        reading_count=1,
        hardware_trigger_delay_microseconds=200,
        pulse_period_seconds=0.01
    )

    # Assertions
    assert len(digitizer_data) == 3  # Should return 3 samples
    assert digitizer_data[0].voltage_reading == 1.0
    assert digitizer_data[1].voltage_reading == 2.0
    assert digitizer_data[2].voltage_reading == 3.0

    # Check that time_since_start_seconds is correct
    # The time calculations depend on your implementation of __get_sampling_mode_linear_time_since_start_seconds
    assert digitizer_data[0].time_since_start_seconds == 0.0005
    assert digitizer_data[1].time_since_start_seconds == 0.0113
    assert digitizer_data[2].time_since_start_seconds == 0.0221

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()


def test_fetch_voltage_data_sampling_mode_linear_end_of_time_single_reading_per_trigger():
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()
    
    # Mock the behavior of send_scpi_command (assuming no return is needed)
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = "1.0,2.0,3.0"  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_linear(
        spike_safe_socket=mock_socket,
        time_sampling_mode=TimeSamplingMode.END_OF_TIME,
        aperture_microseconds=600,
        reading_count=1,
        hardware_trigger_delay_microseconds=200,
        pulse_period_seconds=0.01
    )

    # Assertions
    assert len(digitizer_data) == 3  # Should return 3 samples
    assert digitizer_data[0].voltage_reading == 1.0
    assert digitizer_data[1].voltage_reading == 2.0
    assert digitizer_data[2].voltage_reading == 3.0

    # Check that time_since_start_seconds is correct
    # The time calculations depend on your implementation of __get_sampling_mode_linear_time_since_start_seconds
    assert digitizer_data[0].time_since_start_seconds == 0.0002
    assert digitizer_data[1].time_since_start_seconds == 0.0110
    assert digitizer_data[2].time_since_start_seconds == 0.0218

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()


def test_fetch_voltage_data_sampling_mode_linear_middle_of_time_multiple_readings_per_trigger():
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()
    
    # Mock the behavior of send_scpi_command (assuming no return is needed)
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = "1.0,2.0,3.0,4.0,5.0,6.0"  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_linear(
        spike_safe_socket=mock_socket,
        time_sampling_mode=TimeSamplingMode.MIDDLE_OF_TIME,
        aperture_microseconds=600,
        reading_count=2,
        hardware_trigger_delay_microseconds=200,
        pulse_period_seconds=0.01
    )

    # Assertions
    assert len(digitizer_data) == 6  # Should return 3 samples
    assert digitizer_data[0].voltage_reading == 1.0
    assert digitizer_data[1].voltage_reading == 2.0
    assert digitizer_data[2].voltage_reading == 3.0
    assert digitizer_data[3].voltage_reading == 4.0
    assert digitizer_data[4].voltage_reading == 5.0
    assert digitizer_data[5].voltage_reading == 6.0

    # Check that time_since_start_seconds is correct
    # The time calculations depend on your implementation of __get_sampling_mode_linear_time_since_start_seconds
    assert digitizer_data[0].time_since_start_seconds == 0.0005
    assert digitizer_data[1].time_since_start_seconds == 0.0011
    assert digitizer_data[2].time_since_start_seconds == 0.0119
    assert digitizer_data[3].time_since_start_seconds == 0.0125
    assert digitizer_data[4].time_since_start_seconds == 0.0233
    assert digitizer_data[5].time_since_start_seconds == 0.0239

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()


def test_fetch_voltage_data_sampling_mode_linear_end_of_time_multiple_readings_per_trigger():
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()
    
    # Mock the behavior of send_scpi_command (assuming no return is needed)
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = "1.0,2.0,3.0,4.0,5.0,6.0"  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_linear(
        spike_safe_socket=mock_socket,
        time_sampling_mode=TimeSamplingMode.END_OF_TIME,
        aperture_microseconds=600,
        reading_count=2,
        hardware_trigger_delay_microseconds=200,
        pulse_period_seconds=0.01
    )

    # Assertions
    assert len(digitizer_data) == 6  # Should return 3 samples
    assert digitizer_data[0].voltage_reading == 1.0
    assert digitizer_data[1].voltage_reading == 2.0
    assert digitizer_data[2].voltage_reading == 3.0
    assert digitizer_data[3].voltage_reading == 4.0
    assert digitizer_data[4].voltage_reading == 5.0
    assert digitizer_data[5].voltage_reading == 6.0

    # Check that time_since_start_seconds is correct
    # The time calculations depend on your implementation of __get_sampling_mode_linear_time_since_start_seconds
    assert digitizer_data[0].time_since_start_seconds == 0.0002
    assert digitizer_data[1].time_since_start_seconds == 0.0008
    assert digitizer_data[2].time_since_start_seconds == 0.0116
    assert digitizer_data[3].time_since_start_seconds == 0.0122
    assert digitizer_data[4].time_since_start_seconds == 0.0230
    assert digitizer_data[5].time_since_start_seconds == 0.0236

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()

@pytest.mark.parametrize(
    "sampling_mode, time_sampling_mode, expected_sample_count, expected_sample_numbers, expected_time_since_start",
    [
        (SamplingMode.FAST_LOG, TimeSamplingMode.MIDDLE_OF_TIME, 525, [1, 2, 3, 524, 525], [0.000001, 0.000003, 0.000005, 8.35, 8.45]),
        (SamplingMode.MEDIUM_LOG, TimeSamplingMode.MIDDLE_OF_TIME, 500, [1, 2, 3, 499, 500], [0.000001, 0.000003, 0.000005, 98.2, 99.4]),
        (SamplingMode.SLOW_LOG, TimeSamplingMode.MIDDLE_OF_TIME, 500, [1, 2, 3, 499, 500], [0.000001, 0.000003, 0.000005, 970.0, 990.0]),
        (SamplingMode.FAST_LOG, TimeSamplingMode.END_OF_TIME, 525, [1, 2, 3, 524, 525], [0.000002, 0.000004, 0.000006, 8.4, 8.5]),
        (SamplingMode.MEDIUM_LOG, TimeSamplingMode.END_OF_TIME, 500, [1, 2, 3, 499, 500], [0.000002, 0.000004, 0.000006, 98.8, 100.0]),
        (SamplingMode.SLOW_LOG, TimeSamplingMode.END_OF_TIME, 500, [1, 2, 3, 499, 500], [0.000002, 0.000004, 0.000006, 980.0, 1000.0]),
    ]
)
def test_fetch_voltage_data_sampling_mode_logarithmic(sampling_mode, time_sampling_mode, expected_sample_count, expected_sample_numbers, expected_time_since_start):
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()

    # Mock the behavior of send_scpi_command
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = ",".join([str(x) for x in range(1, expected_sample_count + 1)])  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_logarithmic(
        spike_safe_socket=mock_socket,
        time_sampling_mode=time_sampling_mode,
        sampling_mode=sampling_mode
    )

    # Check that time_since_start_seconds is correct
    for i, expected_time in enumerate(expected_time_since_start):
        sample_number = expected_sample_numbers[i]
        assert digitizer_data[sample_number - 1].time_since_start_seconds == expected_time

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()

@pytest.mark.parametrize(
    "sampling_mode, time_sampling_mode, hardware_trigger_delay_microseconds, expected_sample_count, expected_sample_numbers, expected_time_since_start",
    [
        (SamplingMode.FAST_LOG, TimeSamplingMode.MIDDLE_OF_TIME, 0, 525, [1, 2, 3, 524, 525], [0.000001, 0.000003, 0.000005, 8.35, 8.45]),
        (SamplingMode.FAST_LOG, TimeSamplingMode.MIDDLE_OF_TIME, 200, 525, [1, 2, 3, 524, 525], [0.000201, 0.000203, 0.000205, 8.3502, 8.4502]),
        (SamplingMode.FAST_LOG, TimeSamplingMode.END_OF_TIME, 0, 525, [1, 2, 3, 524, 525], [0.000002, 0.000004, 0.000006, 8.4, 8.5]),
        (SamplingMode.FAST_LOG, TimeSamplingMode.END_OF_TIME, 200, 525, [1, 2, 3, 524, 525], [0.000202, 0.000204, 0.000206, 8.4002, 8.5002])
    ]
)
def test_fetch_voltage_data_sampling_mode_logarithmic_trigger_delay(sampling_mode, time_sampling_mode, hardware_trigger_delay_microseconds, expected_sample_count, expected_sample_numbers, expected_time_since_start):
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()

    # Mock the behavior of send_scpi_command
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = ",".join([str(x) for x in range(1, expected_sample_count + 1)])  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_logarithmic(
        spike_safe_socket=mock_socket,
        time_sampling_mode=time_sampling_mode,
        sampling_mode=sampling_mode,
        hardware_trigger_delay_microseconds=hardware_trigger_delay_microseconds
    )

    # Check that time_since_start_seconds is correct
    for i, expected_time in enumerate(expected_time_since_start):
        sample_number = expected_sample_numbers[i]
        assert digitizer_data[sample_number - 1].time_since_start_seconds == expected_time

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()

@pytest.mark.parametrize("sampling_mode, expected_exception", [
    (SamplingMode.LINEAR, "SamplingMode.LINEAR sampling mode is invalid. Use sampling mode FAST_LOG, MEDIUM_LOG, or SLOW_LOG."),
    (SamplingMode.CUSTOM, "SamplingMode.CUSTOM sampling mode is invalid. Use sampling mode FAST_LOG, MEDIUM_LOG, or SLOW_LOG.")
])
def test_fetch_voltage_data_sampling_mode_logarithmic_exceptions(sampling_mode, expected_exception):
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()
    
    # Mock the behavior of send_scpi_command (assuming no return is needed)
    mock_socket.send_scpi_command = MagicMock()

    mock_socket.read_data.return_value = ",".join([str(x) for x in range(1, 526)])  # Simulated voltage readings

    with pytest.raises(ValueError) as excinfo:
        fetch_voltage_data_sampling_mode_logarithmic(
            mock_socket,
            time_sampling_mode=TimeSamplingMode.MIDDLE_OF_TIME,
            sampling_mode=sampling_mode
        )

    assert str(excinfo.value) == expected_exception

@pytest.mark.parametrize(
    "custom_sequence, time_sampling_mode, expected_sample_count, expected_sample_numbers, expected_time_since_start",
    [
        # 4_decade_50_point_log.digseq middle of time
        (
            "50@2,2@4,7@6,6@8,4@10,4@12,3@14,2@16,3@18,2@20,2@22,2@24,1@26,2@28,1@30,2@32,1@34,1@36,1@38,1@40,2@42,1@46,1@48,1@50,1@52,1@54,1@56,1@60,1@62,1@66,1@68,1@72,1@74,1@78,1@82,1@86,1@90,1@94,1@98,1@104,1@108,1@114,1@118,1@124,1@130,1@136,1@142,1@150,1@156,1@164,1@172,1@180,1@188,1@196,1@206,1@216,1@226,1@236,1@248,1@258,1@272,1@284,1@298,1@312,1@326,1@342,1@358,1@374,1@392,1@410,1@430,1@450",
            TimeSamplingMode.MIDDLE_OF_TIME, 150, [1, 2, 3, 149, 150], [0.000001, 0.000003, 0.000005, 0.009345, 0.009785]
        ),
        # 9_decade_50_point_log.digseq middle of time
        (
            "50@2,2@4,7@6,6@8,4@10,4@12,3@14,2@16,3@18,2@20,2@22,2@24,1@26,2@28,1@30,2@32,1@34,1@36,1@38,1@40,2@42,1@46,1@48,1@50,1@52,1@54,1@56,1@60,1@62,1@66,1@68,1@72,1@74,1@78,1@82,1@86,1@90,1@94,1@98,1@104,1@108,1@114,1@118,1@124,1@130,1@136,1@142,1@150,1@156,1@164,1@172,1@180,1@188,1@196,1@206,1@216,1@226,1@236,1@248,1@258,1@272,1@284,1@298,1@312,1@326,1@342,1@358,1@374,1@392,1@410,1@430,1@450,1@472,1@494,1@516,1@542,1@566,1@594,1@622,1@650,1@682,1@714,1@746,1@782,1@820,1@858,1@898,1@940,1@984,1@1032,1@1080,1@1130,1@1184,1@1240,1@1298,1@1360,1@1424,1@1490,1@1560,1@1634,1@1712,1@1792,1@1876,1@1964,1@2058,1@2154,1@2256,1@2362,1@2474,1@2590,1@2712,1@2840,1@2974,1@3114,1@3260,1@3414,1@3576,1@3744,1@3920,1@4104,1@4298,1@4500,1@4712,1@4934,1@5168,1@5412,1@5666,1@5934,1@6212,1@6506,1@6812,1@7134,1@7470,1@7822,1@8190,1@8576,1@8980,1@9404,1@9846,1@10310,1@10796,1@11306,1@11838,1@12396,1@12980,1@13592,1@14232,1@14904,1@15606,1@16342,1@17112,1@17918,1@18762,1@19646,1@20572,1@21542,1@22558,1@23620,1@24734,1@25900,1@27120,1@28398,1@29736,1@31138,1@32604,1@34142,1@35750,1@37436,1@39200,1@41048,1@42982,1@45008,1@47128,1@49350,1@51676,1@54110,1@56660,1@59332,1@62128,1@65056,1@68122,1@71332,1@74694,1@78214,1@81900,1@85760,1@89802,1@94034,1@98466,1@103106,1@107966,1@113054,1@118382,1@123960,1@129802,1@135920,1@142326,1@149034,1@156058,1@163412,1@171114,1@179178,1@187622,1@196464,1@205724,1@215420,1@225572,1@236202,1@247334,1@258990,1@271196,1@283978,1@297362,1@311376,1@326050,1@341416,1@357506,1@374356,1@391998,1@410472,1@429818,1@450074,1@471286,1@493496,1@516754,1@541108,1@566610,1@593314,1@621276,1@650556,1@681214,1@713320,1@746938,1@782140,1@819000,1@857598,1@898016,1@940338,1@984654,1@1031060,1@1079652,1@1130536,1@1183816,1@1239608,1@1298028,1@1359202,1@1423260,1@1490336,1@1560572,1@1634120,1@1711134,1@1791778,1@1876222,1@1964644,1@2057236,1@2154190,1@2255714,1@2362022,1@2473342,1@2589906,1@2711964,1@2839776,1@2973610,1@3113752,1@3260498,1@3414162,1@3575066,1@3743554,1@3919982,1@4104724,1@4298174,1@4500742,175@5142858", 
            TimeSamplingMode.MIDDLE_OF_TIME, 525, [1, 2, 3, 524, 525], [0.000001, 0.000003, 0.000005, 992.285891, 997.428749]
        ),
        # 4_decade_50_point_log.digseq end of time
        (
            "50@2,2@4,7@6,6@8,4@10,4@12,3@14,2@16,3@18,2@20,2@22,2@24,1@26,2@28,1@30,2@32,1@34,1@36,1@38,1@40,2@42,1@46,1@48,1@50,1@52,1@54,1@56,1@60,1@62,1@66,1@68,1@72,1@74,1@78,1@82,1@86,1@90,1@94,1@98,1@104,1@108,1@114,1@118,1@124,1@130,1@136,1@142,1@150,1@156,1@164,1@172,1@180,1@188,1@196,1@206,1@216,1@226,1@236,1@248,1@258,1@272,1@284,1@298,1@312,1@326,1@342,1@358,1@374,1@392,1@410,1@430,1@450",
            TimeSamplingMode.END_OF_TIME, 150, [1, 2, 3, 149, 150], [0.000002, 0.000004, 0.000006, 0.00956, 0.01001]
        ),
        # 9_decade_50_point_log.digseq end of time
        (
            "50@2,2@4,7@6,6@8,4@10,4@12,3@14,2@16,3@18,2@20,2@22,2@24,1@26,2@28,1@30,2@32,1@34,1@36,1@38,1@40,2@42,1@46,1@48,1@50,1@52,1@54,1@56,1@60,1@62,1@66,1@68,1@72,1@74,1@78,1@82,1@86,1@90,1@94,1@98,1@104,1@108,1@114,1@118,1@124,1@130,1@136,1@142,1@150,1@156,1@164,1@172,1@180,1@188,1@196,1@206,1@216,1@226,1@236,1@248,1@258,1@272,1@284,1@298,1@312,1@326,1@342,1@358,1@374,1@392,1@410,1@430,1@450,1@472,1@494,1@516,1@542,1@566,1@594,1@622,1@650,1@682,1@714,1@746,1@782,1@820,1@858,1@898,1@940,1@984,1@1032,1@1080,1@1130,1@1184,1@1240,1@1298,1@1360,1@1424,1@1490,1@1560,1@1634,1@1712,1@1792,1@1876,1@1964,1@2058,1@2154,1@2256,1@2362,1@2474,1@2590,1@2712,1@2840,1@2974,1@3114,1@3260,1@3414,1@3576,1@3744,1@3920,1@4104,1@4298,1@4500,1@4712,1@4934,1@5168,1@5412,1@5666,1@5934,1@6212,1@6506,1@6812,1@7134,1@7470,1@7822,1@8190,1@8576,1@8980,1@9404,1@9846,1@10310,1@10796,1@11306,1@11838,1@12396,1@12980,1@13592,1@14232,1@14904,1@15606,1@16342,1@17112,1@17918,1@18762,1@19646,1@20572,1@21542,1@22558,1@23620,1@24734,1@25900,1@27120,1@28398,1@29736,1@31138,1@32604,1@34142,1@35750,1@37436,1@39200,1@41048,1@42982,1@45008,1@47128,1@49350,1@51676,1@54110,1@56660,1@59332,1@62128,1@65056,1@68122,1@71332,1@74694,1@78214,1@81900,1@85760,1@89802,1@94034,1@98466,1@103106,1@107966,1@113054,1@118382,1@123960,1@129802,1@135920,1@142326,1@149034,1@156058,1@163412,1@171114,1@179178,1@187622,1@196464,1@205724,1@215420,1@225572,1@236202,1@247334,1@258990,1@271196,1@283978,1@297362,1@311376,1@326050,1@341416,1@357506,1@374356,1@391998,1@410472,1@429818,1@450074,1@471286,1@493496,1@516754,1@541108,1@566610,1@593314,1@621276,1@650556,1@681214,1@713320,1@746938,1@782140,1@819000,1@857598,1@898016,1@940338,1@984654,1@1031060,1@1079652,1@1130536,1@1183816,1@1239608,1@1298028,1@1359202,1@1423260,1@1490336,1@1560572,1@1634120,1@1711134,1@1791778,1@1876222,1@1964644,1@2057236,1@2154190,1@2255714,1@2362022,1@2473342,1@2589906,1@2711964,1@2839776,1@2973610,1@3113752,1@3260498,1@3414162,1@3575066,1@3743554,1@3919982,1@4104724,1@4298174,1@4500742,175@5142858", 
            TimeSamplingMode.END_OF_TIME, 525, [1, 2, 3, 524, 525], [0.000002, 0.000004, 0.000006, 994.85732, 1000.000178]
        )
    ]
)
def test_fetch_voltage_data_sampling_mode_custom(custom_sequence, time_sampling_mode, expected_sample_count, expected_sample_numbers, expected_time_since_start):
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()

    # Mock the behavior of send_scpi_command
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = ",".join([str(x) for x in range(1, expected_sample_count + 1)])  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_custom(
        spike_safe_socket=mock_socket,
        time_sampling_mode=time_sampling_mode,
        custom_sequence=custom_sequence
    )

    # Check that time_since_start_seconds is correct
    for i, expected_time in enumerate(expected_time_since_start):
        sample_number = expected_sample_numbers[i]
        assert digitizer_data[sample_number - 1].time_since_start_seconds == expected_time

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()

@pytest.mark.parametrize(
    "custom_sequence, time_sampling_mode, hardware_trigger_delay_microseconds, expected_sample_count, expected_sample_numbers, expected_time_since_start",
    [
        # 4_decade_50_point_log.digseq middle of time
        (
            "50@2,2@4,7@6,6@8,4@10,4@12,3@14,2@16,3@18,2@20,2@22,2@24,1@26,2@28,1@30,2@32,1@34,1@36,1@38,1@40,2@42,1@46,1@48,1@50,1@52,1@54,1@56,1@60,1@62,1@66,1@68,1@72,1@74,1@78,1@82,1@86,1@90,1@94,1@98,1@104,1@108,1@114,1@118,1@124,1@130,1@136,1@142,1@150,1@156,1@164,1@172,1@180,1@188,1@196,1@206,1@216,1@226,1@236,1@248,1@258,1@272,1@284,1@298,1@312,1@326,1@342,1@358,1@374,1@392,1@410,1@430,1@450",
            TimeSamplingMode.MIDDLE_OF_TIME, 200, 150, [1, 2, 3, 149, 150], [0.000201, 0.000203, 0.000205, 0.009545, 0.009985]
        ),
        # 9_decade_50_point_log.digseq middle of time
        (
            "50@2,2@4,7@6,6@8,4@10,4@12,3@14,2@16,3@18,2@20,2@22,2@24,1@26,2@28,1@30,2@32,1@34,1@36,1@38,1@40,2@42,1@46,1@48,1@50,1@52,1@54,1@56,1@60,1@62,1@66,1@68,1@72,1@74,1@78,1@82,1@86,1@90,1@94,1@98,1@104,1@108,1@114,1@118,1@124,1@130,1@136,1@142,1@150,1@156,1@164,1@172,1@180,1@188,1@196,1@206,1@216,1@226,1@236,1@248,1@258,1@272,1@284,1@298,1@312,1@326,1@342,1@358,1@374,1@392,1@410,1@430,1@450,1@472,1@494,1@516,1@542,1@566,1@594,1@622,1@650,1@682,1@714,1@746,1@782,1@820,1@858,1@898,1@940,1@984,1@1032,1@1080,1@1130,1@1184,1@1240,1@1298,1@1360,1@1424,1@1490,1@1560,1@1634,1@1712,1@1792,1@1876,1@1964,1@2058,1@2154,1@2256,1@2362,1@2474,1@2590,1@2712,1@2840,1@2974,1@3114,1@3260,1@3414,1@3576,1@3744,1@3920,1@4104,1@4298,1@4500,1@4712,1@4934,1@5168,1@5412,1@5666,1@5934,1@6212,1@6506,1@6812,1@7134,1@7470,1@7822,1@8190,1@8576,1@8980,1@9404,1@9846,1@10310,1@10796,1@11306,1@11838,1@12396,1@12980,1@13592,1@14232,1@14904,1@15606,1@16342,1@17112,1@17918,1@18762,1@19646,1@20572,1@21542,1@22558,1@23620,1@24734,1@25900,1@27120,1@28398,1@29736,1@31138,1@32604,1@34142,1@35750,1@37436,1@39200,1@41048,1@42982,1@45008,1@47128,1@49350,1@51676,1@54110,1@56660,1@59332,1@62128,1@65056,1@68122,1@71332,1@74694,1@78214,1@81900,1@85760,1@89802,1@94034,1@98466,1@103106,1@107966,1@113054,1@118382,1@123960,1@129802,1@135920,1@142326,1@149034,1@156058,1@163412,1@171114,1@179178,1@187622,1@196464,1@205724,1@215420,1@225572,1@236202,1@247334,1@258990,1@271196,1@283978,1@297362,1@311376,1@326050,1@341416,1@357506,1@374356,1@391998,1@410472,1@429818,1@450074,1@471286,1@493496,1@516754,1@541108,1@566610,1@593314,1@621276,1@650556,1@681214,1@713320,1@746938,1@782140,1@819000,1@857598,1@898016,1@940338,1@984654,1@1031060,1@1079652,1@1130536,1@1183816,1@1239608,1@1298028,1@1359202,1@1423260,1@1490336,1@1560572,1@1634120,1@1711134,1@1791778,1@1876222,1@1964644,1@2057236,1@2154190,1@2255714,1@2362022,1@2473342,1@2589906,1@2711964,1@2839776,1@2973610,1@3113752,1@3260498,1@3414162,1@3575066,1@3743554,1@3919982,1@4104724,1@4298174,1@4500742,175@5142858", 
            TimeSamplingMode.MIDDLE_OF_TIME, 200, 525, [1, 2, 3, 524, 525], [0.000201, 0.000203, 0.000205, 992.286091, 997.428949]
        ),
        # 4_decade_50_point_log.digseq end of time
        (
            "50@2,2@4,7@6,6@8,4@10,4@12,3@14,2@16,3@18,2@20,2@22,2@24,1@26,2@28,1@30,2@32,1@34,1@36,1@38,1@40,2@42,1@46,1@48,1@50,1@52,1@54,1@56,1@60,1@62,1@66,1@68,1@72,1@74,1@78,1@82,1@86,1@90,1@94,1@98,1@104,1@108,1@114,1@118,1@124,1@130,1@136,1@142,1@150,1@156,1@164,1@172,1@180,1@188,1@196,1@206,1@216,1@226,1@236,1@248,1@258,1@272,1@284,1@298,1@312,1@326,1@342,1@358,1@374,1@392,1@410,1@430,1@450",
            TimeSamplingMode.END_OF_TIME, 200, 150, [1, 2, 3, 149, 150], [0.000202, 0.000204, 0.000206, 0.00976, 0.01021]
        ),
        # 9_decade_50_point_log.digseq end of time
        (
            "50@2,2@4,7@6,6@8,4@10,4@12,3@14,2@16,3@18,2@20,2@22,2@24,1@26,2@28,1@30,2@32,1@34,1@36,1@38,1@40,2@42,1@46,1@48,1@50,1@52,1@54,1@56,1@60,1@62,1@66,1@68,1@72,1@74,1@78,1@82,1@86,1@90,1@94,1@98,1@104,1@108,1@114,1@118,1@124,1@130,1@136,1@142,1@150,1@156,1@164,1@172,1@180,1@188,1@196,1@206,1@216,1@226,1@236,1@248,1@258,1@272,1@284,1@298,1@312,1@326,1@342,1@358,1@374,1@392,1@410,1@430,1@450,1@472,1@494,1@516,1@542,1@566,1@594,1@622,1@650,1@682,1@714,1@746,1@782,1@820,1@858,1@898,1@940,1@984,1@1032,1@1080,1@1130,1@1184,1@1240,1@1298,1@1360,1@1424,1@1490,1@1560,1@1634,1@1712,1@1792,1@1876,1@1964,1@2058,1@2154,1@2256,1@2362,1@2474,1@2590,1@2712,1@2840,1@2974,1@3114,1@3260,1@3414,1@3576,1@3744,1@3920,1@4104,1@4298,1@4500,1@4712,1@4934,1@5168,1@5412,1@5666,1@5934,1@6212,1@6506,1@6812,1@7134,1@7470,1@7822,1@8190,1@8576,1@8980,1@9404,1@9846,1@10310,1@10796,1@11306,1@11838,1@12396,1@12980,1@13592,1@14232,1@14904,1@15606,1@16342,1@17112,1@17918,1@18762,1@19646,1@20572,1@21542,1@22558,1@23620,1@24734,1@25900,1@27120,1@28398,1@29736,1@31138,1@32604,1@34142,1@35750,1@37436,1@39200,1@41048,1@42982,1@45008,1@47128,1@49350,1@51676,1@54110,1@56660,1@59332,1@62128,1@65056,1@68122,1@71332,1@74694,1@78214,1@81900,1@85760,1@89802,1@94034,1@98466,1@103106,1@107966,1@113054,1@118382,1@123960,1@129802,1@135920,1@142326,1@149034,1@156058,1@163412,1@171114,1@179178,1@187622,1@196464,1@205724,1@215420,1@225572,1@236202,1@247334,1@258990,1@271196,1@283978,1@297362,1@311376,1@326050,1@341416,1@357506,1@374356,1@391998,1@410472,1@429818,1@450074,1@471286,1@493496,1@516754,1@541108,1@566610,1@593314,1@621276,1@650556,1@681214,1@713320,1@746938,1@782140,1@819000,1@857598,1@898016,1@940338,1@984654,1@1031060,1@1079652,1@1130536,1@1183816,1@1239608,1@1298028,1@1359202,1@1423260,1@1490336,1@1560572,1@1634120,1@1711134,1@1791778,1@1876222,1@1964644,1@2057236,1@2154190,1@2255714,1@2362022,1@2473342,1@2589906,1@2711964,1@2839776,1@2973610,1@3113752,1@3260498,1@3414162,1@3575066,1@3743554,1@3919982,1@4104724,1@4298174,1@4500742,175@5142858", 
            TimeSamplingMode.END_OF_TIME, 200, 525, [1, 2, 3, 524, 525], [0.000202, 0.000204, 0.000206, 994.85752, 1000.000378]
        )
    ]
)
def test_fetch_voltage_data_sampling_mode_custom_trigger_delay(custom_sequence, time_sampling_mode, hardware_trigger_delay_microseconds, expected_sample_count, expected_sample_numbers, expected_time_since_start):
    # Set up mock spike_safe_socket object
    mock_socket = MagicMock()

    # Mock the behavior of send_scpi_command
    mock_socket.send_scpi_command = MagicMock()

    # Mock the read_data method to simulate hardware response
    mock_socket.read_data.return_value = ",".join([str(x) for x in range(1, expected_sample_count + 1)])  # Simulated voltage readings

    # Call the method under test
    digitizer_data = fetch_voltage_data_sampling_mode_custom(
        spike_safe_socket=mock_socket,
        time_sampling_mode=time_sampling_mode,
        custom_sequence=custom_sequence,
        hardware_trigger_delay_microseconds=hardware_trigger_delay_microseconds
    )

    # Check that time_since_start_seconds is correct
    for i, expected_time in enumerate(expected_time_since_start):
        sample_number = expected_sample_numbers[i]
        assert digitizer_data[sample_number - 1].time_since_start_seconds == expected_time

    # Ensure the mocked methods were called correctly
    mock_socket.send_scpi_command.assert_called_once_with('VOLT:FETC?', None)
    mock_socket.read_data.assert_called_once()