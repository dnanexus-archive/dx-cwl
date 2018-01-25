#!/usr/bin/env python
import subprocess
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def shell_suppress(cmd, ignore_error=False):
    out = ""
    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        if ignore_error:
            pass
        else:
            print e.output
            raise
    return out


def dx_login(token, project):
    shell_suppress("dx login --token {} --noprojects".format(token))
    shell_suppress("dx select {}".format(project))


def check_app_exists(return_json_str, app_version):
    return_json_str = json.loads(return_json_str)
    # dx describe will return only the newest version of app
    for i in return_json_str:
        if str(i['class']) == 'app':
            if str(i['version']) == app_version:
                logger.info("Current App already exists:")
                logger.info("App name: " + str(i['name']))
                logger.info("App version: " + str(i['version']))
                logger.info("App ID: " + str(i['id']))
                return str(i['id'])
            else:
                # TODO: if the provided app version is an old one?
                logger.info("A new version of App found:")
                logger.info("App name: " + str(i['name']))
                logger.info("Current App version: " + str(i['version']))
                logger.info("New App version: " + app_version + " will be published.")
                return False
    return False
