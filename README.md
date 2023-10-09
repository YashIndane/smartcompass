# Smartcompass
A device to point towards the nearest required location 🧭

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
