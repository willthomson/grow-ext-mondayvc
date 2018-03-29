from google.appengine.ext import vendor
vendor.add('lib')

import logging
import os
import requests
import webapp2

from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

SUBMIT_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}'


def submit_application(board_token, job_id, data, files=None):
    url = SUBMIT_URL.format(board_token=board_token, job_id=job_id)
    auth = (os.getenv('GREENHOUSE_API_KEY'), '')
    resp = requests.post(url, auth=auth, data=data, files=files)
    return resp


def clean_filename(name):
    return ''.join([i for i in name if ord(i) < 128])


class SubmitApplicationHandler(webapp2.RequestHandler):

    def post(self):
        board_token = self.request.get('board_token')
        job_id = self.request.get('job_id')
        files = []
        content = []
        for key, val in self.request.POST.iteritems():
            if hasattr(val, 'file'):
                filename = clean_filename(val.filename)
                file_tuple = (filename, val.file)
                files.append((key, file_tuple))
            else:
                content.append((key, val))
        resp = submit_application(board_token, job_id, data=content, files=files)
        try:
            resp.raise_for_status()
        except Exception as e:
            self.response.set_status(resp.status_code)
            self.response.out.write(resp.text)
            return
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(resp.status_code)
        self.response.out.write(resp.text)


def CorsMiddleware(app):

    def _set_headers(headers):
        headers.append(('Access-Control-Allow-Origin', '*'))
        headers.append(('Access-Control-Allow-Methods', '*'))
        headers.append(('Access-Control-Allow-Headers', 'origin, content-type, accept'))
        return headers

    def middleware(environ, start_response):
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            headers = []
            headers = _set_headers(headers)
            start_response('200 OK', headers)
            return []

        def headers_start_response(status, headers, *args, **kwargs):
            all_headers = [key.lower() for key, val in headers]
            if 'access-control-allow-origin' not in all_headers:
                headers = _set_headers(headers)
            return start_response(status, headers, *args, **kwargs)
        return app(environ, headers_start_response)

    return middleware


app = webapp2.WSGIApplication([
    ('/_grow/api/submit-application', SubmitApplicationHandler),
])
app = CorsMiddleware(app)
