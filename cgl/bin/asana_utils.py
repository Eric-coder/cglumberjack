import requests
import shutil
import os
import click
import sys
from cgl.core.config import app_config
from core.util import load_xml, save_xml, cgl_copy


ROOT = app_config()['paths']['code_root']


def get_project_id():
    xml_file = os.path.join(ROOT, 'resources', 'pycharm_setup', 'workspace.xml')
    docs = load_xml(xml_file)
    for item in docs['project']['component']:
        if item['@name'] == "TaskManager":
            for element in item['servers']['Generic']['option']:
                if element['@name'] == "templateVariables":
                    return element['list']['TemplateVariable'][0]['option'][1]['@value']


@click.command()
@click.option('--get', '-g', default=False, help='Get command to retrieve Asana information')
def main(get):
    if get == 'pid':
        print get_project_id()
        return get_project_id()


if __name__ == "__main__":
    main("pid")