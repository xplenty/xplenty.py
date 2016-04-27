# -*- coding: utf-8 -*-
from requests.exceptions import HTTPError
from requests import Request, Session
import datetime
import base64
import json
from models import (
        Stack,
        Job,
        Cluster,
        ClusterInstances,
        Package,
        PackageValidation,
        PackageTemplates,
        PublicKey,
        Notification,
        Subscription,
        Member,
        Stack,
        Account,
        User,
        Connection,
        ConnectionType,
        Schedule,
        Hook,
        HookTypes,
        HookEvents,
        Plan,
        PaymentMethod,
        Product,
        Region,
        SysVariable,
        Timezone,
        return_matched_kwargs
        )

import sys

from config import API_URL, SHORT_URL, HEADERS, ALLOWED_METHODS

if sys.version_info > (3, 0):
    basestring = (str, bytes)

def is_collection(obj):
    """Tests if an object is a collection."""

    col = getattr(obj, '__getitem__', False)
    val = False if (not col) else True

    if isinstance(obj, basestring):
        val = False

    return val


class XplentyCore(object):

    def __init__(self, account_id="", api_key="", session=None, timeout=30):

        super(XplentyCore, self).__init__()
        if session is None:
            session = Session()

        self._account_id = account_id
        self._api_key = api_key
        self._xplenty_url = API_URL.format(self._account_id)
        self._session = session

        # update headers
        self._session.headers.update(HEADERS)
        
        # update Authorization header
        base64string = base64.encodestring('%s' % (self._api_key)).replace('\n', '')
        self._session.headers.update({"Authorization": "Basic {}".format(base64string)})

    def __repr__(self):
        return '<Xplenty client at 0x{}>'.format(id(self))

    def _url_for(self, special_url=None, *args):
        args = map(str, args)
        if special_url:
            return '/'.join([special_url] + list(args))
        else:
            return '/'.join([self._xplenty_url] + list(args))

    def _send(self, method, resource, params=None, data=None, special_url=None, body=None):
        """Makes an HTTP request."""

        if not is_collection(resource):
            resource = [resource]
        
        url = self._url_for(special_url, *resource)
        
        def _date_handler(obj):
            if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
                return obj.isoformat()
            else:
                return obj

        if data:
            data = json.dumps(data, default=_date_handler)
        
        if body:
            req = Request(method, url, params=params, data=data)
            prepped = req.prepare()
            prepped.body = body
            r = self._session.send(prepped)
        else:
            r = self._session.request(method, url, params=params, data=data)

        if r.status_code == 422:
            http_error = HTTPError('{} Client Error: {}'.format(r.status_code, r.content.decode("utf-8")))
            http_error.response = r
            raise http_error

        if r.status_code == 403:
            http_error = HTTPError('Client Error: {} {}'.format(r.status_code, r.content))
            http_error.response = r
            raise http_error

        r.raise_for_status()

        return r

    def _get_resource(self, resource, obj, params=None, data=None, special_url=None, body=None, **kwargs):
        """Returns a mapped object from an HTTP resource."""
        r = self._send('GET', resource, params=params, special_url=special_url, data=data, body=body)
        item = self._resource_deserialize(r.content.decode("utf-8"))

        return obj.new_from_dict(item, h=self, **kwargs)

    def _get_resources(self, resource, obj, params=None, map=None, special_url=None, body=None, **kwargs):
        """Returns a list of mapped objects from an HTTP resource."""
        r = self._send('GET', resource, params=params, special_url=special_url, body=body)
        d_items = self._resource_deserialize(r.content.decode("utf-8"))

        items =  [obj.new_from_dict(item, h=self, **kwargs) for item in d_items]

        if map is None:
            map = KeyedListResource

        list_resource = map(items=items)
        list_resource._h = self
        list_resource._obj = obj
        list_resource._kwargs = kwargs

        return list_resource

    @staticmethod
    def _resource_serialize(o):
        """Returns JSON serialization of given object."""
        return json.dumps(o)

    @staticmethod
    def _resource_deserialize(s):
        """Returns dict deserialization of a given JSON string."""
        try:
            return json.loads(s)
        except ValueError:
            raise ResponseError('The API Response was not valid.')


class Xplenty(XplentyCore):
    """The main Xplenty class."""

    def __init__(self, account_id="", api_key="", session=None, timeout=30):
        super(Xplenty, self).__init__(account_id=account_id, api_key=api_key, session=session, timeout=timeout)

    def __repr__(self):
        return '<xplenty-client at 0x{}>'.format(id(self))

    def jobs(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Job()._keys()))
        return self._get_resources(('jobs'), Job, params=extra_param)
    
    def clusters(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Cluster()._keys()))
        return self._get_resources(('clusters'), Cluster, params=extra_param)

    def cluster_instances(self, cluster_id):
        return self._get_resources(('clusters', cluster_id, 'instances'), ClusterInstances)

    def packages(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Package()._keys()))
        return self._get_resources(('packages'), Package, params=extra_param)

    def packages_validation(self, package_id):
        return self._get_resources(('packages', package_id, 'validations'), PackageValidation)

    def packages_templates(self):
        return self._get_resources(('packages', 'templates'), PackageTemplates)

    def public_key(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], PublicKey()._keys()))
        return self._get_resources(('user', 'keys'), PublicKey, special_url=SHORT_URL, params=extra_param)

    def notifications(self, mark=False, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Notification()._keys()))
        if mark:
            return self._send('POST', resource=('user', 'notifications', 'mark'), special_url=SHORT_URL).ok
        else:
            return self._get_resources(('user', 'notifications'), Notification, special_url=SHORT_URL, params=extra_param)

    def subscription(self):
        return self._get_resource(('subscription'), Subscription)

    def members(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Member()._keys()))
        return self._get_resources(('members'), Member, params=extra_param)

    def stacks(self):
        return self._get_resources(('stacks'), Stack)
    
    def account(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Account()._keys()))
        return self._get_resources(('accounts'), Account, special_url=SHORT_URL, params=extra_param)

    def user(self, current_password=None):
        json_data = {}
        if current_password:
            json_data['current_password'] = current_password
        return self._get_resource(('user'), User, special_url=SHORT_URL, data=json_data)

    def connection(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Connection()._keys()))
        return self._get_resources(('connections'), Connection, params=extra_param)

    def connection_types(self):
        return self._get_resources(('connections', 'types'), ConnectionType)

    def schedule(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Schedule()._keys()))
        return self._get_resources(('schedules'), Schedule, params=extra_param)

    def hook(self, **kwargs):
        extra_param = {} 
        extra_param.update(return_matched_kwargs(locals()['kwargs'], Hook()._keys()))
        return self._get_resources(('hooks'), Hook, params=extra_param)

    def hook_types(self):
        return self._get_resources(('hooks', 'types'), HookTypes)

    def hook_events(self):
        return self._get_resources(('hook_events'), HookEvents, special_url=SHORT_URL)

    def plan(self):
        return self._get_resources(('plans'), Plan)

    def payment_method(self):
        return self._get_resource(('payment_method'), PaymentMethod)

    def product(self):
        return self._get_resources(('product_updates'), Product, special_url=SHORT_URL)

    def account_region(self):
        return self._get_resources(('regions'), Region, special_url=SHORT_URL)

    def region(self, brand_id):
        params = {}
        params['brand_id'] = brand_id
        return self._get_resources(('regions'), Region, params=params, special_url=SHORT_URL)

    def sys_variable(self, like_obj=False):
        if like_obj:
            return self._get_resource(('variables'), SysVariable, special_url=SHORT_URL)
        return self._send('GET', ('variables'), special_url=SHORT_URL).content

    def timezone(self):
        return self._get_resources(('timezones'), Timezone, special_url=SHORT_URL)


class KeyedListResource(object):
    """KeyedListResource"""

    def __init__(self, items=None):
        super(KeyedListResource, self).__init__()

        self._h = None
        self._items = items or list()
        self._obj = None
        self._kwargs = {}

    def __repr__(self):
        return repr(self._items)

    def __iter__(self):
        for item in self._items:
            yield item

    def __getitem__(self, key):

        # Support index operators.
        if isinstance(key, int):
            if abs(key) <= len(self._items):
                return self._items[key]

        v = self.get(key)

        if v is None:
            raise KeyError(key)

        return v

    def add(self, *args, **kwargs):

        try:
            return self[0].new(*args, **kwargs)
        except IndexError:
            o = self._obj()
            o._h = self._h
            o.__dict__.update(self._kwargs)

            return o.new(*args, **kwargs)

    def remove(self, key):
        if hasattr(self[0], 'delete'):
            return self[key].delete()

    def get(self, key):
        for item in self:
            if key in item._ids:
                return item

    def __delitem__(self, key):
        self[key].delete()


class ResponseError(ValueError):
    """The API Response was unexpected."""
