# !/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Jamotion GmbH, Your Odoo implementation partner
#    Copyright (C) 2004-2010 Jamotion GmbH.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Created by renzo on 23.02.18.
#
import fnmatch
import time
from dateutil import parser as dtparser
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import argparse
import yaml
import logging
from S3.Config import Config as S3Config
from S3.S3 import S3

DEFAULT_PORT = 9327
DEFAULT_LOG_LEVEL = 'info'


def string_to_timestamp(string_value):
    datetime_value = dtparser.parse(string_value)
    return time.mktime(datetime_value.timetuple()) * 1000 + datetime_value.microsecond / 1000


class S3Collector(object):
    def __init__(self, config):
        self._config = config
        self._s3config = S3Config()
        access_key = config.get('access_key', False)
        if access_key:
            self._s3config.update_option('access_key', access_key)
        secret_key = config.get('secret_key', False)
        if secret_key:
            self._s3config.update_option('secret_key', secret_key)
        host_base = config.get('host_base', False)
        if host_base:
            self._s3config.update_option('host_base', host_base)
        host_bucket = config.get('host_bucket', False)
        if host_bucket:
            self._s3config.update_option('host_bucket', host_bucket)
        use_https = config.get('use_https', True)
        self._s3config.update_option('use_https', use_https)
        signature = config.get('signature_v2', True)
        self._s3config.update_option('signature_v2', signature)

        if len(self._s3config.access_key)==0:
            self._s3config.role_config()

        self._s3 = S3(self._s3config)

    def collect(self):
        pattern = self._config.get('pattern', False)

        latest_file_timestamp_gauge = GaugeMetricFamily(
                's3_latest_file_timestamp',
                'Last modified timestamp(milliseconds) for latest file in '
                'folder',
                labels=['folder', 'file'],
        )
        oldest_file_timestamp_gauge = GaugeMetricFamily(
                's3_oldest_file_timestamp',
                'Last modified timestamp(milliseconds) for oldest file in '
                'folder',
                labels=['folder', 'file'],
        )
        latest_file_size_gauge = GaugeMetricFamily(
                's3_latest_file_size',
                'Size in bytes for latest file in folder',
                labels=['folder', 'file'],
        )
        oldest_file_size_gauge = GaugeMetricFamily(
                's3_oldest_file_size',
                'Size in bytes for latest file in folder',
                labels=['folder', 'file'],
        )
        file_count_gauge = GaugeMetricFamily(
                's3_file_count',
                'Number of existing files in folder',
                labels=['folder'],
        )
        for folder in config.get('folders'):
            prefix = folder[-1] == '/' and folder or '{0}/'.format(folder)
            if prefix == '/':
                result = self._s3.bucket_list(config.get('bucket'), None)
            else:
                result = self._s3.bucket_list(config.get('bucket'), prefix)
            files = result['list']
            if pattern:
                files = [f for f in files if fnmatch.fnmatch(f['Key'], pattern)]
            files = sorted(files, key=lambda s: s['LastModified'])
            if not files:
                continue
            last_file = files[-1]
            last_file_name = last_file['Key']
            oldest_file = files[0]
            oldest_file_name = oldest_file['Key']
            latest_modified = string_to_timestamp(last_file['LastModified'])
            oldest_modified = string_to_timestamp(oldest_file['LastModified'])

            file_count_gauge.add_metric([folder], len(files))

            latest_file_timestamp_gauge.add_metric([
                folder,
                last_file_name,
            ], latest_modified)
            oldest_file_timestamp_gauge.add_metric([
                folder,
                oldest_file_name,
            ], oldest_modified)
            latest_file_size_gauge.add_metric([
                folder,
                last_file_name,
            ], int(last_file['Size']))
            oldest_file_size_gauge.add_metric([
                folder,
                oldest_file_name,
            ], int(oldest_file['Size']))

        yield latest_file_timestamp_gauge
        yield oldest_file_timestamp_gauge
        yield latest_file_size_gauge
        yield oldest_file_size_gauge
        yield file_count_gauge


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Expose metrics for S3 storage')
    parser.add_argument('config_file_path', help='Path of the config file')
    args = parser.parse_args()
    with open(args.config_file_path) as config_file:
        config = yaml.load(config_file)
        log_level = config.get('log_level', DEFAULT_LOG_LEVEL)
        logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.getLevelName(log_level.upper()))
        exporter_port = config.get('exporter_port', DEFAULT_PORT)
        logging.debug("Config %s", config)
        logging.info('Starting server on port %s', exporter_port)
        start_http_server(exporter_port)
        REGISTRY.register(S3Collector(config))
    while True: time.sleep(1)
