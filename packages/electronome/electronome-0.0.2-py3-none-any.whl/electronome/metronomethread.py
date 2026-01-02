#import time
from PySide6.QtCore import QThread, QWaitCondition, QMutex, Signal
import mainwin

class MetronomeThread(QThread):

    advance = Signal()

    def __init__(self, parent : mainwin.MainWin):
        super().__init__(parent)
        self._parent = parent    
        self._exiting = False
        self._sleep = 1
        self.advance.connect(parent.advance_beat)

    def set_bpm(self, bpm : int):
        self._sleep = int(1/bpm*60*1000)
        if (self.isRunning()):
            self._wait.wakeAll()

    def stop(self):
        self._exiting = True
        if (self.isRunning()):
            self._wait.wakeAll()

    def run(self):
        self._wait = QWaitCondition()
        self._mutex = QMutex()
        while self._exiting==False:
            #start_time = time.time()
            self.advance.emit()
            self._mutex.lock()
            #elapsed = time.time() - start_time
            self._wait.wait(self._mutex, self._sleep)
            self._mutex.unlock()
        self._exiting = False
