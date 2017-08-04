from protorpc.wsgi import service
from protorpc import messages
from protorpc import remote


class FieldMessage(messages.Message):
    key = messages.StringField(1)
    value = messages.StringField(2)


class SubmitApplicationRequest(messages.Message):
    fields = messages.MessageField(FieldMessage, 1, repeated=True)


class SubmitApplicationResponse(messages.Message):
    pass


class ApplicationService(remote.Service):

    @remote.method(SubmitApplicationRequest, SubmitApplicationResponse)
    def submit(self, request):
        if not request.query:
            raise remote.ApplicationError('Missing: query')
        docs, cursor = execute_search(request.query)
        resp = SearchResponse()
        resp.documents = docs
        resp.cursor = cursor
        return resp


class CorsMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('Access-Control-Allow-Origin', '*'))
            headers.append(('Access-Control-Request-Headers', 'Content-Type'))
            return start_response(status, headers, exc_info)
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            status = '200 OK'
            return custom_start_response(status, [])
        return self.app(environ, custom_start_response)


api = CorsMiddleware(service.service_mappings((
    ('/_grow/api/applications.*', ApplicationService),
)))
