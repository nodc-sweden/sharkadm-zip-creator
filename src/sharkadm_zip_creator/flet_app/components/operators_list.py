import flet as ft
from sharkadm import workflow

FONT_WEIGHT = ft.FontWeight.W_400
TEXT_SIZE_LABEL_1 = 20
TEXT_SIZE_LABEL_2 = 16


@ft.control
class ListOperatorsComponent(ft.Container):
    expand: bool = True

    # def init(self):
    #     self._lv_color = ft.Colors.GREY_500
    #
    #     self.lv = ft.ListView(
    #         spacing=10,
    #         padding=20,
    #         expand=True,   # keep this
    #     )
    #
    #     self.content = ft.Container(
    #         expand=True,
    #         bgcolor=self._lv_color,
    #         content=self.lv,
    #     )
    #
    #     for i in range(100):
    #         self.lv.controls.append(ft.Text(f"Line {i}"))

    # @ft.control
    # class ListOperatorsComponent(ft.Container):
    #     expand: bool = True
    #
    #     def init(self):
    #         self.lv = ft.ListView()
    #
    #         for i in range(200):
    #             self.lv.controls.append(ft.Text(f"Row {i}"))
    #
    #         self.content = ft.Container(
    #             bgcolor=ft.Colors.GREY_500,
    #             expand=True,
    #             content=self.lv,
    #         )

    def init(self):
        self._lv_color = ft.Colors.GREY_500

        self.lv = ft.ListView(
            spacing=10,
            padding=20,
            # width=150,
            auto_scroll=False,
            expand=True,
        )
        self.content = ft.Container(
            bgcolor=self._lv_color,
            content=self.lv,
            height=500,
            expand=True,
            border_radius=30,
        )

    def reset(self) -> None:
        self.lv.controls.clear()
        # self.lv.update()

    def set_workflow(self, wflow: workflow.SHARKadmWorkflow) -> None:
        self.reset()
        text_color = "black"
        self.lv.controls.append(
            ft.Text(
                f"Operationer som kommer att utföras är kopplade till datatypen "
                f"{wflow.data_type.data_type_in_data}",
                size=TEXT_SIZE_LABEL_1,
                weight=FONT_WEIGHT,
                color=text_color,
            )
        )

        descriptions = wflow.get_operator_descriptions()
        if descriptions:
            self.lv.controls.append(ft.Divider())
            self.lv.controls.append(
                ft.Text(
                    "OPERATIONER",
                    size=TEXT_SIZE_LABEL_2,
                    weight=FONT_WEIGHT,
                    color=text_color,
                )
            )
            for name, desc in descriptions.items():
                self.lv.controls.append(
                    ft.Row(
                        [
                            # ft.Text(desc, no_wrap=False),
                            # ft.Text(
                            #     desc,
                            #     expand=True,
                            # ),
                            ft.Text(desc, color=text_color),
                            ft.Text(f"({name})", color=text_color),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        expand=True,
                    )
                )

        descriptions = wflow.get_exporter_descriptions()
        if descriptions:
            self.lv.controls.append(ft.Divider())
            self.lv.controls.append(
                ft.Text(
                    "EXPORTER",
                    size=TEXT_SIZE_LABEL_2,
                    weight=FONT_WEIGHT,
                    color=text_color,
                )
            )
            for name, desc in descriptions.items():
                self.lv.controls.append(
                    ft.Row(
                        [
                            # ft.Container(
                            #     content=ft.Text(desc),
                            #     expand=True,
                            # ),
                            ft.Text(desc, color=text_color),
                            ft.Text(f"({name})", color=text_color),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        expand=True,
                    )
                )
        self.lv.update()
