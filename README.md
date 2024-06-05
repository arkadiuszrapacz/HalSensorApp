# Low-Voltage Hall Sensor Display Application

This project is an application for displaying readings from a low-voltage Hall effect sensor. The communication with the sensor is done via UART, and the data is read from the serial port.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

## Introduction
The Low-Voltage Hall Sensor Display Application is designed to read data from a Hall effect sensor using a UART interface and display the sensor readings in a user-friendly format. This can be useful in various applications, including current sensing, magnetic field detection, and other electromagnetic applications.

## Features
- Read data from a low-voltage Hall effect sensor via UART
- Display sensor readings in real-time
- User-friendly interface for monitoring sensor data
- Easy to set up and use

## Requirements
- A low-voltage Hall effect sensor
- UART interface on your STM microcontroller 

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/arkadiuszrapacz/HalSensorApp.git
    ```

2. The executable file .exe is located in dist/ folder.

## Usage
1. Connect the Hall effect sensor to your microcontroller or computer via the UART interface.
2. Run dist/SensorApp.exe 
3. The application will start reading data from the serial port and display the sensor readings in real-time.

## Configuration
- Ensure the UART parameters (baud rate, parity, stop bits, etc.) match those of the sensor.
- This application has a feature for detecting serial port depending on the name of the connected microprocessor - Hall Sensor

