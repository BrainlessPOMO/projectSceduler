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
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from kivymd.icon_definitions import md_icons

from datetime import datetime

from os.path import exists
from dbSetup import get_data, update_item, add_item, delete_item, create_tables

Builder.load_file('styles.kv')
Config.set('graphics', 'resizable', True)


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


class TheButtons(BoxLayout):
    dialog = None

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
                raise ValueError('empty string')
            if not new_date:
                raise ValueError('empty date')
        except ValueError as e:
            if not self.dialog:
                self.dialog = MDDialog(
                    title="Operation Failed",
                    text="Progress must be an integer\nName and date must not be empty",
                    buttons=[MDFlatButton(
                        text="OK", on_release=self.close_alert)
                    ]
                )

            self.dialog.open()
            return

        self.parent.pickedItem.ids.wid_tf.text = ''
        self.parent.pickedItem.ids.name_tf.text = ''
        self.parent.pickedItem.ids.days_tf.text = ''
        self.parent.pickedItem.ids.progress_tf.text = ''

        add_item(new_name, new_date, new_progress)
        update_data()
        self.parent.update_table()

    def close_alert(self, obj):
        self.dialog.dismiss()
        self.dialog = None

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
            if not self.dialog:
                self.dialog = MDDialog(
                    title="Operation Failed",
                    text="Please pick a project from the list to edit",
                    buttons=[MDFlatButton(
                        text="OK", on_release=self.close_alert)
                    ]
                )

            self.dialog.open()
            return

        self.parent.pickedItem.ids.wid_tf.text = ''
        self.parent.pickedItem.ids.name_tf.text = ''
        self.parent.pickedItem.ids.days_tf.text = ''
        self.parent.pickedItem.ids.progress_tf.text = ''

        update_item(old_id, new_name, new_date, new_progress)
        update_data()
        self.parent.update_table()

    def delete(self):
        old_id = self.parent.pickedItem.ids.wid_tf.text

        try:
            if not old_id:
                raise ValueError('empty date')
        except ValueError as e:
            if not self.dialog:
                self.dialog = MDDialog(
                    title="Operation Failed",
                    text="Please pick a project from the list to delete",
                    buttons=[MDFlatButton(
                        text="OK", on_release=self.close_alert)
                    ]
                )

            self.dialog.open()
            return

        self.parent.pickedItem.ids.wid_tf.text = ''
        self.parent.pickedItem.ids.name_tf.text = ''
        self.parent.pickedItem.ids.days_tf.text = ''
        self.parent.pickedItem.ids.progress_tf.text = ''

        delete_item(old_id)
        update_data()
        self.parent.update_table()

    def clear(self):
        self.parent.pickedItem.ids.wid_tf.text = ''
        self.parent.pickedItem.ids.name_tf.text = ''
        self.parent.pickedItem.ids.days_tf.text = ''
        self.parent.pickedItem.ids.progress_tf.text = ''


class MainBox(BoxLayout):
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
                ("Days Left", dp(20), self.sort_on_days_left),
                ("Progress", dp(20))
            ],
            use_pagination=True,
            row_data=convert_data()
        )
        self.table.bind(on_row_press=self.on_row_press)
        self.add_widget(self.table)

        self.buttons = TheButtons()
        self.add_widget(self.buttons)

        self.speed_dial = MDFloatingActionButtonSpeedDial(
            id="speed_dial",
            data={'Repair Database': [
                'car-wrench', "on_release", self.callback]},
            root_button_anim=True,
            size_hint=(None, None),
            size=(0, 0)
        )
        self.add_widget(self.speed_dial)

    # dial menu functionality
    def callback(self, instance):
        # TODO: repair database functionality
        print("in callback")

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


class ProjectScheduler(MDApp):
    def build(self):
        box = MainBox()
        self.theme_cls.theme_style = "Light"
        self.icon = 'icons/icon2.png'
        self.title = "Project Scheduler"
        return box


if __name__ == "__main__":
    if not exists("projects.db"):
        create_tables()

    global project_data
    project_data = get_data()

    Window.size = (850, 800)
    ProjectScheduler().run()
