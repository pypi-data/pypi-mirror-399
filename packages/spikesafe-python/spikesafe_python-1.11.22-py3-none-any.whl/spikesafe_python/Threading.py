import time

class Threading:
    """
    Class for thread-related utilities.
    
    Methods
    -------
    wait(wait_time: float, os_timer_resolution_offset_time: float = 0, current_time: Callable[[], float] = time.perf_counter) -> None
        Suspends the current thread for a specified amount of time.
    """

    @staticmethod
    def wait(
        wait_time: float,
        os_timer_resolution_offset_time: float = 0,
        current_time: float = time.perf_counter()
    ) -> None:
        """
        Suspends the current thread for a specified amount of time.

        Parameters
        ----------
        wait_time: float
            Wait time in seconds to suspend the current thread.
        os_timer_resolution_offset_time: float, optional
            The offset time in seconds to add to wait_time due to the operating system timer resolution limit. Default is 0.
        current_time: float, optional
            The current time in seconds. Default is time.perf_counter(), which is the result from a high resolution clock
        """
        now = current_time
        end = now + wait_time + os_timer_resolution_offset_time
        while now < end:
            now = time.perf_counter()

def wait(
    wait_time: float,
    os_timer_resolution_offset_time: float = 0,
    current_time: float = time.perf_counter()
) -> None:
    """
    Obsolete: use Threading.wait() instead
    """
    return Threading.wait(wait_time, os_timer_resolution_offset_time, current_time)