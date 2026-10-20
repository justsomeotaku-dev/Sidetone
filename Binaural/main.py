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

        carrier_slider = QSlider(Qt.Orientation.Horizontal)
        carrier_slider.setRange(0, 600)
        carrier_slider.valueChanged.connect(set_carrier)
        layout.addWidget(carrier_slider)

        beat_slider = QSlider(Qt.Orientation.Horizontal)
        beat_slider.setRange(0, 100)
        beat_slider.valueChanged.connect(set_beat)
        layout.addWidget(beat_slider)

        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0,10)
        volume_slider.valueChanged.connect(set_volume)
        layout.addWidget(volume_slider)

        self.start_button = QPushButton("Start listening")
        self.start_button.pressed.connect(self.on_listen)
        layout.addWidget(self.start_button)

        self.status_label = QLabel("...")
        layout.addWidget(self.status_label)
        self.status_changed.connect(self.status_label.setText)

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