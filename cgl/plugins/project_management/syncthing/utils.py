import xml.etree.ElementTree as ET
import getpass
import subprocess
import cgl.plugins.google.sheets as G


def get_config_path():
    """
    Gets the full path to the syncthing config file
    :return: A string containing the full path to the config file
    """
    command = "syncthing -paths"
    return_output = False
    print_output = True
    output_values = []
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if return_output or print_output:
        while True:
            output = p.stdout.readline()
            if output == '' and p.poll() is not None:
                break
            if output:
                output_values.append(output.strip())
    print output_values[1]
    return output_values[1]


def get_my_device_info():
    """
    Retreives current device's information from the syncthing config file
    :return: A dictionary with the device ID and device name
    """
    filepath = get_config_path()
    tree = ET.parse(filepath)
    root = tree.getroot()
    device_id = root[0][1].get('id')
    machine_name = ''

    for child in root:
        if child.tag == 'device' and child.get('id') == device_id:
            machine_name = child.get('name')
            print machine_name

    return {'id': device_id, 'name': machine_name}


def add_device_info_to_sheet(sheet):
    """
    Adds current device information to google sheet
    :param sheet: The sheet object to be edited
    :return:
    """
    new_row = G.find_empty_row_in_sheet(sheet)
    device_dictionary = get_my_device_info()
    sheet.update_cell(new_row, 1, device_dictionary['id'])
    sheet.update_cell(new_row, 2, device_dictionary['name'])
    sheet.update_cell(new_row, 3, getpass.getuser().lower())


def get_all_device_info(sheet):
    """
    Gets all devices currently entered into syncthing
    :return: Array of dictionaries containing necessary device information
    """
    device_list = []
    num_of_rows = G.find_empty_row_in_sheet(sheet)
    for row in range(2, num_of_rows):
        if sheet.cell(row,1).value != get_my_device_info()['id']:
            entry = {"id": sheet.cell(row, 1).value, "name": sheet.cell(row,2).value, "user": sheet.cell(row,3).value}
            device_list.append(entry)
    print device_list
    return device_list


def add_all_devices_to_config(sheet):
    """
    Add a new device to be synched with in syncthing
    :return:
    """
    device_list = get_all_device_info(sheet)
    filepath = get_config_path()
    tree = ET.parse(filepath)
    root = tree.getroot()

    for entry in device_list:
        new_node = ET.SubElement(root, 'device')
        new_node.set('id', entry['id'])
        new_node.set('name', entry['name'])
        new_node.set('compression', "metadata")
        new_node.set("introducer", "false")
        new_node.set("skipIntroductionRemovals", 'false')
        new_node.set("introducedBy", "")
        address = ET.SubElement(new_node, 'address')
        address.text = 'dynamic'
        paused = ET.SubElement(new_node, 'paused')
        paused.text = "false"
        autoAcceptFolders = ET.SubElement(new_node, 'autoAcceptFolders')
        autoAcceptFolders.text = "false"
        maxSendKbps = ET.SubElement(new_node, 'maxSendKbps')
        maxSendKbps.text = 0
        maxRecvKbps = ET.SubElement(new_node, 'maxRecvKbps')
        maxRecvKbps.text = 0
        maxRequestKiB = ET.SubElement(new_node, 'maxRequestKiB')
        maxRequestKiB.text = 0

    tree.write(filepath)


def add_folder_to_config(folder_id, filepath):
    """
    Function to add a new folder to be synched through syncthing
    :param folder_id: The ID label for the folder being added to syncthing
    :param filepath: The path to the file being added to syncthing
    :return:
    """

    config_path = get_config_path()
    tree = ET.parse(config_path)
    root = tree.getroot()

    new_node = ET.SubElement(root, 'folder')
    new_node.set('id', folder_id)
    new_node.set('path', filepath)
    new_node.set('type', 'sendreceive')
    new_node.set('rescanIntervalS', '3600')
    new_node.set('fsWatcherEnabled', "True")
    new_node.set('fsWatcherDelayS', "10")
    new_node.set('ignorePerms', "false")
    new_node.set('autoNormalize', "true")
    tree.write(config_path)


if __name__ =="__main__":
    # file_location = G.get_sheets_authentication('C:\\Users\\Molta\\Desktop')
    sheet1 = G.authorize_sheets('LONE_COCONUT_SYNC_THING', 'C:\\Users\\Molta\\Desktop\\client.json')
    # add_device_info_to_sheet(sheet1)
    #add_all_devices_to_config(sheet1)
    add_folder_to_config('kyls_new_file', 'C:\\Users\\Molta\\test')