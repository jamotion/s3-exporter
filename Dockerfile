FROM python:2.7.14-alpine3.6
MAINTAINER Renzo Meister <rm@jamotion.ch>

RUN apk add --no-cache gcc libffi-dev musl-dev openssl-dev perl py-pip python python-dev

COPY app/requirements.txt /opt/prometheus-s3-exporter/requirements.txt
RUN pip install -r /opt/prometheus-s3-exporter/requirements.txt

COPY app/exporter.py /opt/prometheus-s3-exporter/exporter.py

EXPOSE 9327
VOLUME "/config"
ENTRYPOINT ["python", "/opt/prometheus-s3-exporter/exporter.py", "/config/config.yml"]
