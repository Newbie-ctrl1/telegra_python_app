import flet as ft
import os
import asyncio
from ..services.telegram_manager import TelegramManager
import logging
import requests

class HomeScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.telegram_manager = TelegramManager()
        self.phone_input = ft.TextField(
            label="Nomor Telepon",
            hint_text="Contoh: +628123456789",
            border_radius=10
        )
        self.code_input = ft.TextField(
            label="Kode Verifikasi",
            hint_text="Masukkan kode yang dikirim via Telegram",
            border_radius=10
        )
        
        # Pastikan folder sessions ada
        if not os.path.exists('sessions'):
            os.makedirs('sessions')
            
        # Pastikan folder chat ada
        if not os.path.exists('chat'):
            os.makedirs('chat')

    def create_session_click(self, e):
        if not self.check_server_connection():
            self.show_error("Tidak dapat terhubung ke server. Pastikan server.py sudah berjalan.")
            return
        asyncio.run(self.create_session(e))

    def verify_code_click(self, e):
        asyncio.run(self.verify_code(e))

    def show_chat_history_click(self, e):
        asyncio.run(self.show_chat_history(e))

    def show_profile_settings_click(self, e):
        asyncio.run(self.show_profile_settings(e))

    def show_channel_manager_click(self, e):
        asyncio.run(self.show_channel_manager(e))

    def show_delete_session_click(self, e):
        asyncio.run(self.show_delete_session(e))

    def show_api_settings_click(self, e):
        asyncio.run(self.show_api_settings(e))

    def build(self):
        return ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Telegram Manager", size=24, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.SETTINGS,
                                tooltip="API Settings",
                                on_click=self.show_api_settings_click
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=20
                ),

                # Form Sesi Baru
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Buat Sesi Baru", size=20, weight=ft.FontWeight.BOLD),
                            self.phone_input,
                            ft.ElevatedButton(
                                text="Buat Sesi",
                                on_click=self.create_session_click,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10)
                                )
                            )
                        ]
                    ),
                    padding=20,
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    margin=10
                ),

                # Form Verifikasi
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Verifikasi Kode", size=20, weight=ft.FontWeight.BOLD),
                            self.code_input,
                            ft.ElevatedButton(
                                text="Verifikasi Kode",
                                on_click=self.verify_code_click,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10)
                                )
                            )
                        ]
                    ),
                    padding=20,
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    margin=10
                ),

                # Grid Fitur
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    self.create_feature_button(
                                        "Riwayat Chat",
                                        ft.icons.HISTORY,
                                        self.show_chat_history_click
                                    ),
                                    self.create_feature_button(
                                        "Pengaturan Profil",
                                        ft.icons.PERSON,
                                        self.show_profile_settings_click
                                    )
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    self.create_feature_button(
                                        "Kelola Channel",
                                        ft.icons.GROUP,
                                        self.show_channel_manager_click
                                    ),
                                    self.create_feature_button(
                                        "Hapus Sesi",
                                        ft.icons.DELETE,
                                        self.show_delete_session_click,
                                        is_destructive=True
                                    )
                                ]
                            )
                        ]
                    ),
                    padding=20
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )

    async def check_and_select_session(self, next_action):
        try:
            sessions = await self.telegram_manager.list_sessions()
            
            if not sessions:
                self.show_error("Belum ada sesi yang aktif. Silakan buat sesi baru terlebih dahulu.")
                return
            
            def close_dlg(e):
                dlg.open = False
                self.page.update()

            def session_click(session):
                async def handle_click(e):
                    try:
                        await self.telegram_manager.select_session(session)
                        dlg.open = False
                        self.page.update()
                        await next_action(e)
                    except Exception as ex:
                        self.show_error(str(ex))
                return handle_click

            content = ft.Column(
                controls=[
                    ft.Text("Pilih sesi yang akan digunakan:", size=16),
                    *[ft.ElevatedButton(
                        f"Sesi {session}",
                        on_click=session_click(session)
                    ) for session in sessions]
                ],
                tight=True,
                spacing=10
            )

            dlg = ft.AlertDialog(
                title=ft.Text("Pilih Sesi"),
                content=content,
                actions=[
                    ft.TextButton("Batal", on_click=close_dlg)
                ]
            )

            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

        except Exception as ex:
            self.show_error(str(ex))

    def create_feature_button(self, text: str, icon: str, on_click, is_destructive: bool = False):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=40, color=ft.colors.RED if is_destructive else ft.colors.BLUE),
                    ft.Text(text, size=16, weight=ft.FontWeight.BOLD)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=150,
            height=150,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            margin=5,
            padding=20,
            on_click=on_click,
            ink=True
        )

    async def create_session(self, e):
        try:
            if not self.phone_input.value:
                self.show_error("Masukkan nomor telepon")
                return

            await self.telegram_manager.create_session(self.phone_input.value)
            self.show_success("Kode verifikasi telah dikirim")
        except Exception as ex:
            self.show_error(str(ex))

    async def verify_code(self, e):
        try:
            if not self.code_input.value:
                self.show_error("Masukkan kode verifikasi")
                return

            await self.telegram_manager.verify_code(self.code_input.value)
            self.show_success("Sesi berhasil dibuat")
            self.code_input.value = ""
            self.page.update()
        except Exception as ex:
            self.show_error(str(ex))

    async def show_chat_history(self, e):
        await self.check_and_select_session(self._show_chat_history)

    async def _show_chat_history(self, e):
        try:
            chat_history = await self.telegram_manager.get_chat_history()
            await self.show_chat_dialog(chat_history)
        except Exception as ex:
            self.show_error(str(ex))

    async def show_profile_settings(self, e):
        await self.check_and_select_session(self._show_profile_settings)

    async def _show_profile_settings(self, e):
        def close_dlg(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Pengaturan Profil"),
            content=ft.Column(
                controls=[
                    ft.ElevatedButton("Ubah Username", on_click=self.show_username_dialog),
                    ft.ElevatedButton("Ubah Nama", on_click=self.show_name_dialog)
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Tutup", on_click=close_dlg)
            ]
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    async def show_channel_manager(self, e):
        await self.check_and_select_session(self._show_channel_manager)

    async def _show_channel_manager(self, e):
        def close_dlg(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Kelola Channel"),
            content=ft.Column(
                controls=[
                    ft.ElevatedButton("Lihat Channel & Grup", on_click=self.show_channel_list),
                    ft.ElevatedButton("Keluar dari Semua", on_click=self.leave_all_channels)
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Tutup", on_click=close_dlg)
            ]
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    async def show_delete_session(self, e):
        try:
            sessions = await self.telegram_manager.list_sessions()
            content = ft.Column(
                controls=[
                    ft.Text("Peringatan: Menghapus sesi akan menghapus semua data terkait!", color=ft.colors.RED),
                    *[ft.ElevatedButton(
                        f"Hapus {session}",
                        on_click=lambda s=session: self.delete_session(s)
                    ) for session in sessions]
                ],
                tight=True
            )

            def close_dlg(e):
                dlg.open = False
                self.page.update()

            dlg = ft.AlertDialog(
                title=ft.Text("Hapus Sesi"),
                content=content,
                actions=[
                    ft.TextButton("Tutup", on_click=close_dlg)
                ]
            )

            self.page.dialog = dlg
            dlg.open = True
            self.page.update()
        except Exception as ex:
            self.show_error(str(ex))

    def show_error(self, message: str):
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.RED)
        )

    def show_success(self, message: str):
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=ft.colors.GREEN)
        )

    async def show_api_settings(self, e):
        api_id = ft.TextField(label="API ID")
        api_hash = ft.TextField(label="API Hash")

        def save_settings(e):
            try:
                with open('.env', 'w') as f:
                    f.write(f"API_ID={api_id.value}\n")
                    f.write(f"API_HASH={api_hash.value}\n")
                self.show_success("API credentials berhasil disimpan")
                dlg.open = False
                self.page.update()
            except Exception as ex:
                self.show_error(str(ex))

        def close_dlg(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("API Settings"),
            content=ft.Column(
                controls=[
                    api_id,
                    api_hash,
                    ft.Text(
                        "Dapatkan API credentials di my.telegram.org",
                        size=12,
                        color=ft.colors.GREY
                    )
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Batal", on_click=close_dlg),
                ft.TextButton("Simpan", on_click=save_settings)
            ]
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update() 

    async def show_username_dialog(self, e):
        username_input = ft.TextField(
            label="Username Baru",
            hint_text="Masukkan username tanpa @"
        )

        def close_dlg(e):
            dlg.open = False
            self.page.update()

        async def save_username(e):
            try:
                if not username_input.value:
                    self.show_error("Username tidak boleh kosong")
                    return
                    
                await self.telegram_manager.change_username(username_input.value)
                self.show_success("Username berhasil diubah")
                dlg.open = False
                self.page.update()
            except Exception as ex:
                self.show_error(str(ex))

        dlg = ft.AlertDialog(
            title=ft.Text("Ubah Username"),
            content=ft.Column(
                controls=[
                    username_input,
                    ft.Text(
                        "Username harus unik dan tidak mengandung karakter khusus",
                        size=12,
                        color=ft.colors.GREY
                    )
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Batal", on_click=close_dlg),
                ft.TextButton("Simpan", on_click=save_username)
            ]
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    async def show_name_dialog(self, e):
        first_name_input = ft.TextField(label="Nama Depan")
        last_name_input = ft.TextField(label="Nama Belakang (Opsional)")

        def close_dlg(e):
            dlg.open = False
            self.page.update()

        async def save_name(e):
            try:
                if not first_name_input.value:
                    self.show_error("Nama depan tidak boleh kosong")
                    return
                    
                await self.telegram_manager.change_name(
                    first_name_input.value,
                    last_name_input.value if last_name_input.value else None
                )
                self.show_success("Nama berhasil diubah")
                dlg.open = False
                self.page.update()
            except Exception as ex:
                self.show_error(str(ex))

        dlg = ft.AlertDialog(
            title=ft.Text("Ubah Nama"),
            content=ft.Column(
                controls=[
                    first_name_input,
                    last_name_input
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Batal", on_click=close_dlg),
                ft.TextButton("Simpan", on_click=save_name)
            ]
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    async def show_chat_dialog(self, chat_history: list):
        def close_dlg(e):
            dlg.open = False
            self.page.update()

        content = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            auto_scroll=True
        )

        for message in chat_history:
            content.controls.append(
                ft.Container(
                    content=ft.Text(message, selectable=True),
                    bgcolor=ft.colors.WHITE,
                    padding=10,
                    border_radius=10
                )
            )

        dlg = ft.AlertDialog(
            title=ft.Text("Riwayat Chat"),
            content=content,
            actions=[
                ft.TextButton("Tutup", on_click=close_dlg)
            ]
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    async def show_channel_list(self, e):
        try:
            channels = await self.telegram_manager.list_channels()
            
            def close_dlg(e):
                dlg.open = False
                self.page.update()

            content = ft.ListView(
                expand=True,
                spacing=10,
                padding=20,
                auto_scroll=True
            )

            for channel in channels:
                content.controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    channel['title'],
                                    size=16,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(
                                    f"ID: {channel['id']}",
                                    size=12,
                                    color=ft.colors.GREY
                                ),
                                ft.Text(
                                    f"Tipe: {channel['type']}",
                                    size=12,
                                    color=ft.colors.GREY
                                )
                            ]
                        ),
                        bgcolor=ft.colors.WHITE,
                        padding=10,
                        border_radius=10
                    )
                )

            dlg = ft.AlertDialog(
                title=ft.Text("Daftar Channel & Grup"),
                content=content,
                actions=[
                    ft.TextButton("Tutup", on_click=close_dlg)
                ]
            )

            self.page.dialog = dlg
            dlg.open = True
            self.page.update()
        except Exception as ex:
            self.show_error(str(ex))

    async def leave_all_channels(self, e):
        try:
            def close_dlg(e):
                confirm_dlg.open = False
                self.page.update()

            async def confirm_leave(e):
                try:
                    await self.telegram_manager.leave_all_channels()
                    self.show_success("Berhasil keluar dari semua channel dan grup")
                    confirm_dlg.open = False
                    self.page.update()
                except Exception as ex:
                    self.show_error(str(ex))

            confirm_dlg = ft.AlertDialog(
                title=ft.Text("Konfirmasi"),
                content=ft.Text(
                    "Anda yakin ingin keluar dari semua channel dan grup?\n"
                    "Tindakan ini tidak dapat dibatalkan."
                ),
                actions=[
                    ft.TextButton("Batal", on_click=close_dlg),
                    ft.TextButton(
                        "Keluar",
                        on_click=confirm_leave,
                        style=ft.ButtonStyle(color=ft.colors.RED)
                    )
                ]
            )

            self.page.dialog = confirm_dlg
            confirm_dlg.open = True
            self.page.update()
        except Exception as ex:
            self.show_error(str(ex))

    async def delete_session(self, phone_number: str):
        try:
            def close_dlg(e):
                confirm_dlg.open = False
                self.page.update()

            async def confirm_delete(e):
                try:
                    await self.telegram_manager.delete_session(phone_number)
                    self.show_success(f"Sesi {phone_number} berhasil dihapus")
                    confirm_dlg.open = False
                    self.page.dialog.open = False  # Tutup dialog utama
                    self.page.update()
                except Exception as ex:
                    self.show_error(str(ex))

            confirm_dlg = ft.AlertDialog(
                title=ft.Text("Konfirmasi Hapus"),
                content=ft.Text(
                    f"Anda yakin ingin menghapus sesi {phone_number}?\n"
                    "Semua data terkait akan dihapus dan tidak dapat dikembalikan."
                ),
                actions=[
                    ft.TextButton("Batal", on_click=close_dlg),
                    ft.TextButton(
                        "Hapus",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(color=ft.colors.RED)
                    )
                ]
            )

            self.page.dialog = confirm_dlg
            confirm_dlg.open = True
            self.page.update()
        except Exception as ex:
            self.show_error(str(ex))

    def check_server_connection(self) -> bool:
        """Mengecek apakah server berjalan"""
        try:
            response = requests.get(f"{self.telegram_manager.base_url}/health")
            return response.status_code == 200
        except:
            return False 