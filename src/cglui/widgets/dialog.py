from Qt import QtCore, QtWidgets, QtGui
import os
import re
import datetime
import getpass
from cglcore.config import app_config, UserConfig
from cglui.widgets.containers.model import ListItemModel
from cglui.widgets.widgets import AdvComboBox, EmptyStateWidget
from cglui.widgets.containers.table import LJTableWidget
from cglui.widgets.containers.menu import LJMenu
from cglui.widgets.base import LJDialog


class FileTableModel(ListItemModel):
    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return self.data_[row][col]


class ItemTable(LJTableWidget):
    delete_item_signal = QtCore.Signal()
    rename_item_signal = QtCore.Signal()
    show_in_folder_signal = QtCore.Signal()

    def __init__(self, parent, title):
        LJTableWidget.__init__(self, parent)
        self.item_right_click_menu = LJMenu(self)
        self.label = title
        self.clicked.connect(self.row_selected)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.item_right_click_menu.create_action("Show in Folder", self.show_in_folder_signal)
        self.customContextMenuRequested.connect(self.item_right_click)

    def item_right_click(self, position):
        self.item_right_click_menu.exec_(self.mapToGlobal(position))


class MagicList(LJDialog):
    """
    Magic List is an incredibly useful dialog that allows you a lot of flexibility when creating custom "list" dialogs
    """
    combo_changed_signal = QtCore.Signal()
    item_selected = QtCore.Signal(object)
    button_name = ''
    button_signal = QtCore.Signal(object)

    def __init__(self, parent=None, title='Dialog Title', list_items=None, buttons=None, message=None,
                 combo_box=None, combo_label='Label', combo=False, button_functions=None, auto_close=True,
                 on_selection=None, on_button_clicked=None):
        """

        :param parent: Parent GUI
        :param title: Title of the Gui
        :param list_items: Items that will go into the table view
        :param buttons: List of buttons that will be created - up to 4 allowed
        :param combo_box: List of items to populate the combo_box
        :param combo_label: Label for the combo_box
        :param combo: If False combo_box is hidden, if True it is displayed
        :param button_functions: Allows for a list of static methods that correspond to the button list
        :param auto_close: Closes the dialog after button is pushed
        """
        LJDialog.__init__(self, parent)
        if list_items is None:
            list_items = []
        if buttons is None:
            buttons = []
        if combo_box is None:
            combo_box = []
        self.auto_close = auto_close
        self.selection = None
        self.setMinimumWidth(600)
        self.list_items = list_items
        self.button_functions = button_functions
        self.user_buttons = buttons
        self.combo_defaults = combo_box
        self.root_path = app_config()['paths']['root']
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.combo_row = QtWidgets.QHBoxLayout(self)
        self.combo_label = QtWidgets.QLabel("<b>%s</b>" % combo_label)
        self.message = QtWidgets.QLabel("\n\n%s\n\n" % message)
        self.combo = AdvComboBox(self)
        self.combo_row.addWidget(self.combo_label)
        self.combo_row.addWidget(self.combo)
        if not combo:
            self.combo_label.hide()
            self.combo.hide()
        self.buttons = QtWidgets.QHBoxLayout(self)
        self.button1 = QtWidgets.QPushButton('Button1')
        self.button2 = QtWidgets.QPushButton('Button2')
        self.button3 = QtWidgets.QPushButton('Button3')
        self.button4 = QtWidgets.QPushButton('Button4')
        button_list = [self.button1, self.button2, self.button3, self.button4]
        for i in range(len(buttons)):
            button_list[i].setText(buttons[i])
            self.buttons.addWidget(button_list[i])

        self.data_table = LJTableWidget(self)
        self.data_table.set_item_model(FileTableModel([], [""]))
        self.data_table.clicked.connect(self.on_selected)

        self.v_layout.addLayout(self.combo_row)
        self.v_layout.addWidget(self.data_table)
        if message:
            self.v_layout.addWidget(self.message)
        self.v_layout.addLayout(self.buttons)

        self.setLayout(self.v_layout)
        self.setWindowTitle(title)
        self.load_combo()
        self.load_items()

        self.combo.currentIndexChanged.connect(self.on_combo_changed)
        self.button1.clicked.connect(self.on_button_clicked)
        self.button2.clicked.connect(self.on_button_clicked)
        self.button3.clicked.connect(self.on_button_clicked)
        self.button4.clicked.connect(self.on_button_clicked)
        if on_button_clicked:
            self.button_signal.connect(on_button_clicked)
        if on_selection:
            self.item_selected.connect(on_selection)

    def on_button_clicked(self):
        if self.button_functions:
            position = self.user_buttons.index(self.sender().text())
            self.button_functions[position]()
        else:
            self.button_name = self.sender().text()
            data = [self.sender(), self.selection]
            self.button_signal.emit(data)
            self.accept()

    def load_combo(self):
        if self.combo_defaults:
            self.combo.addItem('')
            for item in self.combo_defaults:
                self.combo.addItem(item)

    def load_items(self):
        """
        loads items, set up initially to handle a list only.
        :return:
        """
        items = []
        for each in self.list_items:
            items.append([each])
        self.data_table.set_item_model(FileTableModel(items, ['']))

    def on_combo_changed(self):
        self.combo_changed_signal.emit()

    def on_selected(self, data):
        print 'on selected', data
        self.selection = data
        self.item_selected.emit(data)


class FrameRange(LJDialog):
    cancel_signal = QtCore.Signal()
    button = True

    def __init__(self, parent=None, title="Frame Range", sframe=None, eframe=None, camera=None):
        LJDialog.__init__(self, parent)
        layout = QtWidgets.QFormLayout()
        hlayout = QtWidgets.QHBoxLayout()
        blayout = QtWidgets.QHBoxLayout()
        self.sframe = sframe
        self.eframe = eframe
        if camera:
            self.title = '%s for: %s' % (title, camera)
        else:
            self.title = title
        self.sframe_label = QtWidgets.QLabel('Start Frame')
        self.eframe_label = QtWidgets.QLabel('End Frame')
        self.sframe_line_edit = QtWidgets.QLineEdit()
        self.eframe_line_edit = QtWidgets.QLineEdit()
        if sframe:
            print sframe, 'yup'
            self.sframe_line_edit.setText(str(sframe))
        if eframe:
            self.eframe_line_edit.setText(str(eframe))
        hlayout.addWidget(self.sframe_label)
        hlayout.addWidget(self.sframe_line_edit)
        hlayout.addWidget(self.eframe_label)
        hlayout.addWidget(self.eframe_line_edit)
        self.button_cancel = QtWidgets.QPushButton('Cancel')
        self.button = QtWidgets.QPushButton('Confirm Frame Range')
        blayout.addWidget(self.button_cancel)
        blayout.addWidget(self.button)
        layout.addRow(hlayout)
        layout.addRow(blayout)
        self.setLayout(layout)
        self.setWindowTitle(self.title)

        self.button.clicked.connect(self.on_button_clicked)
        self.button_cancel.clicked.connect(self.cancel_clicked)

    def cancel_clicked(self):
        self.button = False
        self.cancel_signal.emit()
        self.accept()

    def on_button_clicked(self):
        self.button = True
        sframe = self.sframe_line_edit.text()
        eframe = self.eframe_line_edit.text()
        if sframe:
            if eframe:
                self.eframe = eframe
                self.sframe = sframe
                self.accept()
            else:
                print 'No end frame defined'
        else:
            print 'No Start Frame Defined'


class InputDialog(LJDialog):
    button_clicked = QtCore.Signal(object)

    def __init__(self, parent=None, title='Title', message="message",
                 buttons=None, line_edit=False, line_edit_text=False, combo_box_items=None,
                 combo_box2_items=None, regex=None, name_example=None):
        """
        Meant to be a catch all dialog for handling just about anything.  It can handle 3 buttons
        :param parent:
        :param message:
        """
        self.original_message = message
        LJDialog.__init__(self, parent)
        if buttons is None:
            buttons = ['Cancel', 'Ok', '']
        layout = QtWidgets.QFormLayout()
        button_box = QtWidgets.QHBoxLayout()
        self.name_example = name_example
        self.regex = regex
        self.values = ''
        self.button = ''
        self.input_text = ''
        self.message = QtWidgets.QLabel(message)
        self.combo_box = AdvComboBox(self)
        self.combo_box2 = AdvComboBox(self)
        self.line_edit = QtWidgets.QLineEdit()
        if line_edit_text:
            self.line_edit.setText(line_edit_text)
        layout.addRow(self.message)
        layout.addRow(self.combo_box)
        self.combo_box.hide()
        layout.addRow(self.combo_box2)
        self.combo_box2.hide()
        if combo_box_items:
            self.combo_box.addItems(combo_box_items)
            self.combo_box.show()
        if combo_box2_items:
            self.combo_box2.addItems(combo_box2_items)
            self.combo_box2.show()
        if line_edit:
            layout.addRow(self.line_edit)
        if buttons:
            i = len(buttons)
            while i < 3:
                buttons.append('')
                i += 1
            self.btn1 = QtWidgets.QPushButton(buttons[0])
            self.btn2 = QtWidgets.QPushButton(buttons[1])
            self.btn3 = QtWidgets.QPushButton(buttons[2])
            button_box.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding,
                                                     QtWidgets.QSizePolicy.Minimum))

            button_box.addWidget(self.btn1)
            if buttons[1]:
                button_box.addWidget(self.btn2)
            if buttons[2]:
                button_box.addWidget(self.btn3)
            layout.addRow(button_box)
        self.setLayout(layout)
        self.setWindowTitle(title)

        self.btn1.clicked.connect(self.on_button_clicked)
        self.btn1.clicked.connect(self.close)
        self.btn2.clicked.connect(self.on_button_clicked)
        self.btn2.clicked.connect(self.close)
        self.btn3.clicked.connect(self.on_button_clicked)
        self.btn3.clicked.connect(self.close)
        if regex:
            self.line_edit.textChanged.connect(self.on_text_changed_regex)
            self.combo_box.textChanged.connect(self.on_text_changed_regex)

    def on_button_clicked(self):
        self.button = self.sender().text()
        self.input_text = self.line_edit.text()

    def on_text_changed_regex(self):
        message = ''
        text = ''
        if self.sender() == self.line_edit:
            text = self.line_edit.text()
        elif self.sender() == self.combo_box:
            text = self.combo_box.currentText()
        if re.match(self.regex, text):
            message = '%s\n%s Passes!' % (self.original_message, text)
            self.btn1.setEnabled(True)
            self.btn2.setEnabled(True)
            self.btn3.setEnabled(True)
        else:
            bad_name = '%s\n%s does not pass' % (self.original_message, text)
            message = '%s\n%s' % (bad_name, self.name_example)
            self.btn1.setEnabled(False)
            self.btn2.setEnabled(False)
            self.btn3.setEnabled(False)
        self.message.setText(message)


class PlaylistDialog(InputDialog):
    def __init__(self, parent=None, project_name=None):
        InputDialog.__init__(self, parent, title='Add To Playlist', message='Choose a day for review',
                             combo_box_items=['Today', 'Tomorrow'])
        self.day = "Today"
        self.project_name = project_name
        self.playlist_name = None
        self.playlist = {}
        self.on_day_chosen()
        self.combo_box.currentIndexChanged.connect(self.on_day_chosen)

    def on_day_chosen(self):
        self.day = self.combo_box.currentText()
        if self.day == 'Today':
            self.playlist_name = '%s_%s' % (self.project_name, datetime.date.today())
        if self.day == 'Tomorrow':
            tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
            self.playlist_name = '%s_%s' % (self.project_name, tomorrow_date)


class LoginDialog(LJDialog):

    def __init__(self, parent=None):
        LJDialog.__init__(self, parent)
        self.user_config = UserConfig().d
        self.user_name = ''
        self.user_email = ''
        self.company = ''
        self.parent = parent
        self.project_management = app_config()['account_info']['project_management']
        grid_layout = QtWidgets.QGridLayout()
        self.proj_management_label = QtWidgets.QLabel('Project Management:')
        self.uname_label = QtWidgets.QLabel('%s User Name:' % self.project_management)
        self.email_label = QtWidgets.QLabel('%s Email:' % self.project_management)
        self.local_user_label = QtWidgets.QLabel('Local User:')

        self.local_user_line_edit = QtWidgets.QLineEdit()
        self.uname_line_edit = QtWidgets.QLineEdit()
        self.email_line_edit = QtWidgets.QLineEdit()
        self.company_line_edit = QtWidgets.QLineEdit()
        self.proj_management_line_edit = QtWidgets.QLineEdit()

        grid_layout.addWidget(self.proj_management_label, 0, 0)
        grid_layout.addWidget(self.proj_management_line_edit, 0, 1)
        grid_layout.addWidget(self.local_user_label, 1, 0)
        grid_layout.addWidget(self.local_user_line_edit, 1, 1)
        grid_layout.addWidget(self.uname_label, 2, 0)
        grid_layout.addWidget(self.uname_line_edit, 2, 1)
        grid_layout.addWidget(self.email_label, 3, 0)
        grid_layout.addWidget(self.email_line_edit, 3, 1)

        buttons_layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton('Ok')
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        buttons_layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding,
                                                     QtWidgets.QSizePolicy.Minimum))
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.ok_button)
        self.ok_button.setEnabled(False)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(grid_layout)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.setWindowTitle('Login Info')
        self.load_user_defaults()

        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.email_line_edit.textChanged.connect(self.on_text_changed)
        self.uname_line_edit.textChanged.connect(self.on_text_changed)
        self.load_user_config()
        self.proj_management_line_edit.setEnabled(False)

    def load_user_config(self):
        self.email_line_edit.setText(self.user_config['proj_man_user_email'])
        self.uname_line_edit.setText(self.user_config['proj_man_user_name'])
        if not self.user_config['user_name']:
            self.local_user_line_edit.setText(getpass.getuser())
        else:
            self.local_user_line_edit.setText(self.user_config['user_name'])
        # TODO it'd be nice to have something here to denote if they're using the local user variable or not.
        self.proj_management_line_edit.setText(self.project_management)
        if self.project_management == 'ftrack':
            self.uname_line_edit.hide()
            self.uname_label.hide()

    def on_text_changed(self):
        email = self.email_line_edit.text()
        if email:
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def on_ok_clicked(self):
        self.save_user_defaults()
        self.accept()

    def on_cancel_clicked(self):
        self.accept()
        print 'Cancel Clicked'

    @staticmethod
    def load_user_defaults():
        print('Adjust Load User Defaults to handle .json')
        if os.path.exists(UserConfig().user_config_path):
            print UserConfig().user_config_path

    def save_user_defaults(self):
        import json
        path_ = UserConfig().user_config_path
        self.user_config['proj_man_user_email'] = self.email_line_edit.text()
        self.user_config['proj_man_user_name'] = self.uname_line_edit.text()
        self.user_config['user_name'] = self.local_user_line_edit.text()
        with open(path_, 'w') as outfile:
            json.dump(self.user_config, outfile, indent=4, sort_keys=True)


class ProjectCreator(LJDialog):
    def __init__(self, parent=None):
        LJDialog.__init__(self, parent)
        self.setMinimumWidth(1000)
        proj_man = app_config()['account_info']['project_management']
        self.project_management = app_config()['project_management'][proj_man]
        self.headers = self.project_management['api']['project_creation_headers']
        self.default_task_type = self.project_management['api']['default_schema']
        self.project_name_regex = app_config()['rules']['path_variables']['project']['regex']
        self.project_name_example = app_config()['rules']['path_variables']['project']['example']
        layout = QtWidgets.QVBoxLayout(self)
        self.model = None
        self.data_frame = None
        self.setWindowTitle('Create Project from .csv')
        self.shots_radio = QtWidgets.QRadioButton('Shots')
        self.shots_radio.setChecked(True)
        self.assets_radio = QtWidgets.QRadioButton('Assets')
        radio_row = QtWidgets.QHBoxLayout()
        radio_row.addWidget(self.shots_radio)
        radio_row.addWidget(self.assets_radio)
        radio_row.addStretch(1)
        self.empty_state = EmptyStateWidget(text='Drag .csv to \nCreate Project', files=True)
        self.task_template_label = QtWidgets.QLabel('Task Template')
        self.task_template_combo = AdvComboBox()
        self.shot_task_label = QtWidgets.QLabel("Valid Shot Tasks:")
        self.shot_task_line_edit = QtWidgets.QLineEdit()
        self.asset_task_label = QtWidgets.QLabel("Valid Asset Tasks:")
        self.asset_task_line_edit = QtWidgets.QLineEdit()
        self.message = QtWidgets.QLabel()
        self.headers_label = QtWidgets.QLabel('Headers:')
        self.headers_line_edit = QtWidgets.QLineEdit()
        self.project_label = QtWidgets.QLabel('Project Name')
        self.project_line_edit = QtWidgets.QLineEdit()
        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.project_label, 0, 0)
        self.grid.addWidget(self.project_line_edit, 0, 1)
        self.grid.addWidget(self.message, 1, 1)
        self.grid.addWidget(self.headers_label, 2, 0)
        self.grid.addWidget(self.headers_line_edit, 2, 1)
        self.grid.addWidget(self.task_template_label, 3, 0)
        self.grid.addWidget(self.task_template_combo, 3, 1)
        self.grid.addWidget(self.shot_task_label, 4, 0)
        self.grid.addWidget(self.shot_task_line_edit, 4, 1)
        self.grid.addWidget(self.asset_task_label, 5, 0)
        self.grid.addWidget(self.asset_task_line_edit, 5, 1)
        self.table = LJTableWidget(self)
        self.table.hide()
        self.create_project_button = QtWidgets.QPushButton('Create Project')
        self.create_row = QtWidgets.QHBoxLayout()
        self.create_row.addStretch(1)
        self.create_row.addWidget(self.create_project_button)

        layout.addLayout(self.grid)
        layout.addLayout(radio_row)
        layout.addWidget(self.empty_state)
        layout.addWidget(self.table)
        layout.addLayout(self.create_row)
        # layout.addStretch(1)
        self.asset_task_line_edit.setEnabled(False)
        self.shot_task_line_edit.setEnabled(False)
        self.headers_line_edit.setEnabled(False)

        self.empty_state.files_added.connect(self.on_csv_dragged)
        self.create_project_button.clicked.connect(self.on_create_project_clicked)
        self.task_template_combo.currentIndexChanged.connect(lambda: self.load_tasks('shots',
                                                                                     self.shot_task_line_edit))
        self.task_template_combo.currentIndexChanged.connect(lambda: self.load_tasks('assets',
                                                                                     self.asset_task_line_edit))
        self.shots_radio.clicked.connect(self.shots_radio_clicked)
        self.assets_radio.clicked.connect(self.assets_radio_clicked)
        self.project_line_edit.textChanged.connect(self.on_project_name_changed)
        self.set_headers_text()
        self.load_task_types()
        self.load_tasks('shots', self.shot_task_line_edit)
        self.load_tasks('assets', self.asset_task_line_edit)
        self.hide_radios()
        self.hide_all()
        self.shots_radio_clicked()
        self.shot_task_label.hide()
        self.shot_task_line_edit.hide()

    def shots_radio_clicked(self):
        self.set_empty_state_label()

    def assets_radio_clicked(self):
        self.set_empty_state_label()

    def set_empty_state_label(self):
        if self.shots_radio.isChecked():
            scope = 'shots'
            self.asset_task_line_edit.hide()
            self.asset_task_label.hide()
            self.shot_task_line_edit.show()
            self.shot_task_label.show()
        else:
            scope = 'assets'
            self.shot_task_line_edit.hide()
            self.shot_task_label.hide()
            self.asset_task_line_edit.show()
            self.asset_task_label.show()
        text = 'Drag .csv to \nCreate %s for %s' % (scope, self.project_line_edit.text())
        self.empty_state.setText(text)

    def on_project_name_changed(self):
        message = ''
        text = self.project_line_edit.text()
        if re.match(self.project_name_regex, text):
            self.set_empty_state_label()
            self.message.hide()
            self.show_all()
            self.empty_state.show()
            self.show_radios()
        else:
            self.message.show()
            message = '%s Does not Pass Naming Convention\n%s' % (text, self.project_name_example)
            self.hide_all()
            self.hide_radios()
        self.message.setText(message)
        # Check to see if it follows naming convention
        # if it does, show the rest of the stuff.

    def show_radios(self):
        self.shots_radio.show()
        self.assets_radio.show()

    def hide_radios(self):
        self.shots_radio.hide()
        self.assets_radio.hide()

    def hide_all(self):
        #self.project_management_line_edit.hide()
        self.task_template_label.hide()
        self.task_template_combo.hide()

        self.headers_label.hide()
        self.headers_line_edit.hide()
        self.empty_state.hide()
        self.create_project_button.hide()

    def show_all(self):
        #self.project_management_line_edit.show()
        self.task_template_label.show()
        self.task_template_combo.show()
        self.headers_label.show()
        self.headers_line_edit.show()
        self.empty_state.show()
        self.create_project_button.show()

    def load_task_types(self):
        for key in self.project_management['tasks']:
            self.task_template_combo.addItem(str(key))
        index = self.task_template_combo.findText(str(self.default_task_type))
        self.task_template_combo.setCurrentIndex(index)

    def load_tasks(self, scope, line_edit):
        tasks_string = ''
        schema = self.project_management['tasks'][self.task_template_combo.currentText()]
        if scope in schema['long_to_short']:
            for key in schema['long_to_short'][scope]:
                if tasks_string == '':
                    tasks_string = key.lower
                else:
                    tasks_string = '%s, %s' % (tasks_string, key.lower())
        line_edit.setText(tasks_string)

    def set_headers_text(self):
        text = ''
        last = self.headers[-1]
        for each in self.headers:
            if each != last:
                text += each + ', '
            else:
                text += each
        self.headers_line_edit.setText(text)

    def on_csv_dragged(self, data):
        if len(data) > 0:
            print 'I can only handle one file at a time'
        if data[0].endswith('.csv'):
            print 'Reading .csv file: %s' % data[0]
            self.read_file(data[0])
            self.empty_state.hide()
            self.table.show()
        else:
            print 'Only .csv files supported'

    def read_file(self, filepath):
        import pandas as pd
        from cglui.widgets.containers.model import PandasModel
        df = pd.read_csv(filepath)
        df.columns = [x.lower() for x in df.columns]
        df = self.parse_tasks(df)
        drop_these = []
        for c in df.columns:
            if c.lower() not in self.headers and c.lower() != '':
                drop_these.append(c)
        df = df[df.columns.drop(list(drop_these))]
        self.clean_nan(df)
        df = df.sort_values(by=['shot', 'ftrack_task'])
        # if doesn't match one of the headers remove the column of the data frame
        self.model = PandasModel(df)
        self.table.setModel(self.model)
        print self.set_shots_as_bold()
        # self.table.setSortingEnabled(True)
        # self.table.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def set_shots_as_bold(self):
        row = self.model.rowCount()
        for c in xrange(0, self.model.columnCount()):
            index_ = self.model.index(c, 3)
            if not self.model.data(index_):
                # TODO - i'm actually getting to the right place here, just have no idea how to change the text.
                # C is the row i want though - now i just need to "bold" the text on all these items.
                ni = self.model.index(c, 0)
                self.model.setData(ni, QtGui.QBrush(QtCore.Qt.red), QtCore.Qt.BackgroundRole)

    def parse_tasks(self, df):
        rows_to_drop = []
        tasks = self.shot_task_line_edit.text().split(', ')
        for c in df.columns:
            if c.lower() not in tasks:
                pass
            else:
                # For each row in the column:
                for index, row in df.iterrows():
                    if row[c] and str(row[c]) != 'nan':
                        df = df.append({'shot': row['shot'], 'ftrack_task': c, 'duration': row[c],
                                        'description': row['description']}, ignore_index=True)
        # for r in rows_to_drop:
        #     df.drop(r)
        return df

    @staticmethod
    def clean_nan(df):
        for index, row in df.iterrows():
            if str(row['ftrack_task']).lower() == 'nan':
                df.at[index, 'ftrack_task'] = ''
            if str(row['duration']).lower() == 'nan':
                df.at[index, 'duration'] = 0

    def on_create_project_clicked(self):
        for irow in xrange(self.model.rowCount()):
            row = []
            for icol in xrange(self.model.columnCount()):
                cell = self.model.data(self.model.createIndex(irow, icol))
                row.append(cell)
            i = -1
            for h in self.headers:
                print '%s: %s'
                row_string = '%s, %s' % (row_string, h)
            print row_string





