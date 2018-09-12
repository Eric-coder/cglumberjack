import os
import sys
import yaml
import shutil


class Configuration(object):
    """

    class for storing config values from files, usable simply as a dictionary

    """
    LOADED_CONFIG = {}
    user_dir = os.path.expanduser("~")
    cg_lumberjack_dir = os.path.join(user_dir, 'Documents', 'cglumberjack')

    def __init__(self):
        if not Configuration.LOADED_CONFIG:
            self.make_cglumberjack_dir()
            global_cfg, app_cfg = self._find_config_file()
            cfg = {}
            if os.path.isfile(global_cfg):
                cfg.update(self._load_yaml(global_cfg))
            if os.path.isfile(app_cfg):
                cfg.update(self._load_yaml(app_cfg))
            Configuration.LOADED_CONFIG['app'] = cfg

    def make_cglumberjack_dir(self):
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cfg", "global.yaml")
        to_path = os.path.join(self.cg_lumberjack_dir, 'global.yaml')
        if os.path.exists(self.cg_lumberjack_dir):
            if 'global.yaml' not in os.listdir(self.cg_lumberjack_dir):
                shutil.copy2(base, to_path)
        else:
            os.makedirs(self.cg_lumberjack_dir)
            shutil.copy2(base, to_path)

    def _find_config_file(self):

        template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cfg")
        app_name = os.path.basename(sys.argv[0])
        # this doesn't seem to be used but it's a great idea
        app_cfg = os.path.join(template_folder, os.path.splitext(app_name)[0] + ".yaml")
        if os.path.exists(self.cg_lumberjack_dir):
            global_cfg = os.path.join(self.cg_lumberjack_dir, 'global.yaml')
        else:
            self.make_cglumberjack_dir()
            global_cfg = os.path.join(self.cg_lumberjack_dir, 'global.yaml')
        print 'Global Config Location: ', global_cfg
        return global_cfg, app_cfg

    @staticmethod
    def _load_yaml(path):
        with open(path, 'r') as stream:
            try:
                result = yaml.load(stream)
                if result:
                    return result
                else:
                    return {}
            except yaml.YAMLError as exc:
                print(exc)
                sys.exit(99)


def config():
    """
    get the whole configuration

    Returns: dict


    """
    return Configuration().LOADED_CONFIG


def app_config():
    """
    get the app configuration

    Returns: dict

    """
    return Configuration().LOADED_CONFIG['app']
