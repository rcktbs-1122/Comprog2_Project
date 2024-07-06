from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivymd.app import MDApp
from datetime import datetime
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from database import Database

db = Database()

class DialogContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_text.text = str(datetime.now().strftime('%A %d %B %Y'))
        self.ids.time_text.text = ''
        self.save_button = self.ids.save_button
        self.check_fields()

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save_date)
        date_dialog.open()

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_save_time)
        time_dialog.open()

    def on_save_date(self, instance, value, date):
        self.ids.date_text.text = value.strftime('%A %d %B %Y')

    def on_save_time(self, instance, value):
        self.ids.time_text.text = value.strftime('%I:%M %p')

    def check_fields(self):
        if self.ids.task_text.text.strip() and self.ids.date_text.text.strip() and self.ids.time_text.text.strip():
            self.save_button.disabled = False
        else:
            self.save_button.disabled = True


class ListItemWithCheckbox(TwoLineAvatarIconListItem):

    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        self.pk = pk

    def mark(self, check, the_list_item):
        if check.active == True:
            the_list_item.text = '[s]' + the_list_item.text + '[/s]'
            db.mark_task_as_complete(the_list_item.pk)
        else:
            the_list_item.text = str(db.mark_task_as_incomplete(the_list_item.pk))

    def delete_item(self, the_list_item):
        self.parent.remove_widget(the_list_item)
        db.delete_task(the_list_item.pk)


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    pass

class MainApp(MDApp):
    task_list_dialog = None

    def build(self):
        self.theme_cls.primary_palette = 'Brown'
        self.theme_cls.theme_style = 'Light'


    def show_task_dialog(self):
        if not self.task_list_dialog:
            self.task_list_dialog = MDDialog(
                title="Create Task",
                type="custom",
                size_hint=(0.8, 0.8),
                background_color=(0.6, 0.4, 0.2, 1),
                md_bg_color=(0.6, 0.4, 0.2, 1),
                content_cls=DialogContent(),
            )
        self.task_list_dialog.open()

    def on_start(self):
        try:
            self.load_tasks()
        except Exception as e:
            print(e)

    def load_tasks(self, sort_option='task'):
        self.root.ids.container.clear_widgets()
        incompleted_tasks, completed_tasks = db.get_tasks(sort_option)

        if incompleted_tasks:
            for task in incompleted_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text=str(task[1]), secondary_text=task[2])
                self.root.ids.container.add_widget(add_task)

        if completed_tasks:
            for task in completed_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text='[s]' + str(task[1]) + '[/s]', secondary_text=task[2])
                add_task.ids.check.active = True
                self.root.ids.container.add_widget(add_task)

    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()

    def add_task(self, task, task_datetime):
        created_task = db.create_task(task.text, task_datetime)

        self.root.ids.container.add_widget(
            ListItemWithCheckbox(pk=created_task[0], text='[b]' + str(created_task[1]) + '[/b]',
                                 secondary_text=created_task[2]))
        task.text = ''

    def sort_tasks(self, sort_option):
        self.load_tasks(sort_option)

    def sort_alphabetically(self):
        self.sort_tasks('task')

    def sort_by_due_date(self):
        self.sort_tasks('due_date')

class MainScreen(Screen):
    pass

class StartupScreen(Screen):
    pass

class MainApp(MDApp):
    task_list_dialog = None

    def build(self):
        self.theme_cls.primary_palette = 'Brown'
        self.theme_cls.theme_style = 'Light'

        self.sm = ScreenManager()
        self.startup_screen = StartupScreen(name='startup')
        self.main_screen = MainScreen(name='main')

        self.sm.add_widget(self.startup_screen)
        self.sm.add_widget(self.main_screen)

        return self.sm

    def show_task_dialog(self):
        if not self.task_list_dialog:
            self.task_list_dialog = MDDialog(
                title="Create Task",
                type="custom",
                size_hint=(0.8, 0.8),
                background_color=(0.6, 0.4, 0.2, 1),
                md_bg_color=(0.6, 0.4, 0.2, 1),
                content_cls=DialogContent(),
            )
        self.task_list_dialog.open()

    def on_start(self):
        self.sm.current = 'startup'
    def load_tasks(self, sort_option='task'):
        self.main_screen.ids.container.clear_widgets()
        incompleted_tasks, completed_tasks = db.get_tasks(sort_option)

        if incompleted_tasks:
            for task in incompleted_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text=str(task[1]), secondary_text=task[2])
                self.main_screen.ids.container.add_widget(add_task)

        if completed_tasks:
            for task in completed_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], text='[s]' + str(task[1]) + '[/s]', secondary_text=task[2])
                add_task.ids.check.active = True
                self.main_screen.ids.container.add_widget(add_task)

    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()

    def add_task(self, task, task_datetime):
        created_task = db.create_task(task.text, task_datetime)

        self.main_screen.ids.container.add_widget(
            ListItemWithCheckbox(pk=created_task[0], text='[b]' + str(created_task[1]) + '[/b]',
                                 secondary_text=created_task[2]))
        task.text = ''

    def sort_tasks(self, sort_option):
        self.load_tasks(sort_option)

    def sort_alphabetically(self):
        self.sort_tasks('task')

    def sort_by_due_date(self):
        self.sort_tasks('due_date')

    def return_to_startup(self):
        self.sm.current = 'startup'

if __name__ == '__main__':
    MainApp().run()
