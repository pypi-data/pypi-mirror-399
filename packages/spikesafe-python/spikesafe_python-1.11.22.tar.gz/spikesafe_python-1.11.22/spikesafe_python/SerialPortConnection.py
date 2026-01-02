from __future__ import annotations
import serial
import threading
import logging

class SerialPortConnection:
    """
    Class to manage a Serial Port connection to a device.

    Attributes
    ----------
    port : serial.Serial | None
        The serial port object.
    port_name : str
        The name of the serial port (e.g., 'COM3').
    terminator : str
        The line terminator for the serial connection.
    enable_logging : bool
        Flag to enable logging.
    default_log_level : int
        Default logging level.
    timeout_milliseconds : int
        Timeout in milliseconds for serial port operations.

    Methods
    -------
    connect(com_port: str, baudrate: int = 9600, parity: str = serial.PARITY_NONE, stopbits: int = serial.STOPBITS_ONE, bytesize: int = serial.EIGHTBITS, xonxoff: bool = True, terminator: str = '\n') -> None
        Connects to the specified serial port with given parameters.
    disconnect() -> None
        Disconnects from the serial port.
    write(command: str, enable_logging: bool | None = None) -> None
        Writes a command to the serial port.
    read_data(enable_logging: bool | None = None) -> str
        Reads data from the serial port.
    """

    SERIAL_PORT_TIMEOUT = 3000  # milliseconds

    def __init__(self) -> None:
        """
        Initializes a SerialPortConnection instance.
        """
        self.port: serial.Serial | None = None
        self.port_name: str = ""
        self.terminator: str = '\n'
        self.enable_logging: bool = False
        self.default_log_level: int = logging.INFO
        self._timeout_milliseconds: int = self.SERIAL_PORT_TIMEOUT
        self._write_lock = threading.Lock()
        self._query_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    @property
    def timeout_milliseconds(self) -> int:
        """
        Gets the timeout in milliseconds for serial port operations.

        Returns
        -------
        int
            Timeout in milliseconds.
        """
        return self._timeout_milliseconds

    @timeout_milliseconds.setter
    def timeout_milliseconds(self, value: int) -> None:
        """
        Sets the timeout in milliseconds for serial port operations.

        Parameters
        ----------
        value : int
            Timeout in milliseconds.
        """
        self._timeout_milliseconds = value
        if self.port is not None:
            self.port.timeout = value / 1000.0
            self.port.write_timeout = value / 1000.0

    def connect(
        self,
        com_port: str,
        baudrate: int = 9600,
        parity: str = serial.PARITY_NONE,
        stopbits: int = serial.STOPBITS_ONE,
        bytesize: int = serial.EIGHTBITS,
        xonxoff: bool = True,
        terminator: str = '\n'
    ) -> None:
        """
        Connects to a Serial Port for local communication to a SpikeSafe.

        Parameters
        ----------
        com_port : str
            COM port of the SpikeSafe (e.g., 'COM3').
        baudrate : int, optional
            Baud rate for the serial connection (default is 9600).
        parity : str, optional
            Parity for the serial connection (default is serial.PARITY_NONE).
        stopbits : int, optional
            Stop bits for the serial connection (default is serial.STOPBITS_ONE).
        bytesize : int, optional
            Byte size for the serial connection (default is serial.EIGHTBITS).
        xonxoff : bool, optional
            Software flow control (default is True).
        terminator : str, optional
            Line terminator for the serial connection (default is '\n').

        Raises
        ------
        IOError
            On any error.
        """
        try:
            if self.enable_logging:
                self.logger.log(self.default_log_level, self._get_formatted_log_message("Connecting..."))
            self.port_name = com_port
            self.terminator = terminator
            self.port = serial.Serial(
                port=com_port,
                baudrate=baudrate,
                parity=parity,
                bytesize=bytesize,
                stopbits=stopbits,
                xonxoff=xonxoff,
                timeout=self._timeout_milliseconds / 1000.0,
                write_timeout=self._timeout_milliseconds / 1000.0
            )
        except Exception as e:
            raise IOError(f"Error connecting to Serial Port at {com_port}, {e}")

    def disconnect(self) -> None:
        """
        Disconnects from the Serial Port.

        Raises
        ------
        IOError
            On any error

        """
        try:
            if self.enable_logging:
                self.logger.log(self.default_log_level, self._get_formatted_log_message("Disconnecting..."))
            if self.port is not None:
                self.port.close()
            self.port_name = ""
        except Exception as e:
            raise IOError(f"Error disconnecting from Serial Port at {self.port_name}, {e}")

    def write(self, command: str, enable_logging: bool | None = None) -> None:
        """
        Writes a command to the Serial Port.
        
        Parameters
        ----------
        command : str
            Command to write to the Serial Port
        enable_logging : bool, optional
            Whether to enable logging for this command (default is None, which uses the instance's enable_logging setting)

        Raises
        ------
        IOError
            On any error
        """
        if enable_logging is None:
            enable_logging = self.enable_logging
        self._write_internal(command, enable_logging)

    def _write_internal(self, command, enable_logging):
        try:
            with self._write_lock:
                if enable_logging:
                    self.logger.log(self.default_log_level, self._get_formatted_log_message(f"Writing command: {command}"))
                self.port.write((command + self.terminator).encode())
        except Exception as e:
            raise IOError(f"Error writing command to Serial Port at {self.port_name}, {e}")

    def read_data(self, enable_logging: bool | None = None) -> str:
        """
        Reads data from the Serial Port.

        Parameters
        ----------
        enable_logging : bool, optional
            Whether to enable logging for this command (default is None, which uses the instance's enable_logging setting)

        Returns
        -------
        str
            Data read from the Serial Port

        Raises
        ------
        IOError
            On any error
        """
        if enable_logging is None:
            enable_logging = self.enable_logging
        return self._read_internal(enable_logging)

    def _read_internal(self, enable_logging):
        try:
            with self._query_lock:
                query_return = self.port.readline().decode().strip()
                if enable_logging:
                    self.logger.log(self.default_log_level, self._get_formatted_log_message(f"Reading Data reply: {query_return}"))
                return query_return
        except Exception as e:
            raise IOError(f"Error reading command from Serial Port at {self.port_name}, {e}")

    def _get_formatted_log_message(self, message):
        return f"SerialPort {self.port_name}. {message}"