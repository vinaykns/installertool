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


# destroyCluster creates the oc cluster.
def destroyCluster():
    destroyCmd = '{} destroy cluster --dir {} --log-level {}'.format(args.path, args.dir, args.level)
    returncode = executeCommand(destroyCmd.split())
    if returncode != 0:
        logging.error("failed to destroy the cluster")
        sys.exit()


if __name__ == "__main__":
    destroyCluster()