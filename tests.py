import xplenty
import os
import sys
import time

# Test suite for the Xplenty Python SDK.

# A cluster will be created during testing.
# Make sure that the account used for testing
#   - has 0 clusters OR the capacity to accommodate an extra Sandbox cluster
#   - has at least one package
#   - has at least one schedule
# ... otherwise the tests will fail.
# Also note, a cluster in pending or creating state cannot be terminated and will throw validation error.

max_response = 20
new_job = {
    "variables": {"vegetable": "'tomato'", "pizza": "ClockTime()"},
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


def wait_for_cluster_creation(cluster):
    status = cluster.status.lower()
    round = 1
    info = "Waiting for cluster to finish creating ..."
    while status == "pending" or status == "creating":
        status = api.get_cluster(cluster.id).status.lower()
        if round == 5:
            print(str(info + " usually takes 1-2 minutes"))
        else:
            print(info)
        time.sleep(5)
        round += 1
    return cluster


class TestSuite:
    ERRORS = 0
    SIZE = 0
    SKIPPED = 0

    STYLES = {
        "BOLD": '\033[1m',
        "INFO": '\033[94m',
        "PASS": '\033[32m',
        "WARN": '\033[93m',
        "FAIL": '\033[91m',
        "END": '\033[0m'
    }

    def __init__(self):
        self.SIZE = len([function for function in dir(self)
                         if function.startswith("test_")])

    def run(self):
        self.prints("==== STARTING TESTS ====", [
                    self.STYLES["BOLD"], self.STYLES["INFO"]])

        # Clusters
        cluster = self.test_create_cluster(new_cluster["cluster_type"], new_cluster["nodes"],
                                           new_cluster["cluster_name"], new_cluster["cluster_description"],
                                           new_cluster["terminate_on_idle"], new_cluster["time_to_idle"])

        self.test_get_clusters()

        if cluster:
            self.test_get_cluster(cluster.id)
        else:
            self.SKIPPED += 1
            self.print_warn(
                "Skipping test: 'get_cluster' because create_cluster failed.")

        # Packages
        packages = self.test_get_packages()

        if packages:
            self.test_get_package(packages[0].id)
        else:
            self.SKIPPED += 1
            self.print_warn(
                "Skipping test: 'get_package' because get_packages failed.")

        # Schedules
        schedules = suite.test_get_schedules()

        if schedules:
            self.test_get_schedule(schedules[0].id)
        else:
            self.SKIPPED += 1
            self.print_warn(
                "Skipping test: 'get_schedule' because get_schedules failed.")

        # Account limits
        self.test_get_account_limits()

        # Jobs
        # add_job requires an Available cluster and a package
        job = None
        if cluster and packages:
            job = self.test_add_job(
                cluster.id, packages[0].id, new_job["variables"], new_job["dynamic_variables"])
        else:
            self.SKIPPED += 1
            self.print_warn(
                "Skipping test: 'add_job' because create_cluster or get_packages failed.")

        self.test_get_jobs()

        if job:
            self.test_get_job(job.id)
        else:
            self.SKIPPED += 1
            self.print_warn("Skipping test: 'get_job' because add_job failed.")

        # test_stop_job creates its own job if a cluster exists
        if cluster:
            self.test_stop_job(cluster.id, packages[0].id)
        else:
            self.SKIPPED += 1
            self.print_warn(
                "Skipping test 'stop_job' because create_cluster failed.")

        # Cluster termination
        if cluster:
            cluster = wait_for_cluster_creation(cluster)
            self.test_terminate_cluster(cluster.id)
        else:
            self.SKIPPED += 1
            self.print_warn(
                "Skipping test 'terminate_cluster' because create_cluster failed.")

        if self.SKIPPED > 0:
            self.prints("==== {skipped} TESTS SKIPPED ====".format(
                skipped=self.SKIPPED), [self.STYLES["WARN"]])

        if self.ERRORS == 0:
            self.prints("==== {passed}/{total} TESTS PASSED ====".format(passed=str(self.SIZE - self.SKIPPED), total=str(self.SIZE)),
                        [self.STYLES["BOLD"], self.STYLES["PASS"]])
            # no need to exit() here
        else:
            self.prints("==== {passed}/{total} TESTS FAILED ====".format(passed=str(self.ERRORS), total=str(self.SIZE)),
                        [self.STYLES["BOLD"], self.STYLES["FAIL"]])
            # exit(-1) signals failure
            sys.exit(-1)

    def prints(self, message, styles):
        style_str = ""
        for style in styles:
            style_str += style

        print(style_str + str(message) + self.STYLES["END"])

    def print_fail(self, message, error):
        self.prints(message + " FAIL - " + str(error), [self.STYLES["FAIL"]])

    def print_warn(self, message):
        self.prints(message, [self.STYLES["WARN"]])

    def print_pass(self, message):
        self.prints(message + " PASS", [self.STYLES["PASS"]])

    def test_get_clusters(self):
        name = "get_clusters"
        clusters = None
        try:
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
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

        return clusters

    def test_get_cluster(self, id):
        name = "get_cluster"
        cluster = None
        try:
            cluster = api.get_cluster(id)
            assert cluster is not None
            assert type(cluster) is xplenty.Cluster
            assert cluster.name
            assert cluster.id
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

        return cluster

    def test_create_cluster(self, cluster_type, nodes, cluster_name,
                            cluster_description, terminate_on_idle, time_to_idle):
        name = "create_cluster"
        cluster = None
        try:
            cluster = api.create_cluster(cluster_type, nodes,
                                         cluster_name, cluster_description,
                                         terminate_on_idle, time_to_idle)
            assert cluster is not None
            assert cluster.id
            assert cluster.type == cluster_type
            assert cluster.nodes == nodes
            assert cluster.name == cluster_name
            assert cluster.description == cluster_description
            assert cluster.terminate_on_idle == terminate_on_idle
            assert cluster.time_to_idle == time_to_idle
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

        return cluster

    # Trying to terminate a Creating cluster will cause a ValidationError.
    def test_terminate_cluster(self, id):
        name = "terminate_cluster"
        try:
            cluster = api.terminate_cluster(id)
            assert cluster is not None
            assert cluster.id == id
            assert cluster.status.lower() == "pending_terminate"
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

    def test_get_jobs(self):
        name = "get_jobs"
        jobs = None
        try:
            jobs = api.jobs
            assert jobs is not None
            assert type(jobs) is list
            assert len(jobs) <= max_response
            for job in jobs:
                assert type(job) is xplenty.Job
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

        return jobs

    def test_get_job(self, id):
        name = "get_job"
        job = None
        try:
            job = api.get_job(id)
            assert job is not None
            assert type(job) is xplenty.Job
            assert job.id
            assert job.cluster_id
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

        return job

    # Trying to stop a "Failed" job will throw validation error.
    def test_stop_job(self, cluster_id, package_id):
        name = "stop_job"
        started_job = None
        try:
            # a job needs to be started first, cluster and package must exist
            started_job = api.add_job(
                cluster_id, package_id, new_job["variables"], new_job["dynamic_variables"])
            assert started_job is not None
            res = api.stop_job(started_job.id)
            assert res is not None
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

    def test_add_job(self, cluster_id, package_id, vars, dynamic_vars):
        name = "add_job"
        job = None
        try:
            job = api.add_job(cluster_id, package_id, vars, dynamic_vars)
            assert job is not None
            assert job.id
            assert job.package_id == package_id
            assert job.cluster_id == cluster_id
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

        return job

    def test_get_account_limits(self):
        name = "get_account_limits"
        try:
            account_limits = api.account_limits
            assert account_limits is not None
            assert type(account_limits) is xplenty.AccountLimits
            assert account_limits.limit
            assert account_limits.remaining
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

    def test_get_packages(self):
        name = "get_packages"
        packages = None
        try:
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
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

        return packages

    def test_get_package(self, id):
        name = "get_package"
        try:
            package = api.get_package(id)
            assert type(package) is xplenty.Package
            assert package.name
            assert package.id
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

    def test_get_schedules(self):
        name = "get_schedules"
        schedules = None
        try:
            schedules = api.schedules
            assert schedules is not None
            assert type(schedules) is list
            assert len(schedules) <= max_response
            for schedule in schedules:
                assert type(schedule) is xplenty.Schedule
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)

        return schedules

    def test_get_schedule(self, id):
        name = "get_schedule"
        try:
            schedule = api.get_schedule(id)
            assert type(schedule) is xplenty.Schedule
            assert schedule.name
            assert schedule.id
            self.print_pass(name)
        except Exception as e:
            self.ERRORS += 1
            self.print_fail(name, e)


if __name__ == "__main__":
    suite = TestSuite()

    id_env_key = "XPLENTY_ACCOUNT_ID"
    api_env_key = "XPLENTY_API_KEY"
    # You may replace the Nones with your API credentials if you don't want to put them in the env.
    account_id = str(os.environ.get(id_env_key, None))
    api_key = str(os.environ.get(api_env_key, None))
    api = None
    if account_id and api_key:
        api = xplenty.XplentyClient(account_id, api_key)
    else:
        msg = "API credentials must be in this file or in the env under " + \
            id_env_key + " and " + api_env_key
        suite.prints(msg, [suite.STYLES["BOLD"], suite.STYLES["FAIL"]])
        suite.prints("Halting tests.", [
                     suite.STYLES["BOLD"], suite.STYLES["FAIL"]])
        sys.exit(-1)

    suite.run()
