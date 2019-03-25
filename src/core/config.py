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
    user_config = os.path.join(cg_lumberjack_dir, 'user_config.yaml')

    def __init__(self, company=None):
        if company:
            Configuration.LOADED_CONFIG = {}
        if not Configuration.LOADED_CONFIG:
            self.make_cglumberjack_dir()
            if company:
                self.company_global_dir = os.path.join(self.cg_lumberjack_dir, 'companies', company)
            else:
                self.company_global_dir = None
            global_cfg, app_cfg = self._find_config_file()
            cfg = {}
            cfg['cg_lumberjack_dir'] = self.cg_lumberjack_dir
            if os.path.isfile(global_cfg):
                cfg.update(self._load_yaml(global_cfg))
            if os.path.isfile(app_cfg):
                cfg.update(self._load_yaml(app_cfg))
            Configuration.LOADED_CONFIG['app'] = cfg

    def make_cglumberjack_dir(self):
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cfg", "global_template.yaml")
        to_path = os.path.join(self.cg_lumberjack_dir, 'global.yaml')
        if os.path.exists(self.cg_lumberjack_dir):
            # make the "studio level" global.yaml
            if 'global.yaml' not in os.listdir(self.cg_lumberjack_dir):
                shutil.copy2(base, to_path)
        else:
            os.makedirs(self.cg_lumberjack_dir)
            shutil.copy2(base, to_path)

    def make_company_global_dir(self):
        default_global = os.path.join(self.cg_lumberjack_dir, 'global.yaml')
        to_path = os.path.join(self.company_global_dir, 'global.yaml')
        print 'made it here'
        if os.path.exists(self.company_global_dir):
            print 'Copying from %s to %s' % (default_global, to_path)
            if 'global.yaml' not in os.listdir(self.company_global_dir):
                shutil.copy2(default_global, to_path)
        else:
            print '%s does not exist' % self.company_global_dir
            os.makedirs(self.company_global_dir)
            shutil.copy2(default_global, to_path)

    def _find_config_file(self):
        template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cfg")
        app_name = os.path.basename(sys.argv[0])
        # this doesn't seem to be used but it's a great idea
        app_cfg = os.path.join(template_folder, os.path.splitext(app_name)[0] + ".yaml")
        if self.company_global_dir:
            if os.path.exists(self.company_global_dir):
                global_cfg = os.path.join(self.company_global_dir, 'global.yaml')
                if not os.path.exists(global_cfg):
                    self.make_company_global_dir()
            else:
                self.make_company_global_dir()
                global_cfg = os.path.join(self.company_global_dir, 'global.yaml')
        else:
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


def app_config(company=None):
    """
    get the app configuration

    Returns: dict

    """
    return Configuration(company=company).LOADED_CONFIG['app']


def user_config():
    """
    get the location of the user_config()
    :return: string of path
    """
    return Configuration().user_config
