import sys
import traceback
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout


def excepthook(exc_type, exc_value, exc_tb):
    with open("error_log.txt", "w") as f:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    sys.exit(1)


sys.excepthook = excepthook


def find_stlink_virtual_com_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'STMicroelectronics STLink Virtual COM Port' in port.description:
            return port.device
    return None


class SerialDataDisplay(QWidget):
    def __init__(self, port, baudrate, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate

        self.setWindowTitle("Odczyt danych z portu szeregowego")
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Etykiety kolumn
        voltage_label = QLabel('Napięcie')
        current_label = QLabel('Natężenie prądu')

        voltage_label.setStyleSheet("background-color: lightblue;")
        current_label.setStyleSheet("background-color: lightgreen;")

        voltage_label.setAlignment(Qt.AlignCenter)
        current_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(voltage_label, 0, 0)
        self.layout.addWidget(current_label, 0, 1)

        # Etykiety wartości
        self.voltage_label = QLabel("-")
        self.current_label = QLabel("-")

        self.voltage_label.setStyleSheet("background-color: lightblue;")
        self.current_label.setStyleSheet("background-color: lightgreen;")

        self.voltage_label.setAlignment(Qt.AlignCenter)
        self.current_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.voltage_label, 1, 0)
        self.layout.addWidget(self.current_label, 1, 1)

        # Indykatory flag
        self.flag_indicators = []
        indicator_layout = QVBoxLayout()
        for i in range(3):
            indicator = QLabel(str(i + 1))
            indicator.setFixedSize(40, 40)
            indicator.setAlignment(Qt.AlignCenter)
            indicator.setStyleSheet("background-color: green; border: 1px solid black; font-size: 16px;")
            self.flag_indicators.append(indicator)
            indicator_layout.addWidget(indicator)

        self.layout.addLayout(indicator_layout, 0, 2, 2, 1)

        # Tekst wyjaśniający
        explanation_label = QLabel("1 - Flaga 1, 2 - Flaga 2, 3 - Flaga 3")
        explanation_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(explanation_label, 2, 0, 1, 3)

        self.serial = serial.Serial(port, baudrate)
        self.receive_thread = SerialReceiveThread(self.serial, self.update_values)
        self.receive_thread.start()

    def update_values(self, values):
        if len(values) >= 5:
            self.voltage_label.setText(str(values[0]))
            self.current_label.setText(str(values[1]))

            flags = values[2:5]
            for i, flag in enumerate(flags):
                if flag == 1:
                    self.flag_indicators[i].setStyleSheet("background-color: red; border: 1px solid black; font-size: 16px;")
                else:
                    self.flag_indicators[i].setStyleSheet("background-color: green; border: 1px solid black; font-size: 16px;")

    def closeEvent(self, event):
        self.serial.close()
        event.accept()


class SerialReceiveThread(QThread):
    data_received = pyqtSignal(list)

    def __init__(self, serial, callback):
        super().__init__()
        self.serial = serial
        self.callback = callback

    def run(self):
        while True:
            data = self.serial.readline().decode('utf-8').strip()
            values = data.split(',')

            if len(values) >= 5:
                try:
                    values = [float(val) for val in values]
                    self.callback(values)
                except ValueError:
                    print("Błąd: Nie można przekształcić wartości na liczby")
                    continue


if __name__ == '__main__':
    app = QApplication(sys.argv)

    port = find_stlink_virtual_com_port()
    if port is not None:
        window = SerialDataDisplay(port, 115200)
        window.setGeometry(200, 200, 400, 200)
        window.show()
        sys.exit(app.exec_())
    else:
        print("Nie znaleziono urządzenia STMicroelectronics STLink Virtual COM Port")
