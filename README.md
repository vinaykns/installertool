# installertool

### Updates install-config
tool.py ensures the provided install-config.yaml has upto date container registry (registry.svc.ci.openshift.org) auth value.
tool.py takes api.ci soft token, a current install-config.yaml file path and the cluster type to be installed, ex 4.4-ci
or 4.4-nightly

Sample command structure.
```
python3 tool.py -token $token -install-config $configpath -clustertype $clustertype
```

### Create cluster
Before running the create.py ensure that a directory is created and copy the updated install-config.yaml from the previous 
step to provide it as input.
```
python3 create.py -path $path -dir $dir -level $level
```

### Destroy cluster
Destroy the created cluster as shown below.
```
python3 destroy.py -path $path -dir $dir -level $level
```
