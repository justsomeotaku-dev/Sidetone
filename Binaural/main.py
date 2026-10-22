from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QScrollArea,
    QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer, Qt, Signal
from winmica import BackdropType, EnableMica, is_mica_supported
import sounddevice as sd
import sys
from binaural import start, stop, set_beat, set_carrier, set_volume
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

class UI(QMainWindow):
    status_changed = Signal(str)

    def __init__(self) -> None:
        """Initialize the UI."""

        super().__init__()

        self.listening = False # might change for a Signal later if unstable

        # Required for Mica Transparency on Windows
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        if is_mica_supported():
            hwnd = int(self.winId())
            EnableMica(hwnd, BackdropType.MICA)

        self.setWindowOpacity(0.997)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.setWindowTitle("Binaural Beat Generator")

        self.carrier_slider = QSlider(Qt.Orientation.Horizontal)
        self.carrier_slider.setRange(0, 600)
        self.carrier_slider.valueChanged.connect(set_carrier)
        self.carrier_slider.valueChanged.connect(self.update_hz_label)
        layout.addWidget(self.carrier_slider)

        self.beat_slider = QSlider(Qt.Orientation.Horizontal)
        self.beat_slider.setRange(0, 100)
        self.beat_slider.valueChanged.connect(set_beat)
        self.beat_slider.valueChanged.connect(self.update_hz_label)
        layout.addWidget(self.beat_slider)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0,10)
        self.volume_slider.valueChanged.connect(set_volume)
        self.volume_slider.valueChanged.connect(self.update_hz_label)
        layout.addWidget(self.volume_slider)

        self.start_button = QPushButton("Start listening")
        self.start_button.pressed.connect(self.on_listen)
        layout.addWidget(self.start_button)

        self.hz_label = QLabel("0 Hz Left | 0 Hz Right | 0 Hz Binaural | 0 Volume")
        layout.addWidget(self.hz_label)

        self.status_label = QLabel("...")
        layout.addWidget(self.status_label)
        self.status_changed.connect(self.status_label.setText)

    def update_hz_label(self):
        left_ear = self.carrier_slider.value()
        right_ear = left_ear + self.beat_slider.value()
        volume = self.volume_slider.value()
        
        self.hz_label.setText(f"{left_ear} Hz Left | {right_ear} Hz Right | {right_ear-left_ear} Hz Binaural | {volume} Volume")

    def on_listen(self):
        if not self.listening:
            start(
                self.status_changed.emit
            )
            self.start_button.setText("Stop listening")
            self.listening = True
        else:
            stop()
            self.start_button.setText("Start listening")
            self.listening = False


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = UI()
    window.show()

    sys.exit(app.exec())