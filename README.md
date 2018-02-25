# s3-exporter

Prometheus metrics exporter for S3 Storage

## Config example

```yml
access_key: "your-access-key"
secret_key: "your-secret-key"
host_base: "sos-ch-dk-2.exo.io"
host_bucket: "%(bucket)s.sos-ch-dk-2.exo.io"
use_https: True
signature_v2: True
bucket: "bucket-name"
pattern: "*.zip"
folders:
  - "backup"
  - "nextcloudbackup"

```

## Metrics

Metrics will be available at http://localhost:9327

```sh
# HELP s3_latest_file_timestamp Last modified timestamp(milliseconds) for latest file in folder
# TYPE s3_latest_file_timestamp gauge
s3_latest_file_timestamp{file="backup/backup_2018-02-25.zip",folder="backup"} 1519524066157.0
# HELP s3_oldest_file_timestamp Last modified timestamp(milliseconds) for oldest file in folder
# TYPE s3_oldest_file_timestamp gauge
s3_oldest_file_timestamp{file="backup/backup_2018-02-19.zip",folder="backup"} 1519005663854.0
# HELP s3_latest_file_size Size in bytes for latest file in folder
# TYPE s3_latest_file_size gauge
s3_latest_file_size{file="backup/backup_2018-02-25.zip",folder="backup"} 290355072.0
# HELP s3_oldest_file_size Size in bytes for latest file in folder
# TYPE s3_oldest_file_size gauge
s3_oldest_file_size{file="backup/backup_2018-02-19.zip",folder="backup"} 281699347.0
# HELP s3_file_count Numbeer of existing files in folder
# TYPE s3_file_count gauge
s3_file_count{folder="backup"} 7.0
```

## Alert Example

* Alert for time of latest backup. This example checks if backup is created every day (< 30h)

```
groups:
- name: host.rules
  rules:
  - alert: backup_is_too_old
    expr: (time()) - s3_latest_file_timestamp / 1000 > 108000
    for: 5m
    labels:
      severity: critical
    annotations:
      description: Backup too old. Reported by instance {{ $labels.instance }}.
      summary: Backup too old


```

* Alert for size of latest backup. This example checks latest backup file created has minimum size of 1MB

```
  - alert: backup_size_is_too_small
    expr: s3_latest_file_size < 1000000
    for: 5m
    labels:
      severity: critical
    annotations:
      description: Backup size too small. Reported by instance {{ $labels.instance }}.
      summary: Backup size too small
```

## Run

### Using code (local)

```sh
pip install -r app/requirements.txt
python app/exporter.py config/config.yml
```

### Using docker

```
docker run -p 9327:9327 -v ./config:/config jamotion/s3-exporter
```

### Using docker-compose

```
version: '2'
services:
  s3:
    image: jamotion/s3-exporter
    container_name: s3exporter
    volumes:
      - ./config:/config:ro
    restart: unless-stopped
    ports:
      - 9327:9327
    network_mode: host
```

Put the config file into ./config folder
