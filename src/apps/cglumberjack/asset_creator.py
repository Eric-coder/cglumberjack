import re
import os
import glob
from core.path import CreateProductionData, PathObject
from Qt import QtWidgets, QtCore, QtGui

from core.config import app_config
from cglui.widgets.base import LJDialog
from cglui.widgets.combo import AdvComboBox, LabelComboRow


class AssetWidget(QtWidgets.QWidget):
    button_clicked = QtCore.Signal(object)
    filter_changed = QtCore.Signal()

    def __init__(self, parent, title, scope):
        QtWidgets.QWidget.__init__(self, parent)
        v_layout = QtWidgets.QVBoxLayout(self)
        h_layout = QtWidgets.QHBoxLayout(self)
        if scope == 'assets':
            self.category_row = LabelComboRow('%s Category' % scope.title(), button=False, bold=False)
            self.name_row = LabelComboRow('%s Name(s)' % scope.title(), button=False, bold=False)
        if scope == 'shots':
            self.category_row = LabelComboRow('Sequence', button=False, bold=False)
            self.name_row = LabelComboRow('Shot Name(s)', button=False, bold=False)
        self.label = title
        self.project_label = QtWidgets.QLabel("<b>Create %s For: %s</b>" % (scope.title(), title))
        self.message = QtWidgets.QLabel("")

        h_layout.addWidget(self.project_label)
        h_layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding,
                                               QtWidgets.QSizePolicy.Minimum))

        v_layout.addLayout(h_layout)
        v_layout.addItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Minimum,
                                               QtWidgets.QSizePolicy.Minimum))
        v_layout.addLayout(self.category_row)
        v_layout.addLayout(self.name_row)
        v_layout.addWidget(self.message)

        self.message.hide()

    def set_title(self, new_title):
        self.title.setText('<b>%s</b>' % new_title.title())


class AssetCreator(LJDialog):
    def __init__(self, parent=None, path_dict=None):
        LJDialog.__init__(self, parent)
        self.resize(300, 60)
        self.red_palette = QtGui.QPalette()
        self.red_palette.setColor(self.foregroundRole(), QtGui.QColor(255, 0, 0))
        self.green_palette = QtGui.QPalette()
        self.green_palette.setColor(self.foregroundRole(), QtGui.QColor(0, 255, 0))
        self.black_palette = QtGui.QPalette()
        self.black_palette.setColor(self.foregroundRole(), QtGui.QColor(0, 0, 0))
        if not path_dict:
            return
        self.path_object = PathObject(path_dict)
        self.scope = self.path_object.scope
        self.setWindowTitle('Create %s' % self.scope.title())
        self.asset = None
        self.asset_message_string = ''
        self.asset_list = []
        self.full_root = None
        self.regex = ''
        self.valid_categories_string = ''
        self.seq = None
        self.valid_categories = []
        self.get_valid_categories()
        # Environment Stuff
        self.root = app_config()['paths']['root']
        self.project_management = app_config()['account_info']['project_management']
        if self.scope == 'assets':
            self.asset_string_example = app_config()['rules']['path_variables']['asset']['example']
        elif self.scope == 'shots':
            self.asset_string_example = app_config()['rules']['path_variables']['shotname']['example']
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.scope_row = QtWidgets.QHBoxLayout()
        self.asset_row = QtWidgets.QHBoxLayout(self)
        self.tasks = []
        self.task_row = QtWidgets.QHBoxLayout(self)
        self.task_combo = AdvComboBox()
        self.create_button = QtWidgets.QPushButton('Create %s' % self.scope.title())
        self.create_button.setEnabled(False)

        # asset & shot stuff
        self.asset_widget = AssetWidget(self, scope=self.scope, title=str(self.path_object.project))
        self.asset_widget.name_row.combo.setEnabled(False)
        self.asset_row.addWidget(self.asset_widget)
        # task stuff
        self.task_layout = QtWidgets.QVBoxLayout(self)
        for each in app_config()['pipeline_steps'][self.scope]:
            defaults = app_config()['pipeline_steps'][self.scope]['default_steps']
            if each == 'default_steps':
                pass
            else:
                checkbox = QtWidgets.QCheckBox('%s (%s)' % (each, app_config()['pipeline_steps'][self.scope][each]))
                checkbox.stateChanged.connect(self.on_checkbox_clicked)
                self.task_layout.addWidget(checkbox)
                if app_config()['pipeline_steps'][self.scope][each] in defaults:
                    print each
                    checkbox.setCheckState(QtCore.Qt.Checked)

        self.v_layout.addLayout(self.asset_row)
        self.v_layout.addLayout(self.task_layout)
        self.v_layout.addWidget(self.create_button)
        self.v_layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum,
                                                    QtWidgets.QSizePolicy.Expanding))
        self.asset_widget.message.hide()
        self.load_categories()
        self.asset_widget.category_row.combo.currentIndexChanged.connect(self.on_category_selected)
        self.asset_widget.name_row.combo.editTextChanged.connect(self.process_asset_string)
        self.create_button.clicked.connect(self.on_create_clicked)
        if self.scope == 'shots':
            self.asset_widget.category_row.combo.editTextChanged.connect(self.on_seq_text_changed)
        self.hide_layout_items(self.task_layout)

    def on_checkbox_clicked(self):
        self.find_all_checked_boxes()

    def find_all_checked_boxes(self):
        self.tasks = []
        for i in range(self.task_layout.count()):
            child = self.task_layout.itemAt(i)
            if child.widget().checkState() == QtCore.Qt.Checked:
                self.tasks.append(child.widget().text().split('(')[-1].replace(')', ''))
        print self.tasks

    @staticmethod
    def hide_layout_items(layout):
        for i in range(layout.count()):
            child = layout.itemAt(i).widget()
            child.hide()

    @staticmethod
    def show_layout_items(layout):
        for i in range(layout.count()):
            child = layout.itemAt(i).widget()
            child.show()

    def on_category_selected(self):
        self.path_object.new_set_attr(seq=self.asset_widget.category_row.combo.currentText())
        self.asset_widget.name_row.combo.setEnabled(True)
        self.load_assets()

    def on_seq_text_changed(self):
        self.seq = self.asset_widget.category_row.combo.currentText()
        print app_config()['rules']['path_variables']['seq']['regex']
        seq_rules = app_config()['rules']['path_variables']['seq']['regex']
        example = app_config()['rules']['path_variables']['seq']['example']
        self.regex = re.compile(r'%s' % seq_rules)
        if re.match(self.regex, self.seq):
            self.asset_widget.name_row.combo.setEnabled(True)
            self.asset_widget.message.hide()
        else:
            self.asset_message_string = '%s is not a valid sequence name\n%s' % (self.seq, example)
            self.asset_widget.message.setText(self.asset_message_string)
            self.asset_widget.message.setPalette(self.red_palette)
            self.asset_widget.message.show()

    def load_categories(self):
        categories = app_config()['asset_categories']
        cats = ['']
        for c in categories:
            cats.append(categories[c])
        self.asset_widget.category_row.combo.addItems(cats)

    def process_asset_string(self):
        self.seq = self.asset_widget.category_row.combo.currentText()
        asset_string = self.asset_widget.name_row.combo.currentText()
        if self.scope == 'assets':
            asset_rules = r'^([a-zA-Z]{3,},\s*)*([a-zA-Z]{3,}$)|^([a-zA-Z]{3,},\s*)*([a-zA-Z]{3,}$)'
            example = app_config()['rules']['path_variables']['shot']['regex']
        if self.scope == 'shots':
            asset_rules = app_config()['rules']['path_variables']['shot']['regex']
        self.regex = re.compile(r'%s' % asset_rules)
        if re.match(self.regex, asset_string):
            self.asset_message_string = '%s is a valid %s name' % (asset_string, self.scope)
            self.asset_widget.message.setPalette(self.black_palette)
            self.asset_widget.message.setText(self.asset_message_string)
            self.asset_widget.message.hide()
            self.show_layout_items(self.task_layout)
            self.create_button.setEnabled(True)
            if asset_string in self.asset_list:
                self.asset_message_string = '%s already Exists!' % asset_string
                self.asset_widget.message.setText(self.asset_message_string)
                self.asset_widget.message.setPalette(self.red_palette)
                self.asset_widget.message.show()
                self.hide_layout_items(self.task_layout)
                self.create_button.setEnabled(False)
        else:
            self.asset_message_string = '%s is not a valid %s name\n%s' % (asset_string, self.scope,
                                                                           self.asset_string_example)
            self.asset_widget.message.setText(self.asset_message_string)
            self.asset_widget.message.setPalette(self.red_palette)
            if asset_string == '':
                self.asset_widget.message.hide()
            else:
                self.asset_widget.message.show()
            self.hide_layout_items(self.task_layout)
            self.create_button.setEnabled(False)

    def process_asset_string_old(self, asset_string):
        # TODO - add something here that also filters by the argument(s) given.
        asset_rules = r'^[a-zA-Z]{3,}:([a-zA-Z]{3,},\s*)*([a-zA-Z]{3,}$)|^([a-zA-Z]{3,},\s*)*([a-zA-Z]{3,}$)'
        self.regex = re.compile(r'%s' % asset_rules)
        if re.match(self.regex, asset_string):
            print '%s matches regex' % asset_string
            # if it has a :
            if ':' in asset_string:
                print 'found :'
                self.seq, asset_string = asset_string.split(':')
                # if it's a bunch of assets comma separated
                if ',' in asset_string:
                    self.asset_list = self.remove_spaces_on_list(asset_string.split(','))
                    if self.seq in self.valid_categories:
                        if self.asset_list:
                            self.asset_message_string = 'Click Enter to Create:'
                            for i, _ in enumerate(self.asset_list):
                                name = '%s:%s' % (self.seq, self.asset_list[i])
                                self.asset_list[i] = name
                                self.asset_message_string = '%s\n%s' % (self.asset_message_string, name)
                    else:
                        self.asset_message_string = '%s Not Valid Category! Try: %s' % (self.seq,
                                                                                        self.valid_categories_string)
                else:
                    self.asset_message_string = 'Click Enter to Create: \n%s:%s' % (self.seq, asset_string)
            elif ',' in asset_string:
                print 'asset_string:', asset_string
                self.asset_list = self.remove_spaces_on_list(asset_string.split(','))
                if self.asset_list:
                    self.asset_message_string = 'Click Enter to Create:'
                    for i, _ in enumerate(self.asset_list):
                        name = '%s:%s' % ('Prop', self.asset_list[i])
                        self.asset_list[i] = name
                        self.asset_message_string = '%s\n%s' % (self.asset_message_string, name)
            else:
                self.asset_list = []
                if not self.seq:
                    self.seq = 'Prop'
                self.asset_list.append('%s:%s' % (self.seq, asset_string))
                self.asset_message_string = 'Click Enter to Create: \n%s' % self.asset_list[0]

        else:
            print '%s does not match regex' % asset_string
            self.asset_message_string = '%s does not pass naming convention\n%s' % (asset_string,
                                                                                    self.asset_string_example)

    def get_valid_categories(self):
        categories = app_config()['asset_categories']
        for each in categories:
            self.valid_categories.append(each)
            self.valid_categories_string = '%s, %s' % (self.valid_categories_string, each)

    @staticmethod
    def remove_spaces_on_list(list_):
        new_list = []
        for each in list_:
            new_list.append(each.replace(' ', ''))
        return new_list

    def load_assets(self):
        self.asset_widget.name_row.combo.clear()
        glob_path = self.path_object.path_root
        glob_path = re.sub('/+$', '', glob_path)
        print glob_path
        list_ = glob.glob(glob_path)
        assets = ['']
        for each in list_:
            assets.append(os.path.split(each)[-1])
        self.asset_list = assets
        self.asset_widget.name_row.combo.addItems(assets)

    def load_tasks(self):
        task_list = app_config()['pipeline_steps'][self.scope.lower()]
        tasks = ['']
        for each in task_list:
            tasks.append(each)
        print tasks
        print "I'm meant to load tasks in some kind of gui: %s" % tasks

    @staticmethod
    def is_valid_asset():
        pass

    @staticmethod
    def is_valid_shot():
        pass

    def on_create_clicked(self):
        for each in self.tasks:
            if self.scope == 'assets':
                self.path_object.new_set_attr(asset=self.asset_widget.name_row.combo.currentText())
                self.path_object.new_set_attr(type=self.seq)
            elif self.scope == 'shots':
                self.path_object.new_set_attr(shot=self.asset_widget.name_row.combo.currentText())
                self.path_object.new_set_attr(seq=self.seq)
            self.path_object.new_set_attr(task=each)
            print 'Current Path With Root: %s' % self.path_object.path_root
            # CreateProductionData(self.path_object.data, project_management=self.project_management)


if __name__ == "__main__":
    from cglui.startup import do_gui_init

    app = do_gui_init()
    td = AssetCreator()
    td.setWindowTitle('Project Builder')
    td.show()
    td.raise_()
    app.exec_()

