import requests
import shutil
import os
import click
import sys
import xmltodict
import json

authorize = ""


def get_section_id(section_name):
    r = requests.get("https://app.asana.com/api/1.0/projects/%s/sections" % get_project_id(), headers={'Authorization': "%s" % authorize})
    response = json.loads(r.content)
    for t in response['data']:
        if t['name'] == section_name:
            return t['gid']


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


def get_workspace_id():
    with open(get_workspace_xml()) as xmlfile:
        docs = xmltodict.parse(xmlfile.read())
    for item in docs['project']['component']:
        if item['@name'] == "TaskManager":
            for element in item['servers']['Generic']['option']:
                if element['@name'] == "templateVariables":
                    return element['list']['TemplateVariable'][1]['option'][1]['@value']


def search_tasks(task_name):
    r = requests.get("https://app.asana.com/api/1.0/projects/%s/tasks" % get_project_id(),
                     headers={'Authorization': "%s" % authorize})
    # print r
    # print r.status_code
    dict = json.loads(r.content)
    for i in dict['data']:
        if task_name == i['gid']:
            return 1
    return 0


def create_task(task_name):
    body = {
        "data": {
            "name": task_name,
            "memberships": [
                {
                    "project": "%s" % get_project_id(),
                    "section": "%s" % get_section_id("In Progress")
                }
            ],
            "workspace": get_workspace_id()
        }
    }
    r = requests.post("https://app.asana.com/api/1.0/tasks", headers={'Authorization': "%s" % authorize}, json=body)
    t = json.loads(r.content)
    return t['data']['gid']


@click.command()
@click.option('--get', '-g', default=False, help='Get command to retrieve Asana information')
@click.option('--section', '-s', default=False, help='Special command to get section id of current project')
@click.option('--task', '-t', default=False, help='Command to search if task exists in asana workspace')
def main(get, section, task):
    if section:
        return get_section_id(section)
    elif get == 'pid':
        print get_project_id()
        return get_project_id()
    elif get == 'wid':
        print get_workspace_id()
        return get_workspace_id()
    elif task:
        result = search_tasks(task)
        if result == 0:
            task_id = create_task(task)
            print task_id
            return task_id
        elif result == 1:
            print "exists"


if __name__ == "__main__":
    main()