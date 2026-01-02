# Copyright (c) 2024 Matthew Baker.  All rights reserved.  Licenced under the
# Apache Licence 2.0.  See LICENSE file
import sys
import signal
from PySide6.QtWidgets import QApplication
import mainwin

from config import Config

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    conf = Config()
    app = QApplication([])
    window = mainwin.MainWin(conf)
    window.show()
    app.exec()
    window.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
