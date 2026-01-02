import pytest
from spikesafe_python.EventData import EventData

@pytest.mark.parametrize("syst_err_return, expected_event, expected_code, expected_message, expected_channel_list", [
    # Test no channel list
    ("306, Invalid Command", "306, Invalid Command", 306, "Invalid Command", []),
    # Invalid test no channel list with single physical channel
    #("306, Invalid Command; Physical Channel(s) 1", "306, Invalid Command; Physical Channel(s) 1", 306, "Invalid Command", []),
    # Invalid test no channel list with multiple physical channels
    #("306, Invalid Command; Physical Channel(s) 1,2", "306, Invalid Command; Physical Channel(s) 1,2", 306, "Invalid Command", []),
    # Test single channel list with no physical channel
    ("207, Current Leakage Detected; Channel(s) 1", "207, Current Leakage Detected; Channel(s) 1", 207, "Current Leakage Detected", [1]),
    # Test single channel list with single physical channel
    ("207, Current Leakage Detected; Channel(s) 1; Physical Channel(s) 1", "207, Current Leakage Detected; Channel(s) 1; Physical Channel(s) 1", 207, "Current Leakage Detected", [1]),
    # Test single channel list with multiple physical channels
    ("207, Current Leakage Detected; Channel(s) 1; Physical Channel(s) 1,2", "207, Current Leakage Detected; Channel(s) 1; Physical Channel(s) 1,2", 207, "Current Leakage Detected", [1]),
    # Test multiple channel list with no physical channels
    ("207, Current Leakage Detected; Channel(s) 1,2", "207, Current Leakage Detected; Channel(s) 1,2", 207, "Current Leakage Detected", [1, 2]),
    # Invalid test multiple channel list with single physical channel
    #("207, Current Leakage Detected; Channel(s) 1,2; Physical Channel(s) 1", "207, Current Leakage Detected; Channel(s) 1,2; Physical Channel(s) 1", 207, "Current Leakage Detected", [1, 2]),
    # Test multiple channel list with multiple physical channels
    ("207, Current Leakage Detected; Channel(s) 1,2; Physical Channel(s) 1,2,3,4", "207, Current Leakage Detected; Channel(s) 1,2; Physical Channel(s) 1,2,3,4", 207, "Current Leakage Detected", [1, 2])
])
def test_parse_event_data(syst_err_return, expected_event, expected_code, expected_message, expected_channel_list):
    event_data = EventData()
    parsed_event = event_data.parse_event_data(syst_err_return)
    assert parsed_event.event == expected_event
    assert parsed_event.code == expected_code
    assert parsed_event.message == expected_message
    assert parsed_event.channel_list == expected_channel_list