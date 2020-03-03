## Login to the api.ci 
oc login https://api.ci.openshift.org --token=$tokenvalue

##Capture the username
user=$(oc whoami)

##Capture the password
passwd=$(oc whoami -t)

## login to the registry svc.ci.openshift.org
docker login -u $user -p $passwd registry.svc.ci.openshift.org

## get the pull-secret file into the curent directory
oc registry login --to=$(pwd)/installer/pull-secret

## get the openshift-install binary in the current working directory.
oc adm release extract --command=openshift-install --to installer/ \
registry.svc.ci.openshift.org/ocp/release:$clusterversion

## copy the install-config.yaml to the installer directory
cp $configpath $(pwd)/installer/install-config.yaml