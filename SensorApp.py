import sys
import traceback
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel

def excepthook(exc_type, exc_value, exc_tb):
    with open("error_log.txt", "w") as f:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    sys.exit(1)

sys.excepthook = excepthook

def find_board():
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

        self.latest_values = None

        self.setWindowTitle("Hall Sensor Application")
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_interface)
        self.timer.start(100)

        # Column Labels
        voltage_label = QLabel('Voltage [V]')
        current_label = QLabel('Current [mA]')
        pwm_label = QLabel('PWM Duty Cycle [%]')
        diag1_label = QLabel('OC Diag')
        diag2_label = QLabel('AMC Diag')

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

        # Value Labels
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

        # Explanation Labels
        explanation_label_1 = QLabel("<b>OC Diag (Overcurrent)</b> - Diagnostic output indicating overcurrent.<br> 0 - overcurrent detected, 1 - no overcurrent.")
        explanation_label_1.setAlignment(Qt.AlignCenter)
        explanation_label_1.setWordWrap(True)
        self.layout.addWidget(explanation_label_1, 2, 0, 1, 5)

        explanation_label_2 = QLabel("<b>AMC Diag</b> - Diagnostic output indicating the correct operation of the system.<br> 0 - problem detected, 1 - operation normal.")
        explanation_label_2.setAlignment(Qt.AlignCenter)
        explanation_label_2.setWordWrap(True)
        self.layout.addWidget(explanation_label_2, 3, 0, 1, 5)

        explanation_label_3 = QLabel("<b>PWM Duty Cycle</b><br> <b>819 +/- 2%</b> Thermal&Sensor Alert<br><b>2048 +/- 2%</b> Sensor Alert<br><b>3276 +/- 2%</b> Thermal Alert<br><b>4095</b> No PWM Duty Cycle problem")
        explanation_label_3.setAlignment(Qt.AlignCenter)
        explanation_label_3.setWordWrap(True)
        self.layout.addWidget(explanation_label_3, 4, 0, 1, 5)

        self.setFixedSize(600, 400)

        self.serial = serial.Serial(port, baudrate)
        self.receive_thread = SerialReceiveThread(self.serial)
        self.receive_thread.data_received.connect(self.update_values)
        self.receive_thread.start()

        self.read_timer = QTimer(self)
        self.read_timer.timeout.connect(self.request_data)
        self.read_timer.start(250)

    def request_data(self):
        self.receive_thread.request_data()

    def update_values(self, values):
        if len(values) >= 5:
            self.voltage_label.setText(str(values[0]))
            self.current_label.setText(str(values[1]))
            self.pwm_label.setText(str(values[4]))
            self.diag1_label.setText(str(values[3]))
            self.diag2_label.setText(str(values[2]))
            self.latest_values = values

            # Update indicator colors based on values
            if values[3] == 0:
                self.diag1_label.setStyleSheet("background-color: red;")
            else:
                self.diag1_label.setStyleSheet("background-color: green;")

            if values[2] == 0:
                self.diag2_label.setStyleSheet("background-color: red;")
            else:
                self.diag2_label.setStyleSheet("background-color: green;")

            pwm_value = values[4]
            if pwm_value >= 737 and pwm_value <= 901:
                self.pwm_label.setStyleSheet("background-color: red;")
            elif pwm_value >= 1966 and pwm_value <= 2130:
                self.pwm_label.setStyleSheet("background-color: gray;")
            elif pwm_value >= 3194 and pwm_value <= 3358:
                self.pwm_label.setStyleSheet("background-color: lightblue;")
            elif pwm_value == 4095:
                self.pwm_label.setStyleSheet("background-color: green;")

    def closeEvent(self, event):
        self.serial.close()
        event.accept()

    def update_interface(self):
        if self.latest_values:
            self.update_values(self.latest_values)
            self.latest_values = None

class SerialReceiveThread(QThread):
    data_received = pyqtSignal(list)

    def __init__(self, serial):
        super().__init__()
        self.serial = serial
        self.request_data_flag = False

    def run(self):
        while True:
            if self.request_data_flag:
                self.request_data_flag = False
                data = self.serial.readline().decode('utf-8').strip()
                values = data.split(';')
                if len(values) >= 5:
                    try:
                        values = [float(val) for val in values]
                        values[0] /= 10.0
                        values[1] /= 100.0
                        self.data_received.emit(values)
                    except ValueError:
                        print("Error: Unable to convert value to numbers.")
                        continue

    def request_data(self):
        self.request_data_flag = True

if __name__ == '__main__':
    app = QApplication(sys.argv)

    port = find_board()
    if port is not None:
        window = SerialDataDisplay(port, 115200)
        window.setGeometry(200, 200, 600, 400)
        window.show()
        sys.exit(app.exec_())
    else:
        print("No sensor found.")
