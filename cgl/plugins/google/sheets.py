import os
from oauth2client.service_account import ServiceAccountCredentials
import requests
from cgl.core.utils.read_write import load_json

"""
TODO:
1. Check if device id already exists in google doc, dont add it again
2. If file id already exists, dont add it to xml
"""


def authorize_sheets():
    """
    Authorizes api calls to the google sheet
    :param filepath: Path to the sheets json authentication file
    :param sheet_name: Title of the sheet being accessed
    :return: A google sheet object
    """
    import gspread
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']
    user_globals = load_json(os.path.join(os.path.expanduser(r'~\Documents'), 'cglumberjack', 'user_globals.json'))
    globals_ = load_json(user_globals['globals'])
    sheet_name = globals_['sync']['syncthing']['sheets_name']
    client_file = globals_['sync']['syncthing']['sheets_config_path']
    creds = ServiceAccountCredentials.from_json_keyfile_name(client_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1

    return sheet


def id_exists(id, sheet):
    """
    Checks to see if ID is already entered into the google sheet
    :param id: ID to look for in sheet
    :param sheet: Title of google sheet to search in
    :return: True if the value is already entered in the sheet, false if the value has no entry yet
    """
    data = sheet.col_values(1)
    for i in data:
        if i == id:
            return True
    return False


def name_exists(name, sheet):
    """
    Checks to see if name is already entered into the google sheet
    :param name: Name to look for in sheet
    :param sheet: Title of google sheet to search in
    :return: True if the value is already entered in the sheet, false if the value has no entry yet
    """
    data = sheet.col_values(2)
    for n in data:
        if n == name:
            return True
    return False


def find_empty_row_in_sheet(sheet):
    """
    Finds the first empty row in the google sheet
    :return: Integer representation of the first empty row
    """
    count = 1
    data = sheet.col_values(1)
    for i in data:
        if i == '':
            return count
        count += 1
    return count


def get_sheets_authentication():
    """
    Gets the json authentication file from amazon s3 and saves it on the local machine at the filepath
    :param client: The name of the client for the sheet
    :param filepath: The filepath where the authentication json will be saved
    :return: Returns the filepath to the local copy of the authentication file
    """
    # TODO - change this to read the ENV Variable once that's more stable/consistant.
    USER_GLOBALS = load_json(os.path.join(os.path.expanduser('~\Documents'), 'cglumberjack', 'user_globals.json'))
    GLOBALS = load_json(USER_GLOBALS['globals'])
    filepath = GLOBALS['sync']['syncthing']['sheets_config_path']
    if filepath.endswith('.json'):
        url = GLOBALS['sync']['syncthing']['sync_thing_url']
        r = requests.get(url, allow_redirects=True)
        with open(filepath, 'w+') as f:
            f.write(r.content)
        return filepath
    else:
        print('ERROR in sheets_config_path globals, %s does not match client.json format' % filepath)


# if __name__ == '__main__':
#     # sheet = authorize_sheets('LONE_COCONUT_SYNC_THING', 'C:\\Users\\Molta\\Desktop\\client.json')
#     # k = does_id_exist('2SB5KDS-FHJ5MEH-RJKY2QR-FLJ6S3R-4KQHBCW-2YZCRJJ-LULS7LQ-NUGWDAB', sheet)
#     # print k
#     # l = does_name_exist('DESKTOP-CEDFLDG', sheet)
#     # print l