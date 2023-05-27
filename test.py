from kivy.lang import Builder
from kivy.properties import DictProperty

from kivymd.app import MDApp

KV = '''
MDScreen:

    MDFloatingActionButtonSpeedDial:
        id: speed_dial
        data: app.data
        root_button_anim: True
        hint_animation: True
'''


class Example(MDApp):
    data = DictProperty()

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.data = {
            'Python': 'language-python',
            'JS': [
                'language-javascript',
                "on_press", lambda x: print("pressed JS"),
                "on_release", lambda x: print(
                    "stack_buttons",
                    self.root.ids.speed_dial.stack_buttons
                )
            ],
            'PHP': [
                'language-php',
                "on_press", lambda x: print("pressed PHP"),
                "on_release", self.callback
            ],
            'C++': [
                'language-cpp',
                "on_press", lambda x: print("pressed C++"),
                "on_release", lambda x: self.callback()
            ],
        }
        return Builder.load_string(KV)

    def callback(self, *args):
        print(args)


Example().run()
