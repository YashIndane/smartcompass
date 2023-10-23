![](https://img.shields.io/badge/Python-red?logo=Python&logoColor=white) ![](https://img.shields.io/badge/IOT-red?logo=IOT&logoColor=white) ![](https://img.shields.io/badge/Raspberry-red?logo=Raspberrypi&logoColor=white) ![](https://img.shields.io/badge/Google-Maps-red?logo=googlemaps&logoColor=white) ![](https://img.shields.io/badge/Docker-red?logo=docker&logoColor=white) ![](https://img.shields.io/badge/License-MIT-red) [![Docker Build/Publish Image](https://github.com/YashIndane/smartcompass/actions/workflows/smartcompass_arm64v8_image_builder.yml/badge.svg)](https://github.com/YashIndane/smartcompass/actions/workflows/smartcompass_arm64v8_image_builder.yml)

# Smartcompass

A device to point towards the nearest required location. A normal compass is boring (just points north), lets make something smarter that points to any required place.

# Story

Our general compass just points towards north. I decided to make a smart compass, that will point to the nearest place selected using keypad.

# Usage

Set HyperIMU app on android phone to send UDP packets to the PI. Select orientation and GPS values in packet settings.
Attach the phone to the device, such that the phone points towards the tip of the needle. The pi uses the orientation sensors inside the phone to determine its orientation. This values are streamed to the PI using HyperIMU.

Press the button on keypad for desired nearest location.

The buttons correspond to different places ->

1 - Automobile Service

2 - Hospital

3 - Police Station

4 - Petrol Pump

A - Mall

5 - Pizza

6 - Bank

B - Post Office

7 - Stadium

8 - Railway Station

C - Airport

`*` - Hotel

0 - Restaurant

`#` - School

D - Reset

For the needle to return to 0 degree mark, press the Reset button.

# Working

The pi continously scans the keypad for a button press. Once a button is pressed, using Google Maps API nearest corresponding location place coordinates and name are fetched.

Next the Pi calculates the Bearing Angle, using the coordinates fetched and the device coordinates received from HyperIMU stream. Then according to the device orientation, the final angle is calculated. This final angle is fed to stepper driver and the needle moves.

After the needle points to the required direction, the needle gets locked in that direction. To return back to 0 degree mark, press Reset.


# HyperIMU App

Install the app from - [link](https://play.google.com/store/apps/details?id=com.ianovir.hyper_imu&hl=en&gl=US)

 
# Parts required
1. [Raspberry Pi Zero 2W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
2. [28byj-48 Stepper](https://www.mouser.com/datasheet/2/758/stepd-01-data-sheet-1143075.pdf)
3. [ULN2003 Driver](https://www.ti.com/product/ULN2003A)
4. [4*4 Keypad](https://www.electroduino.com/4x4-keypad-module/)

# Circuit Diagram

## Attaching Keypad to the Pi

![sc-schematic](https://github.com/YashIndane/smartcompass/assets/53041219/6eda7d15-9781-4ab2-9409-de83fd9c3831)

## Attaching Stepper to the Pi

![schemastepper](https://github.com/YashIndane/smartcompass/assets/53041219/3c0c334f-d2d8-420a-8cf2-87e701679541)

## Docker installation

```
$ sudo curl -fsSL https://get.docker.com -o docker-install.sh
$ sh docker-install.sh
$ sudo usermod -aG docker pi
$ sudo reboot
```

## Pulling the container image from DockerHub

[Docker Image Link](https://hub.docker.com/repository/docker/yashindane/smartcompass/general)

```
$ sudo docker pull --platform linux/arm64/v8 docker.io/yashindane/smartcompass:latest
```

## Running the container

```
$ sudo docker run -it --platform linux/arm64/v8 --name smartcompass-con.$(date "+%Y.%m.%d-%H.%M.%S") --net=host --device /dev/gpiomem yashindane/smartcompass:v2 --ip="<IPV4-OF-PI>" --port=<UDP-PORT> --key="<GOOGLE-MAPS-API-KEY>" --keypad_rows="16,20,21,5" --keypad_cols="6,13,19,26" --motor_pins="17,18,27,22"
```
