ARG base

FROM ubuntu:20.04 as dev

LABEL maintainer="nafisatd@uncannyvision.com"

RUN apt -y update \
  && apt -y install python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install requests prometheus_client kubernetes

RUN mkdir -p /app
RUN mkdir -p /app/config

COPY run.sh /app/
COPY src/prometheus_metrics2.py /app/

WORKDIR /app/

ENTRYPOINT ["./run.sh"]
