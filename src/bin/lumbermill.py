from Qt import QtWidgets
import core.startup


def load_lumbermill(app, splash=None):
    from apps.lumbermill.main import CGLumberjack
    import time
    start_time = time.time()
    print 'Loading Lumbermill'
    QtWidgets.qApp.processEvents()
    gui = CGLumberjack(show_import=False, user_info=user_info, start_time=start_time)
    gui.show()
    gui.raise_()
    if splash:
        splash.finish(gui)
    app.exec_()


if __name__ == "__main__":
    app, splash = core.startup.app_init()
    project_management, user_info = core.startup.user_init()
    project_management = 'lumbermill'
    if user_info:
        print 'Found User, %s' % user_info['login']
        if core.startup.check_time_log(project_management):
            load_lumbermill(app, splash)
        else:
            from src.bin.time_sheet import load_time_sheet
            load_time_sheet(app)
    else:
        from src.bin.login_dialog import load_login_dialog
        load_login_dialog(app)

