from protorpc import messages
from protorpc import protojson
import bleach
import grow
import os
import requests
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


class Error(Exception):
    pass


class AttributeMessage(messages.Message):
    tag = messages.StringField(1)
    attributes = messages.StringField(2, repeated=True)


class GreenhousePreprocessor(grow.Preprocessor):
    KIND = 'greenhouse'
    DEGREES_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/education/degrees'
    DEPARTMENTS_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/departments'
    DISCIPLINES_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/education/disciplines'
    JOBS_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/jobs?content=true'
    JOB_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}?questions=true'
    SCHOOLS_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/education/schools'

    class Config(messages.Message):
        board_token = messages.StringField(1)
        jobs_collection = messages.StringField(2)
        departments_collection = messages.StringField(3)
        allowed_html_tags = messages.StringField(4, repeated=True)
        allowed_html_attributes = messages.MessageField(AttributeMessage, 5, repeated=True)
        education_path = messages.StringField(6)
        departments_blacklist = messages.StringField(7, repeated=True)

    def bind_jobs(self, board_token, collection_path):
        url = GreenhousePreprocessor.JOBS_URL.format(board_token=board_token)
        resp = requests.get(url)
	if resp.status_code != 200:
            raise Error('Error requesting -> {}'.format(url))
        content = resp.json()
        self._bind(collection_path, content['jobs'])

    def _download_schools(self, board_token):
        schools = {'items': []}
        total = 0
        has_run = False
        items_so_far = 0
        page = 0
        while has_run is False or total > items_so_far:
            self.pod.logger.info('Downloading schools (page {})'.format(page))
            url = GreenhousePreprocessor.SCHOOLS_URL.format(board_token=board_token) + '?page={}'.format(page)
            resp = requests.get(url)
            if resp.status_code != 200:
                raise Error('Error requesting -> {}'.format(url))
            resp = resp.json()
            if has_run is False:
                total = resp.get('meta', {}).get('total_count', 0)
                has_run = True
            schools['items'] += resp['items']
            items_so_far += len(resp['items'])
            page += 1
        return schools

    def bind_education(self, board_token, education_path):
        schools = self._download_schools(board_token)
        url = GreenhousePreprocessor.DEGREES_URL.format(board_token=board_token)
        resp = requests.get(url)
	if resp.status_code != 200:
            raise Error('Error requesting -> {}'.format(url))
        degrees = resp.json()
        url = GreenhousePreprocessor.DISCIPLINES_URL.format(board_token=board_token)
        resp = requests.get(url)
	if resp.status_code != 200:
            raise Error('Error requesting -> {}'.format(url))
        disciplines = resp.json()
        item = {
            'degrees': degrees,
            'disciplines': disciplines,
            'schools': schools,
        }
        path = os.path.join(education_path)
        self.pod.write_yaml(path, item)
        self.pod.logger.info('Saving -> {}'.format(path))

    def _parse_entry(self, item):
        if item.get('title'):
            item['$title'] = item.pop('title')
        if item.get('content'):
            item['content'] = self._parse_content(item.get('content'))
        if item.get('compliance'):
            for i, row in enumerate(item['compliance']):
                item['compliance'][i]['description'] = \
                        self._parse_content(row['description'])
        return item

    def _parse_content(self, content):
        parser = HTMLParser()
        content = parser.unescape(content)
        tags = self.config.allowed_html_tags
        if tags:
            attributes = {}
            if self.config.allowed_html_attributes:
                for attribute in self.config.allowed_html_attributes:
                    attributes[attribute.tag] = attribute.attributes
            content = bleach.clean(
                    content, tags=tags, attributes=attributes, strip=True)
        return content

    def _get_single_job(self, item):
        board_token = self.config.board_token
        url = GreenhousePreprocessor.JOB_URL.format(
                board_token=board_token, job_id=item['id'])
        resp = requests.get(url)
	if resp.status_code != 200:
            raise Error('Error requesting -> {}'.format(url))
        content = resp.json()
        return content

    def _bind(self, collection_path, items):
        existing_paths = self.pod.list_dir(collection_path)
        existing_basenames = [path.lstrip('/') for path in existing_paths]
        departments_blacklist = self.config.departments_blacklist or []
        departments_blacklist = [name.lower() for name in departments_blacklist]
        new_basenames = []
        for item in items:
            # Skip departments added to the blacklist.
            department_names = [department.get('name', '').lower()
                    for department in item.get('departments', [])]
            skip = False
            for name in department_names:
                if name in departments_blacklist:
                   self.pod.logger.info('Skipping department -> {}'.format(name))
                   skip = True
            if skip:
                continue
            item = self._get_single_job(item)
            item = self._parse_entry(item)
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
        if self.config.jobs_collection:
            self.bind_jobs(
                self.config.board_token,
                self.config.jobs_collection)
        if self.config.education_path:
            self.bind_education(
                self.config.board_token,
                self.config.education_path)
