import os
from typing import List
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, \
    QSpinBox, QCheckBox, QPushButton, QApplication
from PySide6.QtCore import QSize, Qt, QPoint, Slot, QUrl
from PySide6.QtGui import QResizeEvent, QFont, QMouseEvent, QFontMetrics, \
    QKeyEvent
from PySide6.QtMultimedia import QSoundEffect
import qdarktheme
from config import Config
import time

class MainWin(QWidget):

    emphasized_color = "rgb(46, 163, 16)"
    unemphasized_color = "rgb(225, 229, 232)"
    emphasized_inactive_color = "rgb(60, 84, 53)"
    unemphasized_inactive_color = "rgb(84, 85, 87)"

    fontSize = 18

    def __init__(self, conf : Config):
        import metronomethread
        super().__init__()
        self.config = conf

        self._beat_widgets : List[QLabel] = []
        self._beat_emphasized : List[bool] = []
        self._beats_width = 0
        self._beats_height = 0
        self._first_draw = True
        self._beat_pixel_size = 0
        self._thread : metronomethread.MetronomeThread = \
            metronomethread.MetronomeThread(self)

        self.setMinimumSize(QSize(465, 230))

        # create audio 
        path = os.path.dirname(metronomethread.__file__)
        low_filename = os.path.join(path, "Perc_Can_lo.wav")
        high_filename = os.path.join(path, "Perc_Can_hi.wav")
        low = self.config.get("low")
        high = self.config.get("high")
        if (low is not None and low != "_builtin_"):
            if (os.path.isfile(low)):
                print("Error:", low, "does not exist. Exiting")
                QApplication.exit()
            low_filename = low
        if (high is not None and low != "_builtin_"):
            if (os.path.isfile(high)):
                print("Error:", high, "does not exist. Exiting")
                QApplication.exit()
            high_filename = high
        self._high_wav = QSoundEffect()
        self._high_wav.setSource(QUrl.fromLocalFile(high_filename))
        self._low_wav = QSoundEffect()
        self._low_wav.setSource(QUrl.fromLocalFile(low_filename))

        # create layout

        self._top_vlayout = QVBoxLayout()
        self._topcontrols_hlayout = QHBoxLayout()
        self._beats_hlayout = QHBoxLayout()
        self._bottomcontrols_hlayout = QHBoxLayout()

        self._top_vlayout.addLayout(self._topcontrols_hlayout, 0)
        self._top_vlayout.addLayout(self._beats_hlayout, 1)
        self._top_vlayout.addLayout(self._bottomcontrols_hlayout, 0)
        self.setLayout(self._top_vlayout)

        #QApplication.setStyle("Fusion")
        qdarktheme.setup_theme("dark") # type: ignore
        self.setWindowTitle("Electronome")
        size = conf.get("size")
        if (size is not None and "x" in size):
            try:
                size1 = size.split("x")
                self.resize(int(size1[0]), int(size1[1]))
            except Exception as e:
                print(e)
                self.resize(200, 120)
        else:
            self.resize(200, 100)

        # BPM label
        bpm_label = QLabel("BPM")
        self._topcontrols_hlayout.addWidget(bpm_label)
        font = bpm_label.font()
        font.setPixelSize(self.fontSize)
        bpm_label.setFont(font)

        # BPM spin box
        self._bpm_spinbox = QSpinBox()
        font = self._bpm_spinbox.font()
        font.setPixelSize(self.fontSize)
        self._bpm_spinbox.setFont(font)
        bpm = self.config.get("bpm")
        if (bpm is None):
            bpm = "60"
        try:
            bpm = int(bpm)
        except:
            print("Warning: invalid bpm " + bpm)
            bpm = 60
        self._bpm_spinbox.setMinimum(1)
        self._bpm_spinbox.setMaximum(360)
        self._bpm_spinbox.setValue(bpm)
        self._bpm_spinbox.setFixedWidth(60)
        self._topcontrols_hlayout.addWidget(self._bpm_spinbox)
        if (conf.get_boolean("half")):
            self._thread.set_bpm(bpm*2)
        else:
            self._thread.set_bpm(bpm)
        self._bpm_spinbox.valueChanged.connect(self.update_bpm)

        # Beats per bar
        bpb_label = QLabel("Beats/bar")
        self._topcontrols_hlayout.addWidget(bpb_label)
        font = bpb_label.font()
        font.setPixelSize(self.fontSize)
        bpb_label.setFont(font)

        beats_per_bar = self.config.get("beats")
        if beats_per_bar is None:
            beats_per_bar = "4"
        try:
            beats_per_bar = int(beats_per_bar)
        except:
            print("Warning: invalid beats " + beats_per_bar)
            beats_per_bar = 4
        self._beats_spinbox = QSpinBox()
        font = self._beats_spinbox.font()
        font.setPixelSize(self.fontSize)
        self._beats_spinbox.setFont(font)
        self._beats_spinbox.setFixedWidth(50)
        self._beats_spinbox.setMinimum(1)
        self._beats_spinbox.setMaximum(50)
        self._beats_spinbox.setValue(beats_per_bar)
        self._beats_spinbox.setFixedWidth(50)
        self._beats_spinbox.valueChanged.connect(self.update_beats)

        self._topcontrols_hlayout.addWidget(self._beats_spinbox)

        # Half beat checkbox
        self._half_check = QCheckBox("Half Beat")
        font = self._half_check.font()
        font.setPixelSize(self.fontSize)
        self._half_check.setFont(font)
        self._half_check.setChecked(self.config.get_boolean("half"))
        self._half_check.checkStateChanged.connect(self.update_beats)
        self._topcontrols_hlayout.addWidget(self._half_check)

        self._topcontrols_hlayout.addStretch(1)

        # Start/Stop Button
        self._started = False
        self._current_beat = -1
        self._start_stop_button = QPushButton("Start")
        font = self._start_stop_button.font()
        font.setPixelSize(self.fontSize)
        self._start_stop_button.setFont(font)
        self._bottomcontrols_hlayout.addStretch(1)
        self._bottomcontrols_hlayout.addWidget(self._start_stop_button)
        self._bottomcontrols_hlayout.addStretch(1)
        self._start_stop_button.clicked.connect(self.start_stop_clicked)

    def resizeEvent(self, event : QResizeEvent):
        self.config.set("size", str(event.size().width()) + "x" + \
                         str(event.size().height()))
        self.calc_beats_size()
        if self._first_draw:
            self._first_draw = False
            self.make_beat_widgets()
            self.add_beat_widgets()
        else:
            self.update_beats_size()

    def start_stop_clicked(self):
        if (self._started):
            self._started = False
            self._current_beat = -1
            self._start_stop_button.setText("Start")
            self._beats_spinbox.setEnabled(True)
            self._half_check.setEnabled(True)
            self._thread.stop()
        else:
            self._started = True
            self._start_stop_button.setText("Stop")
            self._beats_spinbox.setEnabled(False)
            self._half_check.setEnabled(False)
            self._thread.start()
        for i in range(len(self._beat_widgets)):
            color = self.unemphasized_inactive_color
            if (self._beat_emphasized[i]):
                color = self.emphasized_inactive_color
            w = self._beat_widgets[i]
            w.setStyleSheet(f"QLabel {{ color : {color}; }}")
        QApplication.processEvents() 

    def remove_beat_widgets(self):
        while ((child := self._beats_hlayout.takeAt(0)) != None): # type: ignore
            w = child.widget()
            if w:
                w.deleteLater()
        self._beat_widgets = []
        self._beat_emphasized = []


    def update_beats_size(self):
        if (len(self._beat_widgets) == 0):
            return
        num_beats = self._beats_spinbox.value()
        if (self._half_check.isChecked()):
            num_beats *= 2
        max_width = (self._beats_width / num_beats)-10
        max_height = self._beats_height - 30
        max_size = max_width if max_width < max_height else max_height
        max_size = int(max_size)
        self._beat_pixel_size  = max_size
        font = self._beat_widgets[0].font()
        font.setPixelSize(max_size)
        for w in self._beat_widgets:
            w.setFont(font)

    def make_beat_widgets(self):
        emphasized = self.config.get("emphasize")
        if (emphasized == None):
            emphasized = ""
        emphasized = emphasized.split(",")
        self._beat_widgets = []
        self._beat_emphasized = []
        num_beats = self._beats_spinbox.value()
        actiual_num_beats = num_beats
        if (self._half_check.isChecked()):
            num_beats *= 2
        max_width = (self._beats_width / num_beats)-10
        max_height = self._beats_height - 30
        max_size = max_width if max_width < max_height else max_height
        max_size = int(max_size)
        self._beat_pixel_size  = max_size

        font = QFont()
        for i in range(actiual_num_beats):
            beat = QLabel(str(i+1))
            beat.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if (i == 0):
                font = beat.font()
                font.setPixelSize(max_size)
            beat.setFont(font)
            beat_color = self.unemphasized_inactive_color
            if (str(i+1) in emphasized):
                self._beat_emphasized.append(True)
                beat_color = self.emphasized_inactive_color
            else:
                self._beat_emphasized.append(False)
            beat.setStyleSheet(f"QLabel {{ color : {beat_color}; }}")
            self._beat_widgets.append(beat)

            if (self._half_check.isChecked()):
                beat = QLabel("+")
                beat.setFont(font)
                beat.setAlignment(Qt.AlignmentFlag.AlignCenter)
                beat_color = self.unemphasized_inactive_color
                if (str(i+1)+"+" in emphasized):
                    self._beat_emphasized.append(True)
                    beat_color = self.emphasized_inactive_color
                else:
                    self._beat_emphasized.append(False)
                beat.setStyleSheet(f"QLabel {{ color : {beat_color}; }}")
                self._beat_widgets.append(beat)

    def add_beat_widgets(self):
        i = 0
        for w in self._beat_widgets:
            self._beats_hlayout.addWidget(w)
            self._beats_hlayout.setStretch(i, 1)
            i += 1

    def calc_beats_size(self):
        g = self._beats_hlayout.geometry()
        self._beats_width = g.width()
        self._beats_height = g.height()

    def update_beats(self):
        num_beats = self._beats_spinbox.value()
        half = self._half_check.isChecked()
        self.config.set("beats", str(num_beats))
        self.config.set("half", str(half))
        self.remove_beat_widgets()
        self.make_beat_widgets()
        self.add_beat_widgets()
        self.update_bpm()

    def update_bpm(self):
        bpm = self._bpm_spinbox.value()
        if (bpm < 1):
            return
        half = self._half_check.isChecked()
        self.config.set("bpm", str(bpm))
        if (half):
            bpm *= 2
        self._thread.set_bpm(bpm)

    def next_beat_is_emphasized(self):
        if (self._current_beat == len(self._beat_emphasized)-1):
            return self._beat_emphasized[0]
        else:
            return self._beat_emphasized[self._current_beat+1]

    @Slot()
    def advance_beat(self):
        next_is_high = self.next_beat_is_emphasized()
        if (self._current_beat == len(self._beat_widgets)-1):
            self._current_beat = 0
        else:
            self._current_beat += 1
        for i in range(len(self._beat_widgets)):
            if (i == self._current_beat):
                color = self.unemphasized_color
                if (self._beat_emphasized[i]):
                    color = self.emphasized_color
            else:
                color = self.unemphasized_inactive_color
                if (self._beat_emphasized[i]):
                    color = self.emphasized_inactive_color
            w = self._beat_widgets[i]
            w.setStyleSheet(f"QLabel {{ color : {color}; }}")

        wav = self._low_wav # type: ignore
        if next_is_high:
            wav = self._high_wav # type: ignore
        #self.advance.emit()
        wav.play() # type: ignore

    def mouseReleaseEvent(self, event : QMouseEvent ):
        super().mouseReleaseEvent(event)
        widget = self.childAt(event.x(), event.y())
        if (widget is None):
            return
        found = False
        text_width = 0
        text_height = 0
        text = ""
        idx = 0
        for w in self._beat_widgets:
            if w == widget:
                found = True
                font = w.font()
                fm = QFontMetrics(font)
                text = w.text()
                rect = fm.boundingRect(text)
                text_width = rect.width()
                text_height = rect.height()
                break
            idx += 1
        if (not found):
            return
        center_pos = widget.mapToParent(QPoint(int(widget.size().width()/2),int(widget.size().height()/2)))
        left = center_pos.x() - text_width/2
        right = center_pos.x() + text_width/2
        top = center_pos.y() - text_height/2
        bottom = center_pos.y() + text_height/2
        click_y = event.y() #- center_pos.y()
        click_x = event.x() #- center_pos.x()
        if (click_x < left or click_x > right or \
                click_y < top or click_y > bottom):
            return
        beat_color = ""
        if (self._beat_emphasized[idx]):
            self._beat_emphasized[idx] = False
            if (self._current_beat == idx):
                beat_color = self.unemphasized_color
            else:
                beat_color = self.unemphasized_inactive_color
        else:
            self._beat_emphasized[idx] = True
            if (self._current_beat == idx):
                beat_color = self.emphasized_color
            else:
                beat_color = self.emphasized_inactive_color

        widget.setStyleSheet(f"QLabel {{ color : {beat_color}; }}")
        self.save_emphasized()


    def save_emphasized(self):
        emphasized : List[str] = []
        if (self._half_check.isChecked()):
            for i in range(len(self._beat_emphasized)):
                if (self._beat_emphasized[i]):
                    s = str(int(i/2)+1)
                    if (i % 2 == 1):
                        s += "+"
                    emphasized.append(s)
        else:
            for i in range(len(self._beat_emphasized)):
                if (self._beat_emphasized[i]):
                    s = str(int(i)+1)
                    emphasized.append(s)
        self.config.set("emphasize",",".join(emphasized))
        
    def keyReleaseEvent(self, event : QKeyEvent):
        if (event.nativeVirtualKey() == 1):
            self.start_stop_clicked()

    def quit(self):
        if (self._thread.isRunning()):
            self._thread.stop()
            while (self._thread.isRunning()):
                time.sleep(0.1)
        QApplication.exit()

