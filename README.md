# installertool

### Updates install-config
tool.py ensures the provided install-config.yaml has upto date container registry (registry.svc.ci.openshift.org) auth value. 
Sample command structure.
```
python3 tool.py -token $token -install-config $path -version $version
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
