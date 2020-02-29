#!/usr/bin/python3
import argparse
import logging
import subprocess
import sys

# set the logging level
logging.basicConfig(level=logging.DEBUG)

# set the argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-path", "--path", help="Provide openshift-install path")
parser.add_argument("-dir", "--dir", help="Cluster Directory")
parser.add_argument("-level", "--level", help="Log level")
args = parser.parse_args()

# executeCommand executes the cmd in a seperate shell and return its status code.
def executeCommand(args):
    cmdObject = subprocess.run(args=args)
    return cmdObject.returncode


# createCluster creates the oc cluster.
def createCluster():
    #print(args.path, args.dir, args.level)
    createCmd = '{} create cluster --dir {} --log-level {}'.format(args.path, args.dir, args.level)
    print(createCmd)
    returncode = executeCommand(createCmd.split())
    if returncode != 0:
        logging.error("failed to bring up the cluster")
        sys.exit()


if __name__ == "__main__":
    createCluster()