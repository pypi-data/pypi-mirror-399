# Goal: Parse channel portion of SpikeSafe memory table read into an accessible object
# Example: (CH1 10.123456 1.123000 1)

from __future__ import annotations
import logging
import math

log = logging.getLogger(__name__)

class ChannelData:
    """ A class used to store data in a simple accessible object from 
    a channel in SpikeSafe's event response

    Attributes
    ----------
    channel_number : int
        Channel number
    current_reading : float
        Channel current reading
    is_on_state : bool
        Channel on state
    voltage_reading : float
        Channel voltage reading

    Methods
    -------
    parse_channel_data(self, channel_memory_table_read_response: str) -> ChannelData
        Parses a channel in SpikeSafe's event response into a simple accessible object
    current_reading_amps_formatted(self) -> float
        Return the current reading formatted to matching hardware decimal places.
    voltage_reading_volts_formatted(self) -> float
        Return the voltage reading formatted to matching hardware decimal places.
    """

    
    channel_number: int = 0
    current_reading: float = math.nan
    is_on_state: bool = False
    voltage_reading: float = math.nan

    def __init__(self) -> None:
        pass

    # Goal: Helper function to parse channel portion of SpikeSafe memory table read into an accessible object
    def parse_channel_data(self, channel_memory_table_read_response: str) -> ChannelData:
        """Parses a channel in SpikeSafe's event response into a simple accessible object

        Parameters
        ----------
        channel_memory_table_read_response : str
            Channel in SpikeSafe's event response
        
        Returns
        -------
        ChannelData
            Channel in SpikeSafe's event response in a simple accessible object

        Raises
        ------
        Exception
            On any error
        """
        try:
            # find start of CH, extract "1 10.123456 1.123000 1" to string, and separate by " " into list
            search_str = "CH"
            channel_data_start_index = channel_memory_table_read_response.find(search_str)
            channel_parsable_format = channel_memory_table_read_response[channel_data_start_index + len(search_str) : len(channel_memory_table_read_response) - 1]
            channel_response_split = channel_parsable_format.split(' ')

            # set all values
            self.channel_number = int(channel_response_split[0])
            self.voltage_reading = float(channel_response_split[1])
            self.current_reading = float(channel_response_split[2])
            self.is_on_state = {'0': False, '1': True}[channel_response_split[3]]

            # return channel data object to caller
            return self
        except Exception as err:
            # print any error to the log file and raise to function caller
            log.error("Error parsing channel data from SpikeSafe memory table read: {}".format(err))                                            
            raise  

    def current_reading_amps_formatted_float(self) -> float:
        """Return the current reading formatted to matching hardware decimal places.

        Returns
        -------
        float
            Current reading formatted to matching hardware decimal places.
        """
        return round(self.current_reading, 7)    
    
    def current_reading_amps_formatted_string(self) -> str:
        """Return the current reading formatted to matching hardware decimal places.

        Returns
        -------
        string
            Current reading formatted to matching hardware decimal places.
        """
        return f'{self.current_reading:.7f}'
    
    def voltage_reading_volts_formatted_float(self) -> float:
        """Return the voltage reading formatted to matching hardware decimal places.

        Returns
        -------
        float
            Voltage reading formatted to matching hardware decimal places.
        """
        return round(self.voltage_reading, 6)
    
    def voltage_reading_volts_formatted_string(self) -> str:
        """Return the voltage reading formatted to matching hardware decimal places.

        Returns
        -------
        string
            Voltage reading formatted to matching hardware decimal places.
        """
        return f'{self.voltage_reading:.6f}'