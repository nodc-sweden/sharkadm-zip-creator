import flet as ft
from sharkadm_zip_creator.flet_app import utils
from sharkadm import utils as sharkadm_utils
from sharkadm import workflow

FONT_WEIGHT = ft.FontWeight.W_400
TEXT_SIZE_LABEL_1 = 20
TEXT_SIZE_LABEL_2 = 16


class FrameOperators(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self.expand = True
        col = ft.Column([
            # ft.Text(
            #     'Operationer som kommer utföras:',
            #     size=30,
            #     weight=ft.FontWeight.W_100,
            # ),
            ft.Divider(),
            self.lv
        ], expand=True)

        self.controls.append(col)

    def reset(self) -> None:
        self.lv.controls = []
        self.lv.update()

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow, data_type: str) -> None:
        self.reset()

        self.lv.controls.append(ft.Text(f'Operationer som kommer att utföras är kopplade till datatypen '
                                        f'{data_type.capitalize()}', size=TEXT_SIZE_LABEL_1, weight=FONT_WEIGHT))

        descriptions = wflow.get_validator_before_descriptions()
        if descriptions:
            self.lv.controls.append(ft.Divider())
            self.lv.controls.append(ft.Text('Valideringar', size=TEXT_SIZE_LABEL_2, weight=FONT_WEIGHT))
            for name, desc in descriptions.items():
                self.lv.controls.append(ft.Row([
                    ft.Text(desc),
                    ft.Text(f'({name})')
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        descriptions = wflow.get_transformer_descriptions()
        if descriptions:
            self.lv.controls.append(ft.Divider())
            self.lv.controls.append(ft.Text('Transformeringar', size=TEXT_SIZE_LABEL_2, weight=FONT_WEIGHT))
            for name, desc in descriptions.items():
                self.lv.controls.append(ft.Row([
                    ft.Text(desc),
                    ft.Text(f'({name})')
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        descriptions = wflow.get_validator_after_descriptions()
        if descriptions:
            self.lv.controls.append(ft.Divider())
            self.lv.controls.append(ft.Text('Valideringar efter', size=TEXT_SIZE_LABEL_2, weight=FONT_WEIGHT))
            for name, desc in descriptions.items():
                self.lv.controls.append(ft.Row([
                    ft.Text(desc),
                    ft.Text(f'({name})')
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        descriptions = wflow.get_exporter_descriptions()
        if descriptions:
            self.lv.controls.append(ft.Divider())
            self.lv.controls.append(ft.Text('Exporter', size=TEXT_SIZE_LABEL_2, weight=FONT_WEIGHT))
            for name, desc in descriptions.items():
                self.lv.controls.append(ft.Row([
                    ft.Text(desc),
                    ft.Text(f'({name})')
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        self.lv.update()






