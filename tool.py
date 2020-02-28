#!/usr/bin/python3
import argparse
import json
import shlex, subprocess
import re
import logging
import os, sys
from shutil import copyfile
import yaml

# set the logging level
logging.basicConfig(level=logging.DEBUG)

# set the argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-token", "--token", help="Cli Soft Token")
parser.add_argument("-install-config", "--config", help="Provide install-config.yaml path")
parser.add_argument("-version", "--version", help="Cluster version")
args = parser.parse_args()


def commandReturnStatus(cmd):
    # executes the cmd and returns its status code.
    return subprocess.call(cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def executeCommand(args):
    # executes the cmd in a seperate shell and returns its object
    cmdObject = subprocess.run(args=args, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    return cmdObject

def checkocbinary():
    # check if oc binary is present on the localhost
    if commandReturnStatus("type oc"):
        # check the version of the oc binary to make sure it is
        # atleast v4.2+
        args = ['oc', 'version', '--short']
        cmdObject = executeCommand(args)
        
        # currently it continues even though the return code is non zero, as we always don't
        # need to have a server up and running.
        cmdStdout = cmdObject.stdout.decode("utf-8")
    
        for each in cmdStdout.split('\n'):
            data = each.split(':')
            if data[0] == 'Client Version':
                req = data[1]
                reObject = re.search('v4.*', req)
                rawString = req[reObject.start():reObject.end()]
                versionNo = int(re.sub(r'[.]','',rawString[:4][1:]))
                if versionNo >= 42:
                    logging.info("oc binary of atleast 4.2 version is found on the localhost")
                    return True
                else:
                    # TODO: Need to implement the case if there isn't oc binary of version atleast v4.2.
                    return False


def getReqFiles():
    # get the openshift-install binary for the corresponding version.
    # login into the api.ci.openshift.org using the token
    command = 'oc login https://api.ci.openshift.org --token={}'.format(args.token)

    if commandReturnStatus(command):
        logging.info("successful login into api.ci.openshift.org")
    
    # Get the username
    userCmd = 'oc whoami'
    usercmdObject = executeCommand(userCmd.split())
    if usercmdObject.returncode != 0:
        logging.error("unable to get the user name")
        sys.exit()

    user = usercmdObject.stdout.decode("utf-8")
    
    # Get the password for the user associated with
    passCmd = 'oc whoami -t'
    passcmdObject = executeCommand(passCmd.split())
    if passcmdObject.returncode != 0:
        logging.error("unable to get the password")
        sys.exit()
    
    password = passcmdObject.stdout.decode("utf-8")

    # login to the registry svc.ci.openshift.org
    dockerLoginCmd = 'docker login -u {} -p {} registry.svc.ci.openshift.org'.format(user, password)
    dockerLoginCmdObject = executeCommand(dockerLoginCmd.split())
    if dockerLoginCmdObject.returncode != 0:
        logging.error("docker login failed to execute")
        sys.exit()
    
    # get the pull-secret file into the curent directory
    pullsecretFileCmd = 'oc registry login --to=pull-secret'
    pullsecretFileCmdObject = executeCommand(pullsecretFileCmd.split())
    if pullsecretFileCmdObject.returncode != 0:
        logging.error("failed to obtain the pull-secret file")
        sys.exit()
    
    # get the openshift-install binary in the current working directory.
    ocInstallCmd = 'oc adm release extract --command=openshift-install \
        registry.svc.ci.openshift.org/ocp/release:{}'.format(args.version)
    ocInstallCmdObject = executeCommand(ocInstallCmd.split())
    if ocInstallCmdObject.returncode != 0:
        logging.error("failed to download the openshift-install binary")
        sys.exit(1)
    
    # copy the install-config.yaml into the current directory
    dst = os.getcwd() + "/" + "install-config.yaml"
    copyfile(args.config, dst)




def updateSvcregistryauth():
    # update the auth of container registry "registry.svc.ci.openshift.org"
    # from the install-config.yaml file
    # have a pre requisite knowledge that pull-secret file will be present in the
    # current working directory.
    f = open("pull-secret")
    data = json.load(f)
    svcAuth = data['auths']['registry.svc.ci.openshift.org']['auth']
    f.close()

    # update the auth in install-config.yaml with svcAuth.
    f = open("install-config.yaml")
    data = yaml.load(f, Loader=yaml.FullLoader)
    pullSecretData = json.loads(data['pullSecret'])
    pullSecretData['auths']['registry.svc.ci.openshift.org']['auth'] = svcAuth
    data['pullSecret'] = json.dumps(pullSecretData)
    data['pullSecret'] = data['pullSecret'].replace(" ", "")
    f.close()
    os.rename('install-config.yaml', 'install-config.yaml.old')

    # Dump the updated yaml data into a new file.
    with open('install-config.yaml', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

    outfile.close()


if __name__ == "__main__":
    # step1: Check if the oc binary is available else get a v4.2+ binary
    response = checkocbinary()

    # create a working space directory.
    currDir = os.getcwd()
    directory = "installer"
    path = os.path.join(currDir, directory)
    os.mkdir(path)
    logging.info('Directory {} created in {}'.format(directory, currDir))

    # change to the path directory 
    os.chdir(path)

    # Download the openshift-install binary corresponding to the version specified.
    getReqFiles()

    # update the auth for the svc registry.
    updateSvcregistryauth()