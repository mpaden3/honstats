import json

import os
import argparse

from get_secrets import get_secret


def write_env(secrets, project_root, env_file_name=".env.local"):
    basedir = os.path.dirname(project_root + "/" + env_file_name)
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    envFile = open(project_root + "/" + env_file_name, "w+")
    for key in secrets.keys():
        envFile.write("%s=%s\n" % (key, secrets[key]))


parser = argparse.ArgumentParser(
    description="Copy secret files from aws secret manager"
)
parser.add_argument("name", metavar="Secret Name", help="Name of the secret")
parser.add_argument(
    "--region",
    metavar="AWS region",
    default="eu-central-1",
    help="Region where secret manager is located",
)
parser.add_argument(
    "--env-file",
    metavar="Env file",
    default=".env.local",
    help="Name of file with environment variables",
)
parser.add_argument(
    "--project-root", metavar="Project root", default=".", help="Root of the project"
)
args = vars(parser.parse_args())

secret_name = args["name"]
region_name = args["region"]
project_root = args["project_root"]
env_file_name = args["env_file"]

env_vars = json.loads(get_secret()["SecretString"])
write_env(env_vars, project_root, env_file_name)
