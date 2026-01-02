from .TcpSocket import TcpSocket

class Discharge:
    """
    Class for calculating SpikeSafe channel discharge time based on compliance voltage.

    Methods
    -------
    get_spikesafe_channel_discharge_time(compliance_voltage: float) -> float
        Returns the time in seconds to fully discharge the SpikeSafe channel based on the compliance voltage
    wait_for_spikesafe_channel_discharge(tcp_socket: TcpSocket, channel_number: int) -> None
        Waits for the SpikeSafe channel to fully discharge
    """

    @staticmethod
    def get_spikesafe_channel_discharge_time(compliance_voltage: float) -> float:
        """
        Returns the time in seconds to fully discharge the SpikeSafe channel based on the compliance voltage

        Parameters
        ----------
        compliance_voltage : float
            Compliance voltage to factor in discharge time
        
        Returns
        -------
        float
            Discharge time in seconds

        Raises
        ------
        None
        """
        # Discharge time accounting for compliance voltage, voltage readroom, and discharge voltage per second
        voltage_headroom_voltage = 7
        discharge_voltage_per_second = 1000
        discharge_time = (compliance_voltage + voltage_headroom_voltage) / discharge_voltage_per_second
        return discharge_time

    @staticmethod
    def wait_for_spikesafe_channel_discharge(
        tcp_socket: TcpSocket, 
        channel_number: int,
        enable_logging: bool | None = None
    ) -> None:
        """
        Waits for the SpikeSafe channel to fully discharge

        Parameters
        ----------
        tcp_socket : TcpSocket
            TCP socket connection to the SpikeSafe device
        channel_number : int
            Channel number to poll discharge state of
        
        Returns
        -------
        None

        Raises
        ------
        Exception
            On any error
        """
        # wait until the channel is fully discharged before disconnecting the load
        is_discharge_complete = ''                
        while is_discharge_complete != 'TRUE':                
            tcp_socket.send_scpi_command(f'OUTP{channel_number}:DISC:COMP?', enable_logging)
            is_discharge_complete = tcp_socket.read_data(enable_logging)

def get_spikesafe_channel_discharge_time(compliance_voltage: float) -> float:
    """
    Obsolete: use Discharge.get_spikesafe_channel_discharge_time instead
    """
    return Discharge.get_spikesafe_channel_discharge_time(compliance_voltage)