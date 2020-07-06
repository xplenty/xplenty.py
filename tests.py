import xplenty

# This test suite will terminate jobs and clusters. Use with care.
# It is advisable to create 1 new cluster for this test suite.

# The following is required by the test suite:
# 1 cluster, 1 job, 1 pacakge, 1 schedule
# Fill in the below variables with their ID
max_response = 20
# replace this cluster_id on each run (gets deleted during test)
cluster_id = 1272885
# job can be of any status
job_id = 35967363
# ensure package is valid
package_id = 130202
schedule_id = 7894
new_job = {
    "variables" : {"vegetable": "'tomato'", "pizza":"ClockTime()"},
    "dynamic_variables": {"dynamic": "ClockTime()"}
}
new_cluster = {
    "cluster_type": "sandbox", 
    "nodes": 1,
    "cluster_name": "SDK Test",
    "cluster_description": "Created from Python SDK",
    "terminate_on_idle": False, 
    "time_to_idle": 3600
}
account_id ="<account>"
api_key = "<key>"

api = xplenty.XplentyClient(account_id,api_key)

def test_get_clusters():
    clusters = api.clusters
    assert clusters is not None
    assert type(clusters) is list
    assert len(clusters) <= max_response
    for cluster in clusters:
        assert type(cluster) is xplenty.Cluster
    
    clusters = api.get_clusters(offset=0, limit=max_response - 1)
    assert clusters is not None
    assert type(clusters) is list
    assert len(clusters) <= max_response - 1
    for cluster in clusters:
        assert type(cluster) is xplenty.Cluster
    
    print "get_clusters OK"

def test_get_cluster(id):
    cluster = api.get_cluster(id)
    assert cluster is not None
    assert type(cluster) is xplenty.Cluster
    assert cluster.name
    assert cluster.id

    print "get_cluster OK"

def test_create_cluster(cluster_type, nodes, cluster_name, cluster_description, terminate_on_idle, time_to_idle):
    cluster = api.create_cluster(cluster_type, nodes, cluster_name, cluster_description, terminate_on_idle, time_to_idle)
    assert cluster is not None
    assert cluster.id
    assert cluster.type == cluster_type
    assert cluster.nodes == nodes
    assert cluster.name == cluster_name
    assert cluster.description == cluster_description
    assert cluster.terminate_on_idle == terminate_on_idle
    assert cluster.time_to_idle == time_to_idle

    print "create_cluster OK"
    
def test_terminate_cluster(id):
    cluster = api.terminate_cluster(id)
    assert cluster is not None
    assert cluster.id == id
    assert cluster.status.lower() == "pending_terminate"
    
def test_get_jobs():
    jobs = api.jobs
    assert jobs is not None
    assert type(jobs) is list
    assert len(jobs) == max_response
    for job in jobs:
        assert type(job) is xplenty.Job

    print "get_jobs OK"

def test_get_job(id):
    job = api.get_job(id)
    assert job is not None
    assert type(job) is xplenty.Job
    assert job.id
    assert job.cluster_id
    
    print "get_job OK"

# Trying to stop a "Failed" job will throw validation error.
def test_stop_job():
    # a job needs to be started first, cluster and package must exist
    started_job = api.add_job(cluster_id, package_id, new_job["variables"], new_job["dynamic_variables"])
    assert started_job is not None
    res = api.stop_job(started_job.id)
    assert res is not None

    print "stop_job OK"

def test_add_job(cluster_id, package_id, vars, dynamic_vars):
    job = api.add_job(cluster_id, package_id, vars, dynamic_vars)
    assert job is not None 
    assert job.id
    assert job.package_id == package_id
    assert job.cluster_id == cluster_id

    print "add_job OK"

def test_get_account_limits():
    account_limits = api.account_limits
    assert account_limits is not None
    assert type(account_limits) is xplenty.AccountLimits
    assert account_limits.limit
    assert account_limits.remaining

    print "get_account_limits OK"

def test_get_packages():
    packages = api.packages
    assert packages is not None
    assert type(packages) is list
    assert len(packages) <= max_response
    for package in packages:
        assert type(package) is xplenty.Package

    packages = api.get_packages(offset=0, limit=max_response - 1)
    assert packages is not None
    assert type(packages) is list
    assert len(packages) <= max_response - 1
    for package in packages:
        assert type(package) is xplenty.Package

    print "get_packages OK"

def test_get_package(id):
    package = api.get_package(id)
    assert type(package) is xplenty.Package
    assert package.name
    assert package.id

    print "get_package OK"

def test_get_schedules():
    schedules = api.schedules
    assert schedules is not None
    assert type(schedules) is list
    assert len(schedules) <= max_response
    for schedule in schedules:
        assert type(schedule) is xplenty.Schedule

    print "get_schedules OK"

def test_get_schedule(id):
    schedule = api.get_schedule(id)
    assert type(schedule) is xplenty.Schedule
    assert schedule.name
    assert schedule.id

    print "get_schedule OK"

if __name__ == "__main__":
    test_get_clusters()
    test_get_cluster(cluster_id)
    test_get_packages()
    test_get_package(package_id)
    test_get_schedules()
    test_get_schedule(schedule_id)
    test_get_account_limits()
    test_get_jobs()
    test_get_job(job_id)
    # add_job requires an Available cluster and a package
    test_add_job(cluster_id, package_id, new_job["variables"], new_job["dynamic_variables"])
    # test_stop_job creates its own job
    test_stop_job()
    # terminate cluster should come before create_cluster, in case account cant have more than 1 cluster
    test_terminate_cluster(cluster_id)
    test_create_cluster(new_cluster["cluster_type"], new_cluster["nodes"], 
                        new_cluster["cluster_name"], new_cluster["cluster_description"], 
                        new_cluster["terminate_on_idle"], new_cluster["time_to_idle"])