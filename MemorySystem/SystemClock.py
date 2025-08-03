

class SystemClock:
    def __init__(self) -> None:
        self.__time = 0

    @property
    def now(self) -> int:
        return self.__time

    def wait_until(self, target_time) -> None:

        if __debug__:
            assert target_time >= self.__time

        self.__time = target_time
