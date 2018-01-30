#!/usr/bin/env python
import subprocess
import json
import sys
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


def find_all_apps(app_name):
    find_apps_return_json = subprocess.check_output("dx find apps --name {0} -a --json ".format(app_name), shell=True)
    return json.loads(find_apps_return_json)


def find_one_app(app_name, app_version):
    res = find_all_apps(app_name)
    if not res:
        logger.error("Couldn't find the app {0}".format(app_name))
        sys.exit(1)
    else:
        for i in res:
            if i["describe"]["version"] == app_version:
                return i["id"]
    logger.error("Couldn't find the app {0}:{1}".format(app_name, app_version))


def check_app_exists(app_name, app_version):
    logger.info("Trying to build an app {0}:{1}".format(app_name, app_version))
    find_apps_return_json = find_all_apps(app_name)
    list_of_app_version = []
    if not find_apps_return_json:
        logger.info("A new app will be published ...")
    else:
        logger.info("Currently available version:")
        for i in find_apps_return_json:
            app_version_founded = i["describe"]["version"]
            list_of_app_version.append(app_version_founded)
            logger.info(app_version_founded)
    if app_version in list_of_app_version:
        logger.error("The version is already published.")
        sys.exit(1)


def get_image_name(asset_id):
    describe_return_json = subprocess.check_output("dx describe {0} --json".format(asset_id), shell=True)
    describe_return_json = json.loads(describe_return_json)
    image_name = describe_return_json['name']
    return image_name


def find_images_for_applet(required_images_list, provided_assets, run_spec_asset_depends):
    if required_images_list:
        if not provided_assets:
            logger.error("The following images are required to build the applet:")
            logger.error(",".join(required_images_list))
            sys.exit(1)
        else:
            logger.info("Docker images assets used:")
            for x in provided_assets:
                image_name = get_image_name(x)
                if image_name in required_images_list:
                    run_spec_asset_depends.append({"id": x})
                    required_images_list.remove(image_name)
                    logger.info(x)
            if required_images_list:
                logger.error("Couldn't find the images:")
                logger.error(",".join(required_images_list))
                sys.exit(1)


def return_file_details(file_id):
    """
    Return a dictionary to be used as 'suggestions' field in dxapp.json
    :param file_id: suggested file id
    :return:
    """
    describe_file_json = subprocess.check_output("dx describe {0} --json".format(file_id), shell=True)
    describe_file_json = json.loads(describe_file_json)
    return {
        "name": describe_file_json['name'],
        "project": describe_file_json['project'],
        "path": describe_file_json['folder'],
        "id": file_id
    }


def get_default_input_files_from_cwl_hints(input_hints, default_dnanexus_input_dict):
    # TODO: Too many loops and ifs
    for i in input_hints:
        if i.get('class', '') == 'Any':
            for j, k in i.items():
                if j != 'class':
                    if j not in default_dnanexus_input_dict:
                        default_dnanexus_input_dict[j] = [return_file_details(k)]
                    else:
                        default_dnanexus_input_dict[j].append(return_file_details(k))
