#Dockerfile for smartcompass-project

FROM docker.io/yashindane/smartcompass-base-arm64:v1

MAINTAINER Yash Indane <yashindane46@gmail.com>

LABEL platform="linux/arm64/v8" version="arm64v8"

COPY . ./

ENTRYPOINT ["python", "./compass.py"]
