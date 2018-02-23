FROM python:2.7.14-alpine3.6
MAINTAINER Renzo Meister <rm@jamotion.ch>

COPY app /opt/prometheus-s3-exporter
RUN apk add --no-cache gcc libffi-dev musl-dev openssl-dev perl py-pip python python-dev
RUN pip install -r /opt/prometheus-s3-exporter/requirements.txt

EXPOSE 9327
VOLUME "/config"
ENTRYPOINT ["python", "/opt/prometheus-s3-exporter/exporter.py", "/config/config.yml"]
