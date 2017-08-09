from protorpc import messages
from protorpc import protojson
import grow
import os
import requests


class Error(Exception):
    pass


class GreenhousePreprocessor(grow.Preprocessor):
    KIND = 'greenhouse'
    JOBS_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/jobs'
    DEPARTMENTS_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/departments'

    class Config(messages.Message):
        board_token = messages.StringField(1)
        jobs_collection = messages.StringField(2)
        departments_collection = messages.StringField(3)

    def bind_jobs(self, board_token, collection_path):
        url = GreenhousePreprocessor.JOBS_URL.format(board_token=board_token)
        resp = requests.get(url)
	if resp.status_code != 200:
            raise Error('Error requesting -> {}'.format(url))
        content = resp.json()
        self._bind(collection_path, content['jobs'])

    def bind_departments(self, board_token, collection_path):
        url = GreenhousePreprocessor.DEPARTMENTS_URL.format(board_token=board_token)
        resp = requests.get(url)
	if resp.status_code != 200:
            raise Error('Error requesting -> {}'.format(url))
        content = resp.json()
        self._bind(collection_path, content['departments'])

    def _bind(self, collection_path, items):
        existing_paths = self.pod.list_dir(collection_path)
        existing_basenames = [path.lstrip('/') for path in existing_paths]
        new_basenames = []
        for item in items:
            path = os.path.join(collection_path, '{}.yaml'.format(item['id']))
            self.pod.write_yaml(path, item)
            self.pod.logger.info('Saving -> {}'.format(path))
            new_basenames.append(os.path.basename(path))
        basenames_to_delete = set(existing_basenames) - set(new_basenames)
        for basename in basenames_to_delete:
            # Skip deleting _blueprint, etc.
            if basename.startswith('_'):
                continue
            path = os.path.join(collection_path, basename)
            self.pod.delete_file(path)
            self.pod.logger.info('Deleting -> {}'.format(path))

    def run(self, *args, **kwargs):
        if self.config.departments_collection:
            self.bind_jobs(
                self.config.board_token,
                self.config.departments_collection)
        if self.config.jobs_collection:
            self.bind_jobs(
                self.config.board_token,
                self.config.jobs_collection)
