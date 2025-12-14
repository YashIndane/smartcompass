#!/usr/bin/python3

# Module to read IMU sensor using HyperIMU App

import socket
import os

from typing import Tuple, List

class IMU:
    _BUFFER_SIZE = 1024

    def __init__(self, device_ip: str, udp_port: int) -> None:
        self.device_ip = device_ip
        self.udp_port = udp_port

        # socket initiate
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )
        self.sock.bind((device_ip, udp_port))

    def get_imu_reading(self) -> Tuple[float, str, str]:
        """Reads the IMU sensor

        :return: X-axis rotation in degrees, Latitude & Longitude (type Tuple[float, str, str])
        """
          
        data, address = self.sock.recvfrom(IMU._BUFFER_SIZE)
        data: List[str] = str(data)[2:].split(',')
        # x-axis rotation vector
        x_rot: float = round(float(data[0]), 1)

        # latitude & longitude GPS values
        lat, long = data[3], data[4]

        return (x_rot, lat, long)
    
    def close_socket(self) -> None: self.sock.close()
