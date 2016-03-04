# -*- coding: utf-8 -*-
import base64
import json
import logging
import urllib
import urllib2
from urlparse import urljoin

from .exceptions import XplentyAPIException
from .models import Cluster, Job, AccountLimits, Package

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # avoid "No handler found" warnings


API_URL = "https://api.xplenty.com/%s/api/"   # %s is a placehoher for the account id

HEADERS = {
	'Accept': 'application/vnd.xplenty+json',
}


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

    def get_packages(self):
        method_path = 'packages'
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
