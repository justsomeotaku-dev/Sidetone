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
from listen import listen, stop, set_volume
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

        self.setWindowTitle("Sidetone")

        self.api_dropdown = QComboBox()
        self.api_dropdown.currentIndexChanged.connect(self.populate_io)
        self.input_dropdown = QComboBox()
        self.output_dropdown = QComboBox()

        self.populate_apis()
        self.populate_io()

        layout.addWidget(self.api_dropdown)
        layout.addWidget(self.input_dropdown)
        layout.addWidget(self.output_dropdown)

        self.listen_button = QPushButton("Start listening")
        self.listen_button.pressed.connect(self.on_listen)
        layout.addWidget(self.listen_button)

        self.status_label = QLabel("...")
        layout.addWidget(self.status_label)
        self.status_changed.connect(self.status_label.setText)

        volume_slider = QSlider()
        volume_slider.setOrientation(Qt.Orientation.Horizontal)
        volume_slider.setRange(0,3)
        volume_slider.valueChanged.connect(set_volume)
        layout.addWidget(volume_slider)

    def on_listen(self):
        if not self.listening:
            listen(
                self.input_dropdown.currentData(),
                self.output_dropdown.currentData(),
                self.status_changed.emit
            )
            self.listen_button.setText("Stop listening")
            self.listening = True
        else:
            stop()
            self.listen_button.setText("Start listening")
            self.listening = False

    def populate_apis(self):
        try:
            self.api_dropdown.clear()
            for index, api in enumerate(sd.query_hostapis()):
                if api["name"] != "Windows WDM-KS":
                    self.api_dropdown.addItem(api["name"], index)

            self.api_dropdown.setCurrentIndex(sd.default.hostapi)
        except Exception as e:
            print(f"Couldn't load apis: {e}")

    def populate_io(self):
        self.input_dropdown.clear()
        self.output_dropdown.clear()
    
        try:
            api_index = self.api_dropdown.currentData()
            api = sd.query_hostapis(api_index)

            for device_id in api["devices"]:
                device = sd.query_devices(device_id)
                name = device["name"]
                inputs = device["max_input_channels"]
                outputs = device["max_output_channels"]

                if inputs > 0:
                    self.input_dropdown.addItem(
                        f"{name} ({inputs} ch)", device_id
                    )
                if outputs > 0:
                    self.output_dropdown.addItem(
                        f"{name} ({outputs} ch)", device_id
                    )
                    
        except Exception as e:
            print(f"Could not load audio devices: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = UI()
    window.show()

    sys.exit(app.exec())

# wdms-ks is erroring, incompatible, so i removed it from the dropdown
# add Signal to prevent button spam
# use the sample rate of each device instead of hardcoding channels and samplerate