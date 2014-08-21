import requests
import json
from collections import namedtuple
from base64 import b64encode

API_BASE = "https://api.inboxapp.com/n/"

class InboxAPIObject(dict):
    attrs = []

    def __init__(self):
        pass

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    @classmethod
    def from_dict(cls, dct):
        obj = cls()
        for attr in cls.attrs:
            if attr in dct:
                obj[attr] = dct[attr]

        return obj


class Message(InboxAPIObject):
    attrs = ["bcc", "body", "date", "files", "from", "id", "namespace",
             "object", "subject", "thread", "to", "unread"]


class Tag(InboxAPIObject):
    attrs = ["id", "name", "namespace", "object"]


class Thread(InboxAPIObject):
    attrs = ["drafts", "id", "messages", "namespace", "object", "participants",
             "snippet", "subject", "subject_date", "tags"]


class Draft(InboxAPIObject):
    attrs = Message.attrs + ["state"]


class File(InboxAPIObject):
    attrs = ["content_type", "filename", "id", "is_embedded", "message",
             "namespace", "object", "size"]


class Namespace(InboxAPIObject):
    attrs = ["account", "email_address", "id", "namespace", "object",
             "provider"]


class InboxClient(object):
    """A basic client for the Inbox API."""
    Message = namedtuple('Message', 'id thread')

    @classmethod
    def from_email(cls, email_address):
        namespaces = cls.namespaces()
        for ns in namespaces:
            if ns["email_address"] == email_address:
                return cls(ns["id"])
        return None

    @classmethod
    def request_code(cls, app_id, hint, redirect_uri):
        return ("https://beta.inboxapp.com/oauth/authorize?client_id="
                "%s&response_type=code&scope=email&login_hint="
                "%s&redirect_uri=%s") % (app_id,
                                         hint,
                                         redirect_uri)

    @classmethod
    def get_access_token(cls, app_id, app_secret, code):
        url = "https://www.inboxapp.com/oauth/token"
        params = {"client_id": app_id,
                  "client_secret": app_secret,
                  "grant_type": 'authorization_code',
                  "code": code}

        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        r = requests.post(url, data=params).json()
        access_token = r['access_token']
        return access_token

    @classmethod
    def from_token(cls, token, apiBase=API_BASE):
        return cls(token=token)

    @classmethod
    def from_namespace(cls, namespace, apiBase=API_BASE):
        """Only used for testing the API locally"""
        return cls(namespace=namespace, apiBase=apiBase)

    def __init__(self, namespace=None, apiBase=API_BASE, token=None):
        self.default_namespace = namespace
        self.apiBase = apiBase
        self.token = token
        self.session = requests.Session()
        if token is not None:
            # We're using the client against the authenticated API.
            # add the necessary headers.
            try:
                token_encoded = b64encode(token + ':')
            except TypeError:
                token_encoded = b64encode(bytes(token + ':', 'UTF-8')).decode('UTF-8')

            headers = {'Authorization': 'Basic ' + token_encoded,
                       'X-Inbox-API-Wrapper': 'Python'}
            self.session.headers.update(headers)

            # Add a default namespace
            if namespace is None:
                self.default_namespace = self.get_namespaces(apiBase=apiBase)[0]

    def _get_resources(self, resource, cls, **kwargs):
        namespace = self.default_namespace
        if 'namespace' in kwargs:
            namespace = kwargs.pop('namespace')

        url = "%s%s/%s?" % (self.apiBase, namespace, resource)
        for arg in kwargs:
            url += "%s=%s&" % (arg, kwargs[arg])

        response = self.session.get(url)
        if response.status_code != 200:
            response.raise_for_status()

        result = response.json()
        ret = []
        for entry in result:
            ret.append(cls.from_dict(entry))
        return ret

    def _get_resource(self, resource, cls, resource_id, **kwargs):
        """Get an individual REST resource"""
        namespace = self.default_namespace
        if 'namespace' in kwargs:
            namespace = kwargs.pop('namespace')

        url = "%s%s/%s/%s?" % (self.apiBase, namespace, resource,
                               resource_id)
        for arg in kwargs:
            url += "%s=%s&" % (arg, kwargs[arg])
        url = url[:-1]
        response = self.session.get(url)
        if response.status_code != 200:
            response.raise_for_status()

        result = response.json()
        return cls.from_dict(result)

    def _create_resource(self, resource, cls, contents):
        namespace = self.default_namespace
        if 'namespace' in kwargs:
            namespace = kwargs.pop('namespace')

        url = "%s%s/%s" % (self.apiBase, namespace, resource)
        response = self.session.post(url, data=json.dumps(contents))
        result = response.json()
        return cls.from_dict(result)

    def _create_resources(self, resource, cls, contents):
        """batch resource creation and parse the returned list"""
        namespace = self.default_namespace
        if 'namespace' in kwargs:
            namespace = kwargs.pop('namespace')

        url = "%s%s/%s" % (self.apiBase, namespace, resource)
        response = self.session.post(url, data=json.dumps(contents))
        result = response.json()
        ret = []

        for entry in result:
            ret.append(cls.from_dict(entry))
        return ret

    def _update_resource(self, resource, cls, id, data):
        namespace = self.default_namespace
        if 'namespace' in kwargs:
            namespace = kwargs.pop('namespace')

        url = "%s%s/%s" % (self.apiBase, namespace, resource)
        response = self.session.post(url, data=json.dumps(data))
        if response.status_code != 200:
            response.raise_for_status()

        result = response.json()
        return cls.from_dict(result)

    def get_namespaces(self, **kwargs):
        response = self.session.get(self.apiBase)
        result = response.json()
        ret = []

        for entry in result:
            ret.append(Namespace.from_dict(entry))

        return ret

    def get_messages(self, **kwargs):
        return self._get_resources("messages", Message, **kwargs)

    def get_threads(self, **kwargs):
        return self._get_resources("threads", Thread, **kwargs)

    def get_thread(self, id, **kwargs):
        return self._get_resource("threads", Thread, id, **kwargs)

    def get_drafts(self, **kwargs):
        return self._get_resources("drafts", Draft, **kwargs)

    def get_draft(self, id, **kwargs):
        return self._get_resource("drafts", Draft, id, **kwargs)

    def get_files(self, **kwargs):
        return self._get_resources("files", File, id, **kwargs)

    def get_file(self, id, **kwargs):
        return self._get_resource("files", File, id, **kwargs)

    def create_draft(self, body):
        return self._create_resource("drafts", Draft, body)

    def create_tag(self, tagname):
        return self._create_resource("tags", Tag, {"name": tagname})

    def create_files(self, body):
        url = "%s%s/files" % (self.apiBase, self.namespace)
        response = self.session.post(url, files=body)
        result = response.json()
        ret = []
        for entry in result:
            ret.append(File.from_dict(entry))
        return ret

    def update_tags(self, thread_id, tags):
        url = "%s%s/threads/%s" % (self.apiBase, self.namespace, thread_id)
        return self.session.put(url, data=json.dumps(tags))

    def send_message(self, message):
        url = "%s%s/send" % (self.apiBase, self.namespace)
        send_req = self.session.post(url, data=json.dumps(message))
        return send_req

    def send_draft(self, draft_id):
        return self._update_resource("send", Draft, id, {"draft_id": draft_id})
