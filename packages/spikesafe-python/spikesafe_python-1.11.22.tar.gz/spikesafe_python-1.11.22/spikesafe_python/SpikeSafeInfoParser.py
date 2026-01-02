from .DigitizerInfo import DigitizerInfo
from .SpikeSafeInfo import SpikeSafeInfo
from .TcpSocket import TcpSocket

class SpikeSafeInfoParser:
    """
    Class to parse and hold the information of a SpikeSafe.

    Methods:
    -------
    parse_spikesafe_info(spike_safe_socket: TcpSocket, enable_logging: bool | None = None) -> SpikeSafeInfo
        Parses the SpikeSafe information from the SCPI command responses.
    compare_rev_version(rev_version: str, ref_version: str) -> bool
        Compares two revision version strings.
    """

    @staticmethod
    def parse_spikesafe_info(spike_safe_socket: TcpSocket, enable_logging: bool | None = None) -> SpikeSafeInfo:
        """Parses the SpikeSafe information from the SCPI command responses.
        
        Parameters
        ----------
        spike_safe_socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        enable_logging : bool, Optional
            Overrides spike_safe_socket.enable_logging attribute (default to None will use spike_safe_socket.enable_logging value)

        Returns
        -------
        SpikeSafeInfo
            An object containing the SpikeSafe information.

        """

        spikesafe_info = SpikeSafeInfo()

        spikesafe_info.ip_address = spike_safe_socket.socket_ip_address

        spike_safe_socket.send_scpi_command("*IDN?", enable_logging)
        idn = spike_safe_socket.read_data(enable_logging)
        spikesafe_info.idn = idn
        SpikeSafeInfoParser._parse_spikesafe_info_from_idn(spikesafe_info, idn)

        spikesafe_info.maximum_set_current = SpikeSafeInfoParser._query_float(spike_safe_socket, 'SOUR0:CURR? MAX', enable_logging)
        spikesafe_info.minimum_set_current = SpikeSafeInfoParser._query_float(spike_safe_socket, 'SOUR0:CURR? MIN', enable_logging)
        spikesafe_info.maximum_compliance_voltage = SpikeSafeInfoParser._query_float(spike_safe_socket, 'SOUR0:VOLT? MAX', enable_logging)
        spikesafe_info.minimum_compliance_voltage = SpikeSafeInfoParser._query_float(spike_safe_socket, 'SOUR0:VOLT? MIN', enable_logging)    
        spikesafe_info.minimum_pulse_width = SpikeSafeInfoParser._query_float(spike_safe_socket, 'SOUR0:PULS:TON? MIN', enable_logging)
        spikesafe_info.maximum_pulse_width = SpikeSafeInfoParser._query_float(spike_safe_socket, 'SOUR0:PULS:TON? MAX', enable_logging)
        spikesafe_info.minimum_pulse_width_offset = SpikeSafeInfoParser._query_float(spike_safe_socket, 'SOUR0:PULS:OFFS? MIN', enable_logging)
        spikesafe_info.maximum_pulse_width_offset = SpikeSafeInfoParser._query_float(spike_safe_socket, 'SOUR0:PULS:OFFS? MAX', enable_logging)

        spike_safe_socket.send_scpi_command('MEM:DATA ZINNUM?')
        zin_number = spike_safe_socket.read_data(enable_logging)
        spikesafe_info.zin_number = zin_number
        
        # Requires Release 3.12.9 (or Ethernet Processor must be 3.0.11.10 or later) to support Multiple digitizers, else:
        supports_multiple_digitizers = SpikeSafeInfoParser.compare_rev_version(spikesafe_info.version, "3.0.11.10")
        if supports_multiple_digitizers:
            spike_safe_socket.send_scpi_command('DIGI:FUNC:CARD:NUMB?')
            digitizer_functioning_card_number_list = spike_safe_socket.read_data(enable_logging)
            digitizer_functioning_card_number_list = digitizer_functioning_card_number_list.split(",")

            for digitizer_functioning_card_number in digitizer_functioning_card_number_list:
                SpikeSafeInfoParser._fetch_digitizer_info(spike_safe_socket, spikesafe_info, digitizer_functioning_card_number, enable_logging)

            spikesafe_info.has_digitizer = len(spikesafe_info.digitizer_infos) > 0
        else: 
            # Requires Release 1.2.5 (or Ethernet Processor 2.0.3.14 or later) to support this command
            supports_digitizer = SpikeSafeInfoParser.compare_rev_version(spikesafe_info.version, "2.0.3.17")
            if supports_digitizer:
                spike_safe_socket.send_scpi_command('MEM:DATA DIGIAVAIL?')
                has_digitizer = spike_safe_socket.read_data(enable_logging)
                spikesafe_info.has_digitizer = has_digitizer

                if has_digitizer == "TRUE":
                    SpikeSafeInfoParser._fetch_digitizer_info(spike_safe_socket, spikesafe_info, None, enable_logging)

        # Requires Release 1.3.1 (or Ethernet Processor 2.0.3.18 or later) to support this command
        supports_switch = SpikeSafeInfoParser.compare_rev_version(spikesafe_info.version, "2.0.3.18")
        if supports_switch:
            spike_safe_socket.send_scpi_command('MEM:DATA CONNAVAIL?')
            has_switch = spike_safe_socket.read_data(enable_logging)
            spikesafe_info.has_switch = False if has_switch == "FALSE" else True

        spike_safe_socket.send_scpi_command('SOUR0:FUNC:SHAP? LIST')
        supported_pulse_modes_list = spike_safe_socket.read_data(enable_logging)
        SpikeSafeInfoParser._parse_spikesafe_info_spikesafe_type(spikesafe_info, supported_pulse_modes_list)
        
        # Requires Release 3.8.0 (or Ethernet Processor 3.0.6.0 or later) to support this command
        spikesafe_info.supports_discharge_query = SpikeSafeInfoParser.compare_rev_version(spikesafe_info.version, "3.0.6.0")

        # Requires Release 3.12.9 (or Ethernet Processor 3.0.11.10 or later) to support this command
        spikesafe_info.supports_multiple_digitizer_commands = SpikeSafeInfoParser.compare_rev_version(spikesafe_info.version, "3.0.11.10")
        
        # Requires Release 3.8.1 (or Ethernet Processor 3.0.6.0 or later) to support this command
        spikesafe_info.supports_pulse_width_correction = SpikeSafeInfoParser.compare_rev_version(spikesafe_info.version, "3.0.6.0")

        return spikesafe_info

    @staticmethod
    def _query_float(socket: TcpSocket, cmd: str, log: bool) -> float:
        """
        Sends an SCPI command and parses the response as a float.

        Parameters
        ----------
        socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        cmd : str
            SCPI command to send
        log : bool
            Enables logging for socket communication

        Returns
        -------
        float
            Parsed float value from the response
        """
        socket.send_scpi_command(cmd, log)
        return float(socket.read_data(log))

    @staticmethod
    def _query_int_list(socket: TcpSocket, cmd: str, log: bool) -> list[int]:
        """
        Sends an SCPI command and parses the comma-separated response into a list of integers.

        Parameters
        ----------
        socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        cmd : str
            SCPI command to send
        log : bool
            Enables logging for socket communication

        Returns
        -------
        list of int
            List of parsed integers from the response
        """
        socket.send_scpi_command(cmd, log)
        data = socket.read_data(log)

        # Split by comma, strip whitespace, and parse to int if possible
        integers = []
        for s in data.split(','):
            s = s.strip()
            if s:
                try:
                    integers.append(int(s))
                except ValueError:
                    pass  # Ignore invalid entries

        return integers

    @staticmethod
    def _fetch_digitizer_info(
        spike_safe_socket: TcpSocket,
        spikesafe_info: SpikeSafeInfo,
        digitizer_functioning_card_number: str | None,
        enable_logging: bool
    ) -> None:
        """
        Queries digitizer info from SpikeSafe and returns a DigitizerInfo object.

        Parameters
        ----------
        spike_safe_socket : TcpSocket
            Socket object used to communicate with SpikeSafe
        spikesafe_info : SpikeSafeInfo
            SpikeSafeInfo object to which the DigitizerInfo will be added
        digitizer_functioning_card_number : str | None
            The functioning card number of the digitizer to query. If None, queries the single digitizer.
        enable_logging : bool
            Enables logging for socket communication
        """

        prefix = "VOLT" if digitizer_functioning_card_number is None else f"VOLT{digitizer_functioning_card_number}"

        spike_safe_socket.send_scpi_command(f'{prefix}:VER?', enable_logging)
        digitizer_version = spike_safe_socket.read_data(enable_logging)

        spike_safe_socket.send_scpi_command(f'{prefix}:DATA:HWRE?', enable_logging)
        digitizer_hardware_version = spike_safe_socket.read_data(enable_logging)

        spike_safe_socket.send_scpi_command(f'{prefix}:DATA:SNUM?', enable_logging)
        digitizer_serial_number = spike_safe_socket.read_data(enable_logging)

        spike_safe_socket.send_scpi_command(f'{prefix}:DATA:CDAT?', enable_logging)
        digitizer_last_cal_date = spike_safe_socket.read_data(enable_logging)

        minimum_aperture = SpikeSafeInfoParser._query_float(spike_safe_socket, f'{prefix}:APER? MIN', enable_logging)
        maximum_aperture = SpikeSafeInfoParser._query_float(spike_safe_socket, f'{prefix}:APER? MAX', enable_logging)
        minimum_trigger_delay = SpikeSafeInfoParser._query_float(spike_safe_socket, f'{prefix}:TRIG:DEL? MIN', enable_logging)
        maximum_trigger_delay = SpikeSafeInfoParser._query_float(spike_safe_socket, f'{prefix}:TRIG:DEL? MAX', enable_logging)
        voltage_ranges = SpikeSafeInfoParser._query_int_list(spike_safe_socket, f'{prefix}:RANG? LIST', enable_logging)

        digitizer_info = DigitizerInfo()
        digitizer_info.number = int(digitizer_functioning_card_number)
        digitizer_info.version = digitizer_version
        digitizer_info.hardware_version = digitizer_hardware_version
        digitizer_info.serial_number = digitizer_serial_number
        digitizer_info.last_calibration_date = digitizer_last_cal_date
        digitizer_info.minimum_aperture = minimum_aperture
        digitizer_info.maximum_aperture = maximum_aperture
        digitizer_info.minimum_trigger_delay = minimum_trigger_delay
        digitizer_info.maximum_trigger_delay = maximum_trigger_delay
        digitizer_info.voltage_ranges = voltage_ranges
        spikesafe_info.digitizer_infos.append(digitizer_info)

    @staticmethod
    def _parse_spikesafe_info_from_idn(spikesafe_info: SpikeSafeInfo, idn: str) -> None:
        spikesafe_info.board_type = SpikeSafeInfoParser._parse_board_type(idn)
        spikesafe_info.board_model = SpikeSafeInfoParser._parse_board_model(idn)

        spikesafe_info.version = SpikeSafeInfoParser._parse_300_or_400_version(idn)
        spikesafe_info.serial_number = SpikeSafeInfoParser._parse_300_or_400_serial_number(idn)
        spikesafe_info.hardware_version = SpikeSafeInfoParser._parse_300_or_400_hardware_revision(idn)
        spikesafe_info.cpld_version = SpikeSafeInfoParser._parse_300_or_400_cpld_version(idn)
        spikesafe_info.dsp_version = SpikeSafeInfoParser._parse_300_or_400_dsp_version(idn)
        spikesafe_info.last_cal_date = SpikeSafeInfoParser._parse_300_or_400_last_cal_date(idn)

    @staticmethod
    def _parse_board_type(idn: str) -> str:
        if "SpikeSafe Mini" in idn:
            return "SpikeSafe Mini"
        else:
            index = idn.find("SpikeSafe")
            board_type = idn[index:index + 13]
            return board_type
        
    @staticmethod
    def _parse_board_model(idn: str) -> str:
        index = idn.find("ModelNum:")
        length = 9

        if index == -1:
            index = idn.find("Model:")
            length = 6

        if index == -1:
            return "NA"
        else:
            return idn[index + length:].strip()
        
    @staticmethod
    def _parse_300_or_400_version(idn: str) -> str:
        index = idn.find("Rev") + 3
        semi = idn.find(";")
        version = idn[index:semi].strip()
        return version

    @staticmethod
    def _parse_300_or_400_serial_number(idn: str) -> str:
        index = idn.find("SN:") + 3
        comma = idn.find(",", index)
        serial_num = idn[index:comma].strip()
        return serial_num
    
    @staticmethod
    def _parse_300_or_400_cpld_version(idn: str) -> str:
        indices = SpikeSafeInfoParser._all_indexes_of(idn, "CPLD")
        cpld_versions = []

        for index in indices:
            semicolon = idn.find(";", index + 4)
            if semicolon == -1:
                semicolon = idn.find(",", index + 4)
            cpld_ver = idn[index + 4:semicolon].strip()
            cpld_versions.append(cpld_ver)

        if all(v == cpld_versions[0] for v in cpld_versions):
            return cpld_versions[0]
        else:
            return ",".join(cpld_versions)

    @staticmethod
    def _parse_300_or_400_hardware_revision(idn: str) -> str:
        index = idn.find("HwRev:") + 6
        comma = idn.find(",", index)
        hw_rev = idn[index:comma].strip()
        return hw_rev

    @staticmethod
    def _parse_300_or_400_dsp_version(idn: str) -> str:
        indices = SpikeSafeInfoParser._all_indexes_of(idn, "DSP")
        dsp_versions = []

        for index in indices:
            comma = idn.find(",", index + 3)
            dsp_ver = idn[index + 3:comma].strip()
            dsp_versions.append(dsp_ver)

        if all(v == dsp_versions[0] for v in dsp_versions):
            return dsp_versions[0]
        else:
            return ",".join(dsp_versions)

    @staticmethod
    def _parse_300_or_400_last_cal_date(idn: str) -> str:
        index = idn.find("Last Cal Date:") + 14
        comma = idn.find(",", index)
        last_cal = idn[index:comma].strip()
        return last_cal
        
    @staticmethod
    def _all_indexes_of(s: str, value: str) -> list[int]:
        if not value:
            raise ValueError("The string to find may not be empty")

        indexes = []
        index = 0

        while True:
            index = s.find(value, index)
            if index == -1:
                return indexes
            indexes.append(index)
            index += len(value)

    @staticmethod
    def _parse_spikesafe_info_spikesafe_type(spikesafe_info: SpikeSafeInfo, supported_pulse_modes_list: str) -> None:
        if spikesafe_info.zin_number.startswith("ZIN644"):
            if spikesafe_info.has_digitizer or spikesafe_info.has_switch:
                spikesafe_info.spikesafe_type = "SpikeSafe PSMU"
            else:
                spikesafe_info.spikesafe_type = "SpikeSafe 400 Mini PRF"
        else:

            if spikesafe_info.has_digitizer or spikesafe_info.has_switch:
                spikesafe_info.spikesafe_type = "SpikeSafe PSMU HC"
            elif "DCDYNAMIC" in supported_pulse_modes_list:
                spikesafe_info.spikesafe_type = "SpikeSafe 400 PRF"
            elif "PULSED" in supported_pulse_modes_list:
                spikesafe_info.spikesafe_type = "SpikeSafe 400 DCP"
            else:
                spikesafe_info.spikesafe_type = "SpikeSafe 400 DC"

    # function needed to determine method for quickly discharging the channel
    @staticmethod
    def compare_rev_version(rev_version: str, ref_version: str) -> bool:
        """
        Compares two revision version strings.

        Parameters
        ----------
        rev_version : str
            Revision version string to compare (e.g., "1.2.3")
        ref_version : str
            Reference version string to compare against (e.g., "1.2.0")

        Returns
        -------
        bool
            True if rev_version is greater than or equal to ref_version, False otherwise
        """
        # Split and convert to integers for segment-wise comparison
        rev_parts = list(map(int, rev_version.split('.')))
        ref_parts = list(map(int, ref_version.split('.')))
        return rev_parts >= ref_parts

def parse_spikesafe_info(spike_safe_socket: TcpSocket, enable_logging: bool | None = None) -> SpikeSafeInfo:
    """
    Obsolete: use SpikeSafeInfoParser.parse_spikesafe_info() instead
    """
    return SpikeSafeInfoParser.parse_spikesafe_info(spike_safe_socket, enable_logging)