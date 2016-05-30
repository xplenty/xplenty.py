## Xplenty Python Wrapper

[ ![Codeship Status for xplenty/xplenty.py](https://codeship.com/projects/0e6524f0-8528-0133-0e8b-123c7a12e678/status?branch=master)](https://codeship.com/projects/122186)

The Xplenty PY is a python artifact that provides a simple wrapper for the [Xplenty REST API](https://github.com/xplenty/xplenty-api-doc). To use it, create an XplentyClient object and call its methods to access the Xplenty API. This page describes the available XplentyClient methods.

### Installation

Via pip:
```bash
pip install xplenty
```

### Create an Xplenty Client Object
Pass your account ID and API key to the XplentyClient constructor.
```python
from xplenty import XplentyClient
account_id ="MyAccountID"
api_key = "V4eyfgNqYcSasXGhzNxS"
client = XplentyClient(account_id, api_key)
```
### List All Clusters

This method returns the list of clusters that were created by users in your account.
You can use this information to monitor and display your clusters and their statuses.
```python
clusters = client.clusters()
print "Number of clusters:",len(clusters)
for cluster in clusters:
    print cluster.id, cluster.name, cluster.created_at
```
### Get Cluster Information

This method returns the details of the cluster with the given ID.
```python
id = 85
cluster = client.clusters().get(id)
print cluster.name
```
### Terminate a Cluster

This method deactivates the given cluster, releasing its resources and terminating its runtime period. Use this method when all of the cluster's jobs are completed and it's no longer needed. The method returns the given cluster's details, including a status of "pending_terminate".
```python
id = 85
cluster = client.clusters().get(id)._terminate_cluster()
print cluster.status
```

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

## License
Released under the [MIT license](http://www.opensource.org/licenses/mit-license.php).
