import requests
import shutil
import os
import click
import sys
import xmltodict



def get_workspace_xml():
    home = os.path.expanduser("~")
    xml_file = os.path.join(home, "PycharmProjects", "cglumberjack", ".idea", "workspace.xml")
    return xml_file


def get_project_id():
    with open(get_workspace_xml()) as xmlfile:
        docs = xmltodict.parse(xmlfile.read())
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
    main()