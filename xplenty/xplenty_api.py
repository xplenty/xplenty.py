# -*- coding: utf-8 -*-
import base64
import json
import logging
import urllib
import urllib2
from urlparse import urljoin

from dateutil.parser import parse as parse_datetime

from .exceptions import XplentyAPIException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # avoid "No handler found" warnings


API_URL = "https://api.xplenty.com/%s/api/"   # %s is a placehoher for the account id

HEADERS = {
	'Accept': 'application/vnd.xplenty+json',
}


# from kennethreitz/python-github3
def to_python(obj,
    in_dict,
    str_keys=None,
    date_keys=None,
    int_keys=None,
    float_keys=None,
    object_map=None,
    bool_keys=None,
    dict_keys=None,
    **kwargs):
    """Extends a given object for API Consumption.

    :param obj: Object to extend.
    :param in_dict: Dict to extract data from.
    :param string_keys: List of in_dict keys that will be extracted as strings.
    :param date_keys: List of in_dict keys that will be extrad as datetimes.
    :param object_map: Dict of {key, obj} map, for nested object results.
    """

    d = dict()

    if str_keys:
        for in_key in str_keys:
            d[in_key] = in_dict.get(in_key)

    if date_keys:
        for in_key in date_keys:
            in_date = in_dict.get(in_key)
            try:
                out_date = parse_datetime(in_date)
            except Exception, e:
                #raise e
                out_date = None

            d[in_key] = out_date

    if int_keys:
        for in_key in int_keys:
            if (in_dict is not None) and (in_dict.get(in_key) is not None):
                d[in_key] = int(in_dict.get(in_key))

    if float_keys:
        for in_key in float_keys:
            if (in_dict is not None) and (in_dict.get(in_key) is not None):
                d[in_key] = float(in_dict.get(in_key))

    if bool_keys:
        for in_key in bool_keys:
            if in_dict.get(in_key) is not None:
                d[in_key] = bool(in_dict.get(in_key))

    if dict_keys:
        for in_key in dict_keys:
            if in_dict.get(in_key) is not None:
                d[in_key] = dict(in_dict.get(in_key))

    if object_map:
        for (k, v) in object_map.items():
            if in_dict.get(k):
                d[k] = v.new_from_dict(in_dict.get(k))

    obj.__dict__.update(d)
    obj.__dict__.update(kwargs)

    # Save the dictionary, for write comparisons.
    # obj._cache = d
    # obj.__cache = in_dict

    return obj


class BaseModel(object):

    _strs = []
    _ints = []
    _dates = []
    _bools = []
    _dicts = []
    _floats = []
    _map = {}
    _pks = []

    def __init__(self):
        self._bootstrap()
        self._h = None
        super(BaseModel, self).__init__()

    def __repr__(self):
        return "<resource '{0}'>".format(self._id)

    def _bootstrap(self):
        """Bootstraps the model object based on configured values."""

        for attr in self._keys():
            setattr(self, attr, None)

    def _keys(self):
        return self._strs + self._ints + self._dates + self._bools + self._map.keys()

    @property
    def _id(self):
        try:
            return getattr(self, self._pks[0])
        except IndexError:
            return None

    @property
    def _ids(self):
        """The list of primary keys to validate against."""
        for pk in self._pks:
            yield getattr(self, pk)

        for pk in self._pks:

            try:
                yield str(getattr(self, pk))
            except ValueError:
                pass

    def dict(self):
        d = dict()
        for k in self.keys():
            d[k] = self.__dict__.get(k)

        return d

    @classmethod
    def new_from_dict(cls, d, h=None, **kwargs):

        d = to_python(
            obj=cls(),
            in_dict=d,
            str_keys=cls._strs,
            int_keys=cls._ints,
            float_keys=cls._floats,
            date_keys=cls._dates,
            bool_keys=cls._bools,
            dict_keys=cls._dicts,
            object_map=cls._map,
            _h=h
        )

        d.__dict__.update(kwargs)

        return d


class Cluster(BaseModel):
    """Xplenty Cluster."""

    _strs = ['name','description','status','type', 'url']
    _ints = ['id','owner_id','nodes', 'running_jobs_count', 'time_to_idle']
    _dates = ['created_at','updated_at', 'available_since', 'terminated_at']
    _bools = ['terminate_on_idle']
    _pks = ['id']

    def __repr__(self):
        return "<Cluster '{0}'>".format(self.name)


class Job(BaseModel):
    """Xplenty Job."""

    _strs = ['errors','status','url']
    _ints = ['id','cluster_id','outputs_count','owner_id','package_id','runtime_in_seconds']
    _floats = ['progress']
    _dates = ['created_at','started_at','updated_at','failed_at','completed_at']
    _dicts = ['variables','dynamic_variables']
    _pks = ['id']

    def __repr__(self):
        return "<Job '{0}'>".format(self.name)


class AccountLimits(BaseModel):
    """Xplenty Account limits."""

    _ints = ['limit','remaining']

    def __repr__(self):
        return "<AccountLimits '{0}'>".format(self.name)


class Package(BaseModel):
    """Xplenty Package."""

    _strs = ['name','description', 'url']
    _ints = ['id','owner_id']
    _floats = []
    _dates = ['created_at','updated_at']
    _dicts = ['variables']
    _pks = ['id']

    def __repr__(self):
        return "<Package '{0}'>".format(self.name)


class Schedule(BaseModel):
    """Xplenty Schedule."""

    _strs = ['name','description', 'url', 'interval_unit', 'last_run_status', 'status']
    _ints = ['id','owner_id', 'interval_amount', 'execution_count']
    _floats = []
    _dates = ['created_at','updated_at', 'start_at', 'next_run_at', 'last_run_at']
    _dicts = ['variables', 'task']
    _pks = ['id']

    def __repr__(self):
        return "<Schedule '{0}'>".format(self.name)


class RequestWithMethod(urllib2.Request):
    """Workaround for using DELETE with urllib2"""
    def __init__(self, url, method, data=None, headers={},\
        origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers,\
                 origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


class XplentyClient(object):

    version = "1.0"
    def __init__(self, account_id="", api_key=""):
        self.account_id = account_id
        self.api_key = api_key

    def __repr__(self):
        return '<Xplenty client at 0x%x>' % (id(self))

    def get(self,url):
        logger.debug("GET %s", url)
        request = urllib2.Request(url,headers=HEADERS)
        base64string = base64.encodestring('%s' % (self.api_key)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        try:
            resp = urllib2.urlopen(request)
        except urllib2.HTTPError, error:
            raise XplentyAPIException(error)

        return json.loads(resp.read())

    def post(self, url, data_dict={}):
        encoded_data = urllib.urlencode(data_dict)
        logger.debug("POST %s, data %s", url, encoded_data)

        request = urllib2.Request(url, data=encoded_data, headers=HEADERS)
        base64string = base64.encodestring('%s' % (self.api_key)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        try:
            resp = urllib2.urlopen(request)
        except urllib2.HTTPError, error:
            raise XplentyAPIException(error)

        return json.loads(resp.read())

    def delete(self, url):
        logger.debug("DELETE %s", url)
        request = RequestWithMethod(url, 'DELETE', headers=HEADERS)
        base64string = base64.encodestring('%s' % (self.api_key)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        try:
            resp = urllib2.urlopen(request)
        except urllib2.HTTPError, error:
            raise XplentyAPIException(error)

        return json.loads(resp.read())

    def _join_url(self, method):
        _url = API_URL % ( self.account_id )
        url = urljoin(_url , method )
        return url

    def get_clusters(self):
        method_path = 'clusters'
        url = self._join_url( method_path )
        resp = self.get(url)
        clusters =  [Cluster.new_from_dict(item, h=self) for item in resp]

        return clusters

    def get_cluster(self,id):
        method_path = 'clusters/%s'%(str(id))
        url = self._join_url( method_path )
        resp = self.get(url)
        cluster =  Cluster.new_from_dict(resp, h=self)

        return cluster

    def terminate_cluster(self,id):
        method_path = 'clusters/%s'%(str(id))
        url = self._join_url( method_path )
        resp = self.delete(url)
        cluster =  Cluster.new_from_dict(resp, h=self)

        return cluster

    def create_cluster(self, cluster_type, nodes, cluster_name, cluster_description, terminate_on_idle=False, time_to_idle=3600):
        cluster_info ={}
        cluster_info["cluster[type]"]= cluster_type
        cluster_info["cluster[nodes]"]= nodes
        cluster_info["cluster[name]"]= cluster_name if cluster_name else ""
        cluster_info["cluster[description]"]= cluster_description if cluster_description else ""
        cluster_info["cluster[terminate_on_idle]"]= 1 if terminate_on_idle else 0
        cluster_info["cluster[time_to_idle]"]= time_to_idle
        method_path = 'clusters'
        url = self._join_url( method_path )
        resp = self.post(url,cluster_info)
        cluster =  Cluster.new_from_dict(resp, h=self)

        return cluster

    def get_jobs(self):
        method_path = 'jobs'
        url = self._join_url(method_path )
        resp = self.get(url)

        jobs =  [Job.new_from_dict(item, h=self) for item in resp]

        return jobs

    def get_job(self,id):
        method_path = 'jobs/%s'%(str(id))
        url = self._join_url( method_path )
        resp =self.get(url)
        job =  Job.new_from_dict(resp, h=self)

        return job

    def stop_job(self,id):
        method_path = 'jobs/%s'%(str(id))
        url = self._join_url( method_path )
        resp = self.delete(url)

        return resp

    def add_job(self, cluster_id, package_id, vars={}, dynamic_vars={}):
        job_info = {}
        job_info["job[cluster_id]"]= cluster_id
        # We use job_id instead of package_id since that's how it is accepted on Xplenty's side
        job_info["job[job_id]"]= package_id

        for k, v in vars.iteritems():
            new_key = "job[variables][%s]"%(k)
            job_info[new_key]= v

        for k, v in dynamic_vars.iteritems():
            new_key = "job[dynamic_variables][%s]"%(k)
            job_info[new_key]= v

        method_path = 'jobs'
        url = self._join_url( method_path )
        resp = self.post(url,job_info)
        job =  Job.new_from_dict(resp, h=self)

        return job

    def get_account_limits(self):

        method_path = 'rate_limit_status'
        url = self._join_url( method_path )
        resp = self.get(url)

        limit =  AccountLimits.new_from_dict(resp['limits'], h=self)

        return limit

    def get_packages(self, offset=0, limit=20):
        method_path = 'packages?offset=%d&limit=%d' % (offset, limit)
        url = self._join_url(method_path)
        resp = self.get(url)
        packages = [Package.new_from_dict(item, h=self) for item in resp]

        return packages

    def get_package(self, id):
        method_path = 'packages/%s' % id
        url = self._join_url(method_path)
        resp = self.get(url)
        package = Package.new_from_dict(resp, h=self)

        return package

    def get_schedules(self):
        method_path = 'schedules'
        url = self._join_url(method_path)
        resp = self.get(url)
        return [Schedule.new_from_dict(item, h=self) for item in resp]

    def get_schedule(self, id):
        method_path = 'schedules/%s' % id
        url = self._join_url(method_path)
        resp = self.get(url)
        return Schedule.new_from_dict(resp, h=self)

    @property
    def clusters(self):
        return self.get_clusters()

    @property
    def jobs(self):
        return self.get_jobs()

    @property
    def account_limits(self):
        return self.get_account_limits()

    @property
    def packages(self):
        return self.get_packages()

    @property
    def schedules(self):
        return self.get_schedules()
