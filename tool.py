#!/usr/bin/python3
import argparse
import json
import shlex, subprocess
import re
import logging
import os, sys
from shutil import copyfile, rmtree
import yaml
import requests

# set the logging level
logging.basicConfig(level=logging.DEBUG)

# set the argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-token", "--token", help="Cli Soft Token")
parser.add_argument("-install-config", "--config", help="Provide install-config.yaml path")
parser.add_argument("-clustertype", "--type", help="Cluster version")
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


def setenvvariables():
    # sets the env variables to run the shell script.

    if args.token:
        os.environ["tokenvalue"] = args.token

    if args.config:
        os.environ["configpath"] = args.config

    if args.type:
        version = ""
        majorVer = args.type[:3]
        if "ci" in args.type:
            minorVer = ".0-0.ci"
        else:
            minorVer = ".0-0.nightly"
        

        version = majorVer + minorVer
        cmd = 'https://openshift-release.svc.ci.openshift.org/api/v1/releasestream/{}/latest'.format(version)
        cmdRequest = requests.get(cmd)
        cmdDict = json.loads(cmdRequest.text)
        os.environ["clusterversion"] = cmdDict['name']

    scriptPath = os.curdir + '/script.sh'
    if commandReturnStatus(scriptPath) !=  True:
        sys.exit(1)

def updateSvcregistryauth():
    # update the auth of container registry "registry.svc.ci.openshift.org"
    # from the install-config.yaml file
    
    # change directory to where the required files are present.
    os.chdir("installer")


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

    # check if installer is present, if present delete the dir, else create it.
    if os.path.isdir("installer"):
        rmtree("installer", ignore_errors=True)
   
    os.mkdir(path)
    logging.info('Directory {} created in {}'.format(directory, currDir))

    # Download the openshift-install binary corresponding to the version specified.
    setenvvariables()

    # update the auth for the svc registry.
    updateSvcregistryauth()