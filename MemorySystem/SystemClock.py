class SystemClock:
    """
    Simulates a discrete clock for advancing and tracking the simulation time.

    This class is used to advance and check "simulated time".
    The transmitter waits for a transmission time.
    The detector check the current time.
    """
    def __init__(self) -> None:
        """
        Initializes the simulation clock to time zero.
        """
        self.__time = 0

    @property
    def now(self) -> float:
        """
        Get the current simulation time.

        Returns:
            int: The current time value (in simulation units - seconds).
        """
        return self.__time

    def wait_until(self, target_time: float) -> None:
        """
        Advances the simulation clock to the specified time.

        Args:
            target_time (int): The time to advance to.
            Must be greater than or equal to the current time.

        Raises:
            AssertionError: If target_time is earlier than the current simulation time (only if __debug__ is True).
        """
        if __debug__:
            assert target_time >= self.__time

        self.__time = target_time
