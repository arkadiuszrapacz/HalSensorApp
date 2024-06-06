import sys
import traceback
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel


def excepthook(exc_type, exc_value, exc_tb):
    with open("error_log.txt", "w") as f:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    sys.exit(1)


sys.excepthook = excepthook


def find_stlink_virtual_com_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'USB Serial Port' in port.description:
            return port.device
    return None


class SerialDataDisplay(QWidget):
    def __init__(self, port, baudrate, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate

        self.setWindowTitle("Hall Sensor Application")
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Etykiety kolumn
        voltage_label = QLabel('Voltage [mV]')
        current_label = QLabel('Current [mA]')
        pwm_label = QLabel('PWM [%]')
        diag1_label = QLabel('Diag 1')
        diag2_label = QLabel('Diag 2')

        voltage_label.setStyleSheet("background-color: lightblue;")
        current_label.setStyleSheet("background-color: lightgreen;")
        pwm_label.setStyleSheet("background-color: thistle;")
        diag1_label.setStyleSheet("background-color: lightsalmon;")
        diag2_label.setStyleSheet("background-color: lightsalmon;")

        voltage_label.setAlignment(Qt.AlignCenter)
        current_label.setAlignment(Qt.AlignCenter)
        pwm_label.setAlignment(Qt.AlignCenter)
        diag1_label.setAlignment(Qt.AlignCenter)
        diag2_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(voltage_label, 0, 0)
        self.layout.addWidget(current_label, 0, 1)
        self.layout.addWidget(pwm_label, 0, 2)
        self.layout.addWidget(diag1_label, 0, 3)
        self.layout.addWidget(diag2_label, 0, 4)

        # Etykiety wartości
        self.voltage_label = QLabel("-")
        self.current_label = QLabel("-")
        self.pwm_label = QLabel("-")
        self.diag1_label = QLabel("-")
        self.diag2_label = QLabel("-")

        self.voltage_label.setStyleSheet("background-color: lightblue;")
        self.current_label.setStyleSheet("background-color: lightgreen;")
        self.pwm_label.setStyleSheet("background-color: thistle;")
        self.diag1_label.setStyleSheet("background-color: lightsalmon;")
        self.diag2_label.setStyleSheet("background-color: lightsalmon;")

        self.voltage_label.setAlignment(Qt.AlignCenter)
        self.current_label.setAlignment(Qt.AlignCenter)
        self.pwm_label.setAlignment(Qt.AlignCenter)
        self.diag1_label.setAlignment(Qt.AlignCenter)
        self.diag2_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.voltage_label, 1, 0)
        self.layout.addWidget(self.current_label, 1, 1)
        self.layout.addWidget(self.pwm_label, 1, 2)
        self.layout.addWidget(self.diag1_label, 1, 3)
        self.layout.addWidget(self.diag2_label, 1, 4)

        # Tekst wyjaśniający
        explanation_label = QLabel("Diag 1, 2 - diagnostyka (0 - false, 1 - true)")
        explanation_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(explanation_label, 2, 0, 1, 5)

        self.setFixedSize(600, 200)

        self.serial = serial.Serial(port, baudrate)
        self.receive_thread = SerialReceiveThread(self.serial, self.update_values)
        self.receive_thread.start()

    # Aktualizacja wskazań wartości / indykatorów
    def update_values(self, values):
        if len(values) >= 5:
            self.voltage_label.setText(str(values[0]))
            self.current_label.setText(str(values[1]))
            self.pwm_label.setText(str(values[4]))
            self.diag1_label.setText(str(values[3]))
            self.diag2_label.setText(str(values[2]))

            # Zmiana koloru wypełnienia indykatorów na podstawie wartości
            if values[3] == 0:
                self.diag1_label.setStyleSheet("background-color: red;")
            else:
                self.diag1_label.setStyleSheet("background-color: green;")

            if values[2] == 0:
                self.diag2_label.setStyleSheet("background-color: red;")
            else:
                self.diag2_label.setStyleSheet("background-color: green;")

            pwm_value = values[4]
            if pwm_value <= 20:
                self.pwm_label.setStyleSheet("background-color: red;")
            elif pwm_value > 20 and pwm_value <= 50:
                self.pwm_label.setStyleSheet("background-color: gray;")
            elif pwm_value > 50 and pwm_value <= 80:
                self.pwm_label.setStyleSheet("background-color: lightblue;")
            elif pwm_value > 80 and pwm_value <= 99:
                self.pwm_label.setStyleSheet("background-color: cyan;")
            else:
                self.pwm_label.setStyleSheet("background-color: green;")

    def closeEvent(self, event):
        self.serial.close()
        event.accept()

# Zbieranie oraz rozdzielanie danych z portu szeregowego
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
        window.setGeometry(200, 200, 600, 200)
        window.show()
        sys.exit(app.exec_())
    else:
        print("Nie znaleziono urządzenia USB Serial Port")
