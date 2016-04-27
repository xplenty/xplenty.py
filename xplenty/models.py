# -*- coding: utf-8 -*-
import json
import datetime
from dateutil.parser import parse as parse_datetime
from config import API_URL, SHORT_URL, HEADERS, ALLOWED_METHODS



def return_matched_kwargs(kwargs, keys, place=None):
    data = {}
    for (key, val) in kwargs.iteritems():
        if key not in keys:
            if place:
                raise TypeError("Got an unexpected keyword argument '{}' to method {}".format(key, place))
            else:
                raise TypeError("Got an unexpected keyword argument '{}'".format(key))
        data[key] = val

    return data

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
    _lists = []

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
        return self._strs + self._ints + self._dates + self._bools + self._map.keys() + self._dicts + self._floats + self._pks + self._lists

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
            lists_keys = cls._lists,
            _h=h
        )

        d.__dict__.update(kwargs)

        return d


class ClusterInstances(BaseModel):
    """Xplenty ClusterInstances."""

    _strs = ['private_dns', 'public_dns', 'status', 'zone', 'instance_type']
    _ints = ['instance_id']
    _bools = ['master', 'spot', 'vpc']
    _pks = ['instance_id']

    def __repr__(self):
        return "<Cluster instances '{0}'>".format(self.instance_id)


class Cluster(BaseModel):
    """Xplenty Cluster."""

    _strs = ['name', 'description', 'status', 'type', 'url', 'region', 'master_instance_type',
            'slave_instance_type', 'html_url', 'creator', 'stack', 'bootstrap_actions']
    _ints = ['id', 'owner_id', 'plan_id', 'nodes', 'running_jobs_count', 'time_to_idle']
    _dates = ['created_at', 'updated_at', 'available_since', 'terminated_at', 'idle_since']
    _bools = ['terminate_on_idle', 'terminated_on_idle', 'allow_fallback']
    _pks = ['id']
    _floats = ['master_spot_price', 'slave_spot_price', 'master_spot_percentage', 'slave_spot_percentage']
    
    def __repr__(self):
        return "<Cluster '{0}'>".format(self.name)

    def new(self, nodes, **kwargs):
        return self._create_cluster(nodes, **kwargs)
    
    def _create_cluster(self, nodes, **kwargs):
        method_path = 'clusters'
        json_data = {} 
        json_data['nodes'] = int(nodes)
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))

        res = [i for i in method_path.split('/')]
        r = self._h._send(method="POST", resource=res, data=json_data)
       
        return r

    def update_cluster(self, **kwargs):
        method_path = 'clusters/{}'.format(self.id)
        json_data = {} 
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))
        
        res = [i for i in method_path.split('/')]
        r = self._h._send(method="PUT", resource=res, data=json_data)
        
        cluster_id = json.loads(r.content).get('id')

        return self._h.clusters().get(cluster_id)

    def delete(self):
        return self._terminate_cluster

    @property
    def _terminate_cluster(self):
        method_path = 'clusters/{}'.format(self.id)
        res = [i for i in method_path.split('/')]
        r = self._h._send(method="DELETE", resource=res)
        return r.ok

    def watch_cluster(self, action=False):
        method_path = 'clusters/{}/watchers'.format(self.id)
        res = [i for i in method_path.split('/')]

        if action in ALLOWED_METHODS:
            r = self._h._send(method=action, resource=res)
            if action != 'DELETE':
                r = json.loads(r.content)
                return r 
            else:
                return r.ok
        else:
            return 'Fail method'


class Notification(BaseModel):
    """Xplenty Cluster."""

    _strs = ['title', 'message', 'all', 'sort', 'direction']
    _ints = ['id']
    _dates = ['last_read_at', 'since']
    _bools = []
    _pks = ['id']
    _floats = []

    def __repr__(self):
        return "<Notification '{0}'>".format(self.title)


class Job(BaseModel):
    """Xplenty Job."""

    _strs = ['errors', 'status', 'url', 'sort', 'direction', 'creator', 'log_url', 'html_url']
    _ints = ['id', 'cluster_id', 'outputs_count', 'owner_id', 'package_id', 'runtime_in_seconds']
    _floats = ['progress']
    _dates = ['created_at', 'started_at', 'updated_at', 'failed_at', 'completed_at', 'since']
    _dicts = ['variables', 'dynamic_variables', 'outputs', 'cluster', 'package']
    _pks = ['id']

    def __repr__(self):
        return "<Job '{0}'>".format(self.id)

    def preview_job_output(self, output_id):
        method_path = 'jobs/{}/outputs/{}/preview'.format(self.id, output_id)
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="GET", resource=res)
        result = json.loads(r.content)

        return result

    def get_job_variable(self):
        method_path = 'jobs/{}/variables'.format(self.id)
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="GET", resource=res)
        result = json.loads(r.content)

        return result
    
    def get_job_log(self):
        method_path = 'jobs/{}/log'.format(self.id)
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="GET", resource=res)
        result = json.loads(r.content)
        
        return result

    def new(self, cluster_id, package_id, **kwargs):
        return self._run_job(cluster_id, package_id, **kwargs)

    def _run_job(self, cluster_id, package_id, **kwargs):
        method_path = 'jobs'
        json_data = {}
        json_data['cluster_id'] = cluster_id
        json_data['package_id'] = package_id
        json_data.update(**kwargs)

        r = self._h._send(method="POST", resource=method_path, data=json_data)
        job_id = json.loads(r.content).get('id')

        return self._h.jobs().get(job_id)

    def delete(self):
        return self._terminate_job

    @property
    def _terminate_job(self):
        method_path = 'jobs/{}'.format(self.id)
        res = [i for i in method_path.split('/')]
        r = self._h._send(method="DELETE", resource=res)
        return r.ok

    def watch_job(self, action=False):
        method_path = 'jobs/{}/watchers'.format(self.id)
        res = [i for i in method_path.split('/')]

        if action in ALLOWED_METHODS:
            r = self._h._send(method=action, resource=res)
            if action != 'DELETE':
                r = json.loads(r.content)
                return r 
            else:
                return r.ok
        else:
            return 'Fail method'


class Subscription(BaseModel):
    """Xplenty Subscription."""

    _strs = ['url', 'plan_id' ]
    _ints = ['trial_period_days']
    _floats = []
    _dates = ['trial_start', 'trial_end']
    _bools = ['trialling']
    _pks = ['plan_id']

    def __repr__(self):
        return "<Subscription '{0}'>".format(self.plan_id)


class Member(BaseModel):
    """Xplenty Member."""

    _strs = ['name', 'email', 'gravatar_email', 'avatar_url', 'role', 'url', 'html_url', 'location']
    _ints = ['id']
    _dates = ['created_at', 'updated_at', 'confirmed_at']
    _bools = ['confirmed', 'owner']
    _pks = ['id']

    def __repr__(self):
        return "<Member '{0}'>".format(self.name)

    def new(self, email, name=None, role='member'):
        return self._add_member(email, name, role)

    def _add_member(self, email, name=None, role='member'):
        method_path = 'members'
        member_info = {}
        if role:
            member_info["role"] = role
        if name:
            member_info["name"] = name
        member_info["email"] = email

        r = self._h._send(method="POST", resource=method_path, data=member_info)
        member_id = json.loads(r.content).get('id')

        return self._h.members().get(member_id)

    def delete(self):
        return self._delete_member
    
    @property
    def _delete_member(self):
        method_path = 'members/{}'.format(self.id)
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="DELETE", resource=res)
        
        return r.ok

    def set_member_role(self, role):
        method_path = 'members/{}'.format(self.id)
        json_data = {}
        json_data["role"] = role
        res = [i for i in method_path.split('/')]
        
        r = self._h._send(method="PUT", resource=res, data=json_data)
        member_id = json.loads(r.content).get('id')

        return self._h.members().get(member_id)


class Account(BaseModel):
    """Xplenty Account."""

    _strs = ['account_id', 'uname', 'name', 'region', 'location', 'billing_email', 'gavatar_email', 'avatar_url', 'role', 'url', 'public_key']
    _ints = ['id', 'schedules_count', 'connections_count', 'owner_id', 'members_count', 'packages_count', 'jobs_count', 'running_jobs_count', 'hooks_count']
    _dates = ['created_at', 'updated_at', ]
    _pks = ['id']

    def __repr__(self):
        return "<Account '{0}'>".format(self.name)

    def new(self, name, region, account_id=None):
        return self._add_account(name, region, account_id)

    def _add_account(self, name, region, account_id=None):
        
        method_path = 'accounts'
        special_url = SHORT_URL

        json_data = {}
        json_data['name'] = name
        json_data['region'] = region
        if account_id:
            json_data['account_id'] = account_id

        res = [i for i in method_path.split('/')]

        r = self._h._send(method="POST", resource=res, data=json_data, special_url=special_url)
        account_id = json.loads(r.content).get('id')

        return self._h.account().get(account_id)

    def update_account(self, **kwargs):
        
        method_path = 'accounts/{}'.format(self.account_id)
        special_url = SHORT_URL

        json_data = {}
        json_data['account_id'] = self.account_id
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))

        res = [i for i in method_path.split('/')]

        r = self._h._send(method="PUT", resource=res, data=json_data, special_url=special_url)
        account_id = json.loads(r.content).get('id')

        return self._h.account().get(account_id)

    def delete(self):
        return self._delete_account

    @property
    def _delete_account(self):
        method_path = 'accounts/{}'.format(self.account_id)
        special_url = SHORT_URL

        res = [i for i in method_path.split('/')]
        r = self._h._send(method="DELETE", resource=res, special_url=special_url)
        
        return r.ok


class PackageValidation(BaseModel):
    """ Xplenty Package Validation. """
    # works fine all methods

    _strs = ['status', 'status_message', 'url']
    _ints = ['id', 'package_id', 'owner_id', 'account_id']
    _dates = ['runtime', 'created_at', 'updated_at']
    _pks = ['id']
    _lists = ['errors']

    def __init__(self):
        super(PackageValidation, self).__init__()

    def __repr__(self):
        return "<Package validation '{0}'>".format(self.id)

    def new(self, package_id):
        return self._run_package_validation(package_id)
    
    def _run_package_validation(self, package_id):
        method_path = 'packages/{}/validations'.format(package_id)
        res = [i for i in method_path.split('/')]
        
        r = self._h._send(method="POST", resource=res)
        pv_id = json.loads(r.content).get('id')

        return self._h.packages_validation(package_id).get(pv_id)


class PackageTemplates(BaseModel):
    """ Xplenty Package Templates. """
    # works fine all methods

    _strs = ['name', 'description']
    _ints = ['id', 'position']
    _pks = ['id']
    _dicts = ['author']

    def __repr__(self):
        return "<Package templates '{0}-{1}'>".format(self.id, self.name)


class Package(BaseModel):
    """Xplenty Package."""

    _strs = ['name','description', 'url', 'html_url', 'status', 'sort', 'direction', 'flow_type', 'status', 'status_message']
    _ints = ['id','owner_id', 'package_id', 'account_id']
    _floats = []
    _dates = ['created_at','updated_at', 'since', 'runtime']
    _dicts = ['variables']
    _pks = ['id']
    _lists = ['errors']

    def __repr__(self):
        return "<Package '{0}'>".format(self.name)

    def new(self, **kwargs):
        return self._create_package(**kwargs)

    def _create_package(self, **kwargs):
        method_path = 'packages'
        json_data = {}
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))
        
        r = self._h._send(method="POST", resource=method_path, data=json_data)
        package_id = json.loads(r.content).get('id')

        return self._h.packages().get(package_id)

    def update_package(self, **kwargs):
        method_path = 'packages/{}'.format(self.id)
        json_data = {}
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="PUT", resource=res, data=json_data)
        package_id = json.loads(r.content).get('id')

        return self._h.packages().get(package_id)

    def delete(self):
        return self._delete_package

    @property
    def _delete_package(self):
        method_path = 'packages/{}'.format(self.id)
        res = [i for i in method_path.split('/')]
        
        r = self._h._send(method="DELETE", resource=res)
        
        return r.ok


class PublicKey(BaseModel):
    """Xplenty Public Key."""

    _strs = ['name','comment', 'fingerprint', 'url', 'sort', 'direction']
    _ints = ['id']
    _floats = []
    _dates = ['created_at','updated_at']
    _dicts = []
    _pks = ['id']

    def __repr__(self):
        return "<Public Key '{0}'>".format(self.name)

    def new(self, public_key, name=None):
        return self._create_publickey(public_key, name=name)

    def _create_publickey(self, public_key, name=None):
        method_path = 'user/keys'
        special_url = SHORT_URL
        json_data = {}
        json_data['public_key'] = public_key
        if name:
            json_data['name'] = name

        r = self._h._send(method="POST", resource=method_path, data=json_data, special_url=special_url)
        key_id = json.loads(r.content).get('id')

        return self._h.public_key().get(key_id)

    def delete(self):
        return self._delete_publickey

    @property
    def _delete_publickey(self):
        method_path = 'user/keys/{}'.format(self.id)
        special_url = SHORT_URL
        res = [i for i in method_path.split('/')]
        
        r = self._h._send(method="DELETE", resource=res, special_url=special_url)

        return r.ok


class User(BaseModel):
    """Xplenty User."""

    _strs = ['name', 'email', 'gravatar_email', 'avatar_url', 'time_zone', 'location', 'api_key', 'url']
    _ints = ['id', 'notifications_count', 'unread_notifications_count']
    _dates = ['confirmed_at', 'created_at', 'updated_at']
    _bools = ['confirmed', 'receive_newsletter']
    _dicts = ['notification_settings']
    _pks = ['id']
    
    def __repr__(self):
        return "<User '{0}'>".format(self.name)

    def update_authenticated_user(self, current_password, **kwargs):
        method_path = 'user'
        special_url = 'https://api.xplenty.com/' 
        json_data = {}
        json_data['current_password'] = current_password
        json_data.update(return_matched_kwargs(locals()['kwargs'], User()._keys()))

        url = self._join_url(method_path, special_url=special_url)
        resp = self.get(url, json_data)

        return resp

    def reset_user_password(self, email):
        method_path = 'user_password'
        special_url = SHORT_URL
        json_data = {}
        json_data["email"] = email

        res = [i for i in method_path.split('/')]
        r = self._h._send(method="POST", resource=res, special_url=special_url, data=json_data)

        return r.ok


class Connection(BaseModel):
    """Xplenty Connection."""

    _strs = ['name','type', 'url']
    _ints = ['id']
    _dates = ['created_at','updated_at']
    _pks = ['id']

    def __repr__(self):
        return "<Connection '{0}'>".format(self.name)

    def delete(self):
        return self._delete_connection
    
    @property
    def _delete_connection(self):
        method_path = 'connections/{}/{}'.format(self.type, self.id)
        res = [i for i in method_path.split('/')]
        
        r = self._h._send(method="DELETE", resource=res)

        return r.ok


class ConnectionType(BaseModel):
    """Xplenty ConnectionType."""

    _strs = ['name', 'type', 'description', 'icon_url']
    _pks = ['name']
    _dicts = ['groups']

    def __repr__(self):
        return "<ConnectionType '{0}'>".format(self.name)


class Schedule(BaseModel):
    """Xplenty Schedule."""

    _strs = ['name','description', 'url', 'interval_unit', 'last_run_status', 'status', 'html_url', 'reuse_cluster_strategy']
    _ints = ['id','owner_id', 'interval_amount', 'execution_count']
    _floats = []
    _dates = ['created_at','updated_at', 'start_at', 'next_run_at', 'last_run_at']
    _dicts = ['task']
    _bools = ['overlap']
    _pks = ['id']

    def __repr__(self):
        return "<Schedule '{0}'>".format(self.name)

    def new(self, name, start_at=datetime.datetime.now(), interval_amount=1, interval_unit='hours', **kwargs):
        return self._create_scheldue(name, start_at=datetime.datetime.now(), interval_amount=1, interval_unit='hours', **kwargs) 

    def _create_scheldue(self, name, start_at=datetime.datetime.now(), interval_amount=1, interval_unit='hours', **kwargs):
        method_path = 'schedules'
        json_data = {}
        json_data['name'] = name
        json_data['start_at'] = start_at
        json_data['interval_amount'] = interval_amount
        json_data['interval_unit'] = interval_unit
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))
        
        r = self._h._send(method="POST", resource=method_path, data=json_data)
        schedule_id = json.loads(r.content).get('id')

        return self._h.schedule().get(schedule_id)

    def update_schedule(self, name, start_at=datetime.datetime.now(), interval_amount=1, interval_unit='hours', **kwargs):
        method_path = 'schedules/{}'.format(self.id)
        json_data = {}
        json_data['name'] = name
        json_data['start_at'] = start_at
        json_data['interval_amount'] = interval_amount
        json_data['interval_unit'] = interval_unit
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="PUT", resource=res, data=json_data)
        schedule_id = json.loads(r.content).get('id')

        return self._h.schedule().get(schedule_id)

    def watch_schedule(self, action=False):
        method_path = 'schedules/{}/watchers'.format(self.id)
        res = [i for i in method_path.split('/')]

        if action in ALLOWED_METHODS:
            r = self._h._send(method=action, resource=res)
            if action != 'DELETE':
                r = json.loads(r.content)
                return r 
            else:
                return r.ok
        else:
            return 'Fail method'

    def clone_schedule(self):
        method_path = 'schedules/{}/clone'.format(self.id)
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="POST", resource=res)
        schedule_id = json.loads(r.content).get('id')

        return self._h.schedule().get(schedule_id)

    def run_schedule(self):
        method_path = 'schedules/{}/run'.format(self.id)
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="POST", resource=res)
        schedule_id = json.loads(r.content).get('id')

        return self._h.schedule().get(schedule_id)

    def delete(self):
        return self._delete_schedules

    @property
    def _delete_schedules(self):
        method_path = 'schedules/{}'.format(self.id)
        res = [i for i in method_path.split('/')]
        
        r = self._h._send(method="DELETE", resource=res)

        return r.ok


class HookTypes(BaseModel):
    """Xplenty HookTypes."""

    _strs = ['name', 'type', 'description', 'icon_url']
    _dicts = ['groups']

    def __repr__(self):
        return "<Hook Types '{0}'>".format(self.name)


class HookEvents(BaseModel):
    """Xplenty HookEvents."""

    _strs = ['id', 'name', 'group_name']

    def __repr__(self):
        return "<Hook Event '{0}'>".format(self.id)


class Hook(BaseModel):
    """Xplenty Hook."""

    _strs = ['id', 'name', 'type', 'sort', 'direction', 'salt', 'url']
    _dates = ['since']
    _bools = ['active']
    _dicts = ['setting']
    _lists = ['events']
    _pks = ['id']

    def __repr__(self):
        return "<Hook '{0}'>".format(self.name)

    def new(self, hook_type, events, settings, **kwargs):
        return self._create_hook(hook_type, events, settings, **kwargs)

    def _create_hook(self, hook_type, events, settings, name, **kwargs):
        method_path = 'hooks'
        json_data = {}
        json_data['type'] = hook_type
        json_data['events'] = events
        json_data['settings'] = settings
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))

        r = self._h._send(method="POST", resource=method_path, data=json_data)
        hook_id = json.loads(r.content).get('id')

        return self._h.hook().get(hook_id)

    def update_hook(self, **kwargs):
        method_path = 'hooks/{}'.format(self.id)
        json_data = {}
        json_data.update(return_matched_kwargs(locals()['kwargs'], self._keys()))
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="PUT", resource=res, data=json_data)
        hook_id = json.loads(r.content).get('id')
        
        return self._h.hook().get(hook_id)

    def delete(self):
        return self._delete_hook

    @property
    def _delete_hook(self):
        method_path = 'hooks/{}'.format(self.id)
        res = [i for i in method_path.split('/')]
        
        r = self._h._send(method="DELETE", resource=res)

        return r.ok
    
    def ping_hook(self):
        method_path = 'hooks/{}/ping'.format(self.id)
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="GET", resource=res)
        hook_id = json.loads(r.content).get('id')
        
        return self._h.hook().get(hook_id)

    def reset_hook_salt(self):
        method_path = 'hooks/{}/reset_salt'.format(self.id)
        res = [i for i in method_path.split('/')]

        r = self._h._send(method="PUT", resource=res)
        new_salt = json.loads(r.content).get('salt')
        
        return new_salt


class Stack(BaseModel):
    """Xplenty Stacks."""

    _strs = ['name', 'id']
    _pks = ['name']

    def __repr__(self):
        return "<Stack '{0} {1}'>".format(self.id, self.name)


class Plan(BaseModel):
    """Xplenty Plan."""

    _strs = ['id', 'name', 'description', 'price_currency', 'price_unit', 
            'cluster_node_price_currency', 'cluster_node_price_unit']
    _ints = [ 'price_cents', 'cluster_node_hours_included', 'cluster_node_hours_limit',
            'cluster_node_price_cents', 'cluster_nodes_limit', 'cluster_size_limit',
            'clisters_limit', 'sanbox_clusters_limit', 'sandbox_node_hours_included',
            'sandbox_node_hours_limit', 'members_limit', 'position' ]
    _dates = ['created_at', 'updated_at']
    _pks = ['id']

    def __repr__(self):
        return "<Plan '{0}'>".format(self.name)


class PaymentMethod(BaseModel):
    """Xplenty PaymentMethod."""

    _strs = ['card_last_4', 'card_number', 'expiration_date', 'card_type', 'url']

    def __repr__(self):
        return "<PaymentMethod '{}-{}'>".format(self.card_number, self.card_type)

    def update_payment_method(self, billing_payment_token=None, plan_id=None):
        method_path = 'payment_method'
        json_data = {}
        if billing_payment_token:
            json_data['billing_payment_token'] = billing_payment_token
        if plan_id:
            json_data['plan_id'] = plan_id

        res = [i for i in method_path.split('/')]
        r = self._h._send(method="PUT", resource=res)
         
        return r.ok


class Product(BaseModel):
    """Xplenty Product."""

    _strs = ['title', 'body', 'body_html', 'body_text']
    _dates = ['created_at']
    _ints = ['id', 'likes']
    _bools = ['liked']
    _pks = ['id']

    def __repr__(self):
        return "<Product '{}-{}'>".format(self.id, self.title)

    def update_like_product(self):
        method_path = 'product_updates/{}/like'.format(self.id)
        special_url = SHORT_URL

        res = [i for i in method_path.split('/')]
        r = self._h._send(method="POST", resource=res, special_url=special_url)
        product = json.loads(r.content).get('id')
        
        return self._h.product().get(product)

class Region(BaseModel):
    """Xplenty Region."""

    _strs = ['name', 'group_name', 'id']
    _pks = ['id']

    def __repr__(self):
        return "<Region '{}'>".format(self.id)



class SysVariable(BaseModel):
    """Xplenty System Variables."""

    _strs = ['_COPY_PARALLELISM', '_PARQUET_COMPRESSION', '_PARQUET_PAGE_SIZE', '_PARQUET_BLOCK_SIZ']
    _ints = ['_MAX_COMBINED_SPLIT_SIZE', '_BYTES_PER_REDUCE', '_LINE_RECORD_READER_MAX_LENGTH', '_DEFAULT_PARALLELISM', '_COPY_TARGET_PARTITIONS', '_COPY_TARGET_SIZE']
    _dates = ['_DEFAULT_TIMEZONE']
    _floats = ['_SHUFFLE_INPUT_BUFFER_PERCENT']
    _pks = []

    def __repr__(self):
        return "<SysVariable>"


class Timezone(BaseModel):
    """Xplenty Timezones."""

    _strs = ['id', 'name']
    _pks = ['id']

    def __repr__(self):
        return "<Timezone '{}'>".format(self.id)


    
