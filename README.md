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
folders:
  - "backup"
  - "nextcloudbackup"

```

## Metrics

Metrics will be available at http://localhost:9327

```sh
# HELP s3_latest_file_timestamp Last modified timestamp(milliseconds) for latest file in folder
# TYPE s3_latest_file_timestamp gauge
s3_latest_file_timestamp{folder="backup"} 1519354873092.0
s3_latest_file_timestamp{folder="nextcloudbackup"} 1519340403144.0
# HELP s3_oldest_file_timestamp Last modified timestamp(milliseconds) for oldest file in folder
# TYPE s3_oldest_file_timestamp gauge
s3_oldest_file_timestamp{folder="backup"} 1518836477369.0
s3_oldest_file_timestamp{folder="nextcloudbackup"} 1518822003682.0
# HELP s3_latest_file_size Size in bytes for latest file in folder
# TYPE s3_latest_file_size gauge
s3_latest_file_size{folder="backup"} 322853840.0
s3_latest_file_size{folder="nextcloudbackup"} 531322.0
# HELP s3_oldest_file_size Size in bytes for latest file in folder
# TYPE s3_oldest_file_size gauge
s3_oldest_file_size{folder="backup"} 322849319.0
s3_oldest_file_size{folder="nextcloudbackup"} 528679.0
```

## Alert Example

* Alert for tim eof latest backup. This example checks if backup is created every day

```
```

* Alert for size of latest backup. This example checks latest backup file created has minimum size of 1MB

```
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