Xplenty PY
==========
The Xplenty PY is a python artifact that provides a simple wrapper for the Xplenty REST API.

Usage:
-----

Ceating a client object::

	from xplenty_api import XplentyClient


	account_id ="{Your Account ID}"
	api_key = "{Your API Key}"

	client = XplentyClient(account_id,api_key)
	

Getting Cluster Plans::

	plans = client.plans

	for plan in plans:
		print plan.id , plan.name


Getting All Clusters::

	clusters = client.clusters


	print "Number of clusters:",len(clusters)
	for cluster in clusters:
		print cluster.id, cluster.name, cluster.created_at


Create a cluster::

	plan_id = 1
	name ="New Cluster #199999"
	description ="New Cluster's Description"
	cluster = client.create_cluster(plan_id, name, description)

	print cluster.id


Get cluster information::

	id = 85

	cluster = client.get_cluster(id)

	print cluster.name


Terminate a cluster::

	id = 85
	cluster = client.terminate_cluster(id)
	print cluster.status

Jobs
-----
List jobs::


	jobs = client.jobs

	for job in jobs:
		
		print job.id , job.progress , job.status
		

Run a job::

	cluster_id = 83
	package_id = 782
	variables = {}
	variables['OUTPUTPATH']="test/job_vars.csv"
	variables['Date']="09-10-2012"

	job = client.add_job(cluster_id, package_id, variables)

	print job.id 


Get job info::

	job_id = 235

	job = client.get_job(job_id)

	print job.status

Stop a job::

	job_id = 235

	job = client.stop_job(job_id)

	print job.status
	
Account
-------
Get account limits::

	account = client.account_limits
	print "Account limit:", account.limit
	print "Account limit remaining:", account.remaining
		

License
=======
Xplenty PY is released under the [MIT License](http://www.opensource.org/licenses/MIT).


