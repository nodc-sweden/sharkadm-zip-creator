import pathlib
import textwrap

import flet as ft

from sharkadm_zip_creator.flet_app import utils


class Operator(ft.Card):
    def __init__(self, parent, operator: dict):
        super().__init__()
        self.parent_control = parent
        self.expand = True
        self.name = operator['name']

        self.operator = {}

        name = operator['name']
        self._main_cb = ft.Checkbox(name, on_change=self._on_change_main)
        if operator.get('active', True):
            self._main_cb.value = True
        self.operator['active'] = self._main_cb

        self._children_col = ft.Column()
        for key, value in operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
                wid.value = value
            else:
                wid = ft.Text(key)
            self.operator[key] = wid
            self._children_col.controls.append(wid)

        self.content = ft.Container(
            content=ft.Row(
                [
                    self._main_cb,
                    self._children_col
                ]
            ),
            width=400,
            padding=10,
        )

    def _on_change_main(self, e):
        self._children_col.disabled = True
        if self._main_cb.value:
            self._children_col.disabled = False
        self._children_col.update()

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator.items():
            info[key] = wid.value
        return info


class PostOperator(ft.Card):
    def __init__(self, parent, operator: dict):
        super().__init__()
        self.parent_control = parent
        self.expand = True
        self.name = operator['name']

        self.operator = {}

        name = operator['name']
        self._main_cb = ft.ElevatedButton(name, on_click=self._on_click_main)

        self._children_col = ft.Column()
        for key, value in operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
                wid.value = value
            else:
                wid = ft.Text(key)
            self.operator[key] = wid
            self._children_col.controls.append(wid)

        self.content = ft.Container(
            content=ft.Row(
                [
                    self._main_cb,
                    self._children_col
                ]
            ),
            width=400,
            padding=10,
        )

    def _on_click_main(self, e):
        info = self.get_info()
        info['name'] = self.name
        self.parent_control.run_exporter(**info)

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator.items():
            info[key] = wid.value
        return info





















class _Operator(ft.Row):
    def __init__(self, main_app, operator: dict):
        super().__init__()
        self.main_app = main_app
        self.expand = True
        self.name = operator['name']

        self.operator = {}

        name = operator['name']
        cb = ft.Checkbox(name)
        if operator.get('active', True):
            cb.value = True
        self.operator['active'] = cb

        col = ft.Column()
        for key, value in operator.items():
            if key in ['name', 'active']:
                continue
            if type(value) is bool:
                wid = ft.Checkbox(key)
            else:
                wid = ft.Text(key)
            self.operator[key] = wid
            col.controls.append(wid)

        self.controls = [
            cb,
            col
        ]

    def get_info(self) -> dict:
        info = dict(name=self.name)
        for key, wid in self.operator.items():
            info[key] = wid.value
        return info


class old_Operation(ft.UserControl):
    def __init__(self, **kwargs):
        super().__init__()
        self._data = kwargs
        print(f'{self._data=}')
        self._settings_controls = {}

        self._description_wrap_length = 80

        self._main_active_bgcolor = ft.colors.GREEN_50
        self._switch_active_bgcolor = ft.colors.GREEN_100
        self._text_active_bgcolor = ft.colors.GREEN_200

        self._main_inactive_bgcolor = ft.colors.GREY_200
        self._switch_inactive_bgcolor = ft.colors.GREY_200
        self._text_inactive_bgcolor = ft.colors.GREY_300

        self._main_padding = 5
        self._main_border_radius = 10

        self._child_padding = 5
        self._child_border_radius = 10

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def description(self) -> str:
        return textwrap.fill(self._data.get('description') or '', self._description_wrap_length)

    @property
    def settings(self) -> dict:
        data = self._data.get('kwargs', {})
        for key, control in self._settings_controls.items():
            value = control.value
            if type(value) == pathlib.Path:
                value = str(value)
            data[key] = value
        return data

    @property
    def state(self) -> bool:
        return self._switch.value

    @state.setter
    def state(self, st) -> None:
        assert type(st) == bool
        self._switch.value = st
        self._on_change()

    def _on_change(self, e: ft.ControlEvent | None = None):
        if self._switch.value:
            self._on_select()
        else:
            self._on_deselect()
        self.update()

    def _on_select(self):
        self._main_container.bgcolor = self._main_active_bgcolor
        self._switch_container.bgcolor = self._switch_active_bgcolor
        self._text_container.bgcolor = self._text_active_bgcolor

    def _on_deselect(self):
        self._main_container.bgcolor = self._main_inactive_bgcolor
        self._switch_container.bgcolor = self._switch_inactive_bgcolor
        self._text_container.bgcolor = self._text_inactive_bgcolor

    def build(self):
        self._create_controls()
        return self._get_layout()

    def _create_controls(self):
        self._create_settings_dialog()

        self._main_container = ft.Container(
            bgcolor=self._main_inactive_bgcolor,
            padding=self._main_padding,
            border_radius=self._main_border_radius
        )
        self._switch_container = ft.Container(
            bgcolor=self._switch_inactive_bgcolor,
            padding=self._child_padding,
            border_radius=self._child_border_radius
        )
        self._text_container = ft.Container(
            bgcolor=self._text_inactive_bgcolor,
            padding=self._child_padding,
            border_radius=self._child_border_radius
        )
        self._switch = ft.Switch(label=self.name, on_change=self._on_change)
        self._text = ft.Text(self.description, expand=True)

        self._settings_icon_button = ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    on_click=self._open_settings,
                    # icon_color="blue400",
                    icon_size=20,
                    tooltip="Inställningar", visible=False)
        if self.settings:
            self._settings_icon_button.visible = True

        self._child_row = ft.Row()

    def _create_settings_dialog(self):
        self._settings_content = ft.Row()
        self._settings_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Inställningar"),
                content=self._settings_content,
                actions=[
                    ft.TextButton("OK", on_click=self._close_settings),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: print("Modal dialog dismissed!"),
            )

    def _get_layout(self):
        """Creates the layout and returns the root widget"""

        # self.expand = True
        # self._main_container.expand = True
        # self._child_row.expand = True
        # self._switch_container.expand = True
        # self._text_container.expand = True
        # self._switch.expand = True
        # self._text.expand = True

        self._child_row.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

        row = ft.Row([self._switch, self._settings_icon_button])
        self._switch_container.content = row
        self._text_container.content = self._text

        self._child_row.controls.append(self._switch_container)
        self._child_row.controls.append(self._text_container)

        self._main_container.content = self._child_row
        return self._main_container

    def _open_settings(self, *args):
        self.page.dialog = self._settings_dialog
        self._settings_dialog.open = True
        self.page.update()
        self._update_settings_content(**self.settings)

    def _close_settings(self, *args):
        self._settings_dialog.open = False
        self._settings_dialog.update()

    def _on_pick_directory(self, e: ft.FilePickerResultEvent, linked_control: ft.Text):
        if not e.path:
            return
        linked_control.value = e.path
        linked_control.update()

    def _update_settings_content(self, **kwargs):
        self._settings_content.controls = []
        self._settings_controls = {}
        # column = ft.Column(width=430)
        column = ft.Column(expand=True)
        self._settings_content.controls.append(column)
        for key, value in kwargs.items():
            if key == 'export_directory':
                self._settings_controls[key] = ft.Text()
                pick_file_path = ft.FilePicker(on_result=lambda e, p=self._settings_controls[key]: self._on_pick_directory(e, p))
                self.page.overlay.append(pick_file_path)
                self.page.update()
                button = ft.ElevatedButton(
                            "Välj en mapp att exportera till",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda _: pick_file_path.get_directory_path(
                            ),
                        )

                row = ft.Row([
                    button,
                    self._settings_controls[key]
                ])
                column.controls.append(row)
                if not value:
                    value = utils.USER_DIR
            elif key == 'export_file_name':
                self._settings_controls[key] = ft.TextField()
                row = ft.Row([
                    ft.Text('Ange ett filnamn'),
                    self._settings_controls[key]
                ])
                column.controls.append(row)

            elif type(value) == bool:
                self._settings_controls[key] = ft.Switch(label=key)
                row = ft.Row([
                    self._settings_controls[key]
                ])
                column.controls.append(row)
            if key in self._settings_controls:
                self._settings_controls[key].value = value
            # self._settings_controls[key].update()
        self._settings_content.update()

    def set_data(self, **kwargs) -> None:
        self._settings_controls = {}
        self._data = kwargs
        self._set_data()
        self.set_border(None)

    def get_data(self) -> dict:
        return dict(
            name=self.name,
            description=self.description,
            kwargs=self.settings
        )

    def _set_data(self):
        self._switch.label = self.name
        self._text.value = self.description
        self._switch.update()
        self._text.update()

        if self.settings:
            self._settings_icon_button.visible = True
        else:
            self._settings_icon_button.visible = False
        self._settings_icon_button.update()

    def set_border(self, color=None):
        border = None
        if color:
            border = ft.border.only(top=ft.BorderSide(5, color=color))
            # border = ft.border.all(5, color)
        self._main_container.border = border
        self._main_container.update()