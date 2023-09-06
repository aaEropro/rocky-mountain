from PySide6.QtCore import QTimer, QObject, Signal
import time


class ReadTimer(QObject):

    def __init__(self, parent:QObject=None):
        super().__init__(parent)

        self.time_intervals = []

        self.start_time = None
        self.warmup = False
        self.event_happened = False
        self.active_timer = False
        self.timer = QTimer(self)


    def activate(self):
        ''' the activation of the timer. '''

        self.warmup = True
        self.start_time = time.time()
        self.active_timer = True
        self.timer.singleShot(120000, self.offTimer)    # 2 min warmup
        print('timer activated.')


    def signalEventHappened(self):
        ''' signal that an event_happened has occured. '''

        if not self.active_timer:
            self.activate()
        else:
            self.event_happened = True
            # print('event happened.')


    def offTimer(self) -> None:
        # print(self.warmup, self.event_happened)
        if self.warmup and self.event_happened:    # ended warmup and something happened inside the editor
            self.warmup = False
            self.event_happened = False
            self.timer.singleShot(90000, self.offTimer)    # 1.5 min pause between checks
            print('ended warmup, event(s) happened, continuing...')

        elif self.warmup and (not self.event_happened):    # ended warmup and nothing happened inside the editor
            self.active_timer = False
            self.warmup = False
            print('warmup failed, timeout.')

        elif self.event_happened:    # ended timer and something happened inside the editor
            self.event_happened = False
            self.timer.singleShot(90000, self.offTimer)
            print('event(s) happened, continuing...')

        else:    # ended timer and nothing happened inside the editor
            self.active_timer = False
            if self.start_time is not None:
                self.time_intervals.append((self.start_time, time.time()))
                self.start_time = time.time()
            print(f'timeout, {self.time_intervals}')


    def getReadTime(self) -> list:
        ''' returns a list of tuples containing start times and end times. '''
        
        if self.warmup:
            return []
        if self.active_timer:
            return [*self.time_intervals, (self.start_time, time.time())]
        return self.time_intervals