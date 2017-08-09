from google.appengine.ext import vendor
vendor.add('lib')

import logging
import os
import requests
import webapp2

SUBMIT_URL = 'https://api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}'


def submit_application(board_token, job_id, data):
    url = SUBMIT_URL.format(board_token=board_token, job_id=job_id)
    auth = (os.getenv('GREENHOUSE_API_KEY'), '')
    resp = requests.post(url, auth=auth, data=data)
    return resp


class SubmitApplicationHandler(webapp2.RequestHandler):

    def post(self):
        board_token = self.request.get('board_token')
        job_id = self.request.get('job_id')
        # TODO: Handle file uploads.
        content = []
        for key, val in self.request.POST.iteritems():
            content.append((key, val))
        resp = submit_application(board_token, job_id, content)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(resp.status_code)
        self.response.out.write(resp.text)


app = webapp2.WSGIApplication([
    ('/_grow/api/submit-application', SubmitApplicationHandler),
])
