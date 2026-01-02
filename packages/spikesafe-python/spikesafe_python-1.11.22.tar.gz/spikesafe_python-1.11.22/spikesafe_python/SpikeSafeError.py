# Goal: express errors returned from the SpikeSafe error queue as Python exceptions

class SpikeSafeError(Exception):
    """
    Exception raised for SpikeSafe errors returned by the SYSTem:ERRor? query

    Attributes
    ----------
    code: int
        Numerical code representing the specific SpikeSafe error
    message: str | None
        Explanation of the SpikeSafe error
    channel_list: list[int]
            A list of channels affected by a given error (if applicable)
    full_error: str | None
        The full error query response text
    """

    code: int
    message: str | None
    channel_list: list[int]
    full_error: str | None

    def __init__(self, code: int, message: str, channel_list: list[int] | None = None, full_error: str | None = None) -> None:
        self.code = code
        self.message = message
        self.channel_list = channel_list if channel_list is not None else []
        self.full_error = full_error

    def __str__(self) -> str:
        if self.full_error:
            return f"SpikeSafe Error: {self.full_error}"
        else:
            return f"SpikeSafe Error: {self.message}"