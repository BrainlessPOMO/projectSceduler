from kivy.lang import Builder
from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.config import Config
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu.menu import MDDropdownMenu
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton

from datetime import datetime

from os.path import exists
from os import remove, rename, listdir, makedirs

from shutil import copy2

from dbSetup import get_data, update_item, add_item, delete_item, first_setup, repair_database, backup_database

Builder.load_file('styles.kv')
Config.set('graphics', 'resizable', True)

if not exists("backups"):
    makedirs("backups")

backups = listdir("backups")


def update_backups():
    global backups
    backups = listdir("backups")


def convert_data():
    changed_projects = list()
    for project in project_data:
        current_date = datetime.now().date()

        ending_date = datetime.strptime(project[2], "%Y-%m-%d").date()

        date_diff = ending_date - current_date
        date_diff = date_diff.days
        changed_projects.append(
            (project[0], project[1], date_diff, f"{project[3]}%"))
    return changed_projects


def update_data():
    global project_data
    project_data = get_data()


class ItemInfo(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def on_save(self, instance, value, date_range):
        self.ids.days_tf.text = str(value)

    def on_cancel(self, instance, value):
        pass

    def show_date_dialog(self):
        current_date = datetime.now()
        date_dialog = MDDatePicker(
            year=current_date.year, month=current_date.month, day=current_date.day)
        date_dialog.bind(on_save=self.on_save, on_cansel=self.on_cancel)
        date_dialog.open()


class BottomBar(Snackbar):
    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        Snackbar(
            text=message,
            snackbar_x=0.5,
            snackbar_y="10dp",
            size_hint_x=.5,
            # pos_hint_x=.5,
        ).open()


class TheButtons(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def add(self):
        new_name = self.parent.pickedItem.ids.name_tf.text
        new_date = self.parent.pickedItem.ids.days_tf.text
        new_progress = self.parent.pickedItem.ids.progress_tf.text

        try:
            int(new_progress)
            if not new_name:
                raise Exception('Name must not be empty')
            if not new_date:
                raise Exception('Date must not be empty')
        except ValueError as e:
            BottomBar("Progress must be an integer")
            return
        except Exception as e:
            BottomBar(str(e))
            return

        self.parent.pickedItem.ids.wid_tf.text = ''
        self.parent.pickedItem.ids.name_tf.text = ''
        self.parent.pickedItem.ids.days_tf.text = ''
        self.parent.pickedItem.ids.progress_tf.text = ''

        add_item(new_name, new_date, new_progress)
        self.parent.update_table()

    def update(self):
        old_id = self.parent.pickedItem.ids.wid_tf.text
        new_name = self.parent.pickedItem.ids.name_tf.text
        new_date = self.parent.pickedItem.ids.days_tf.text
        new_progress = self.parent.pickedItem.ids.progress_tf.text

        try:
            int(new_progress)
            int(old_id)
            if not new_date:
                raise ValueError('empty date')
            if not new_name:
                raise ValueError('empty name')
        except ValueError as e:
            BottomBar("Please pick a project from the list to edit")
            return

        self.parent.pickedItem.ids.wid_tf.text = ''
        self.parent.pickedItem.ids.name_tf.text = ''
        self.parent.pickedItem.ids.days_tf.text = ''
        self.parent.pickedItem.ids.progress_tf.text = ''

        update_item(old_id, new_name, new_date, new_progress)
        self.parent.update_table()

    def delete(self):
        old_id = self.parent.pickedItem.ids.wid_tf.text

        try:
            if not old_id:
                raise ValueError('empty date')
        except ValueError as e:
            BottomBar("Please pick a project from the list to delete")
            return

        self.parent.pickedItem.ids.wid_tf.text = ''
        self.parent.pickedItem.ids.name_tf.text = ''
        self.parent.pickedItem.ids.days_tf.text = ''
        self.parent.pickedItem.ids.progress_tf.text = ''

        delete_item(old_id)
        self.parent.update_table()

    def clear(self):
        self.parent.pickedItem.ids.wid_tf.text = ''
        self.parent.pickedItem.ids.name_tf.text = ''
        self.parent.pickedItem.ids.days_tf.text = ''
        self.parent.pickedItem.ids.progress_tf.text = ''


class MainBox(BoxLayout):
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pickedItem = ItemInfo()
        self.add_widget(self.pickedItem)

        self.table = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.8, 0.8),
            column_data=[
                ("ID", dp(10)),
                ("Project Name", dp(60), self.sort_on_name),
                ("Days Left", dp(30), self.sort_on_days_left),
                ("Progress", dp(20))
            ],
            use_pagination=True,
            row_data=convert_data()
        )
        self.table.bind(on_row_press=self.on_row_press)
        self.add_widget(self.table)

        self.buttons = TheButtons()
        self.add_widget(self.buttons)

    def restore(self, instance):
        global backups
        backups = listdir("backups")
        if len(backups) != 0:
            self.parent.parent.current = "restore"
            return

        BottomBar("You have not backup your database at any point!")

    def backup(self, instance):
        print("Backing up")

    # sorting functions
    def sort_on_name(self, data):
        return zip(*sorted(enumerate(data), key=lambda l: l[1][1]))

    def sort_on_days_left(self, data):
        return zip(*sorted(enumerate(data), key=lambda l: l[1][2]))

    # button functions
    def update_table(self):
        update_data()
        self.table.update_row_data(self.table, convert_data())

    def clear(self, instance_button):
        self.pickedItem.ids.wid_tf.text = ''
        self.pickedItem.ids.name_tf.text = ''
        self.pickedItem.ids.days_tf.text = ''
        self.pickedItem.ids.progress_tf.text = ''

    def on_row_press(self, instance_table, instance_row):
        table_range = instance_row.table.recycle_data[instance_row.index]["range"]
        pass_values = []
        for index in range(table_range[0], table_range[1] + 1):
            pass_values.append(instance_row.table.recycle_data[index]["text"])

        pass_values = (
            [item for item in project_data if item[0] == int(pass_values[0])])

        self.pickedItem.ids.wid_tf.text = str(pass_values[0][0])
        self.pickedItem.ids.name_tf.text = str(pass_values[0][1])
        self.pickedItem.ids.days_tf.text = str(pass_values[0][2])
        self.pickedItem.ids.progress_tf.text = str(pass_values[0][3])


class MainScreen(MDBottomNavigationItem):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.box = MainBox()
        self.add_widget(self.box)


class RestoreBox(BoxLayout):
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = "restore"
        self.orientation = 'vertical'
        self.padding = (70, 30)
        self.spacing = 30
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}

    def create_backup(self):
        temp_datetime = datetime.now()
        temp_datetime = f"{temp_datetime.day}-{temp_datetime.month}-{temp_datetime.year}_{temp_datetime.hour}{temp_datetime.minute}{temp_datetime.second}"

        backup_database(f"backups/backup_{temp_datetime}.db")
        BottomBar("Backup file successfully created")
        return

    def create_dropdown_menu(self):
        self.menu_list = list()
        backup_file_list = listdir("backups")

        for backup in backup_file_list:
            self.menu_list.append({
                "viewclass": "OneLineListItem",
                "on_release": lambda x=str(backup): self.on_dropdown_release(x),
                "text": str(backup),
            })

        if len(self.menu_list) == 0:
            self.menu_list.append({
                "viewclass": "OneLineListItem",
                "text": "You have no Backups"
            })

        self.menu = MDDropdownMenu(
            caller=self.ids.file_name,
            items=self.menu_list,
            width_mult=4.5,
            max_height=dp(200)
        )
        self.menu.open()

    def on_dropdown_release(self, backupName):
        self.ids.file_name.text = backupName
        self.menu.dismiss()

    def restore_db(self):
        if self.ids.file_name.text:
            copy2(f'backups/{self.ids.file_name.text}', '.')
            remove('projects.db')
            rename(self.ids.file_name.text, 'projects.db')
            self.ids.file_name.text = ''
            BottomBar("Database successfully restored")

            # update table
            self.parent.parent.parent.first_widget.children[0].update_table()
            return
        BottomBar("You have to pick a backup file from the dropdown")

    def repair_db(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Are you sure?",
                text="This operation will delete all data from the database!",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self.close_alert
                    ),
                    MDRectangleFlatButton(
                        text="YES",
                        on_release=self.repair
                    )
                ]
            )

        self.dialog.open()

    # alert functionality
    def repair(self, instance):
        repair_database()
        self.parent.parent.parent.first_widget.children[0].update_table()
        self.close_alert("")

    def close_alert(self, obj):
        self.dialog.dismiss()
        self.dialog = None


class RestoreScreen(MDBottomNavigationItem):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.restore_box = RestoreBox()
        self.add_widget(self.restore_box)


class ProjectScheduler(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.icon = 'icons/icon2.png'
        self.title = "Project Scheduler"

        bottom_nav = MDBottomNavigation()
        bottom_nav.add_widget(MainScreen(
            name="main",
            icon='projector-screen-outline'
        ))
        bottom_nav.add_widget(RestoreScreen(
            name="restore",
            icon='restore'
        ))

        return bottom_nav


if __name__ == "__main__":
    if not exists("projects.db"):
        first_setup()

    global project_data
    project_data = get_data()

    Window.size = (950, 800)
    ProjectScheduler().run()
