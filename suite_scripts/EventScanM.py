from TimeScanM import *


class EventScan(TimeScanM):
    def __init__(self):
        super().__init__()

    def getScanValue(self, foo, bar):
        return self.nGoodEvents


if __name__ == "__main__":
    a = EventScan()
    super(EventScan, a).main()
