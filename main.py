import flet as ft
import os
import glob
from telethon import TelegramClient
from telethon.sync import TelegramClient as SyncTelegramClient
from telethon.tl.functions.account import UpdateUsernameRequest, UpdateProfileRequest, GetAuthorizationsRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import LeaveChannelRequest
import asyncio
import threading

# API Credentials
API_ID = 20081042
API_HASH = '93fd87dcd1be75b59ba8798fc72f1d31'

# Buat folder sessions jika belum ada
if not os.path.exists('sessions'):
    os.makedirs('sessions')

# PWA Configuration
pwa_config = {
    "name": "Telethod Tools",
    "short_name": "Telethod",
    "description": "Tools untuk manajemen akun Telegram",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#2196f3",
    "orientation": "any",
    "icons": [
        {
            "src": "https://fonts.gstatic.com/s/i/materialicons/telegram/v1/24px.svg",
            "sizes": "24x24",
            "type": "image/svg+xml"
        },
        {
            "src": "https://fonts.gstatic.com/s/i/materialicons/telegram/v1/48px.svg",
            "sizes": "48x48",
            "type": "image/svg+xml"
        }
    ]
}

class TelegramManager:
    def __init__(self):
        # Memastikan direktori sessions ada
        if not os.path.exists("sessions"):
            os.makedirs("sessions")
            
    async def create_session(self, phone_number, status_callback):
        client = TelegramClient(f"sessions/{phone_number}", API_ID, API_HASH)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone_number)
                await status_callback("Kode verifikasi telah dikirim ke nomor Anda")
                return client
            await status_callback("Sesi berhasil dibuat")
            return client
        except Exception as e:
            await status_callback(f"Terjadi kesalahan: {str(e)}")
            return None

def run_async_function(page, func, *args):
    async def create_tasks():
        try:
            await func(*args)
        except Exception as e:
            print(f"[DEBUG] Error in async function: {e}")
            import traceback
            print("[DEBUG] Full traceback:")
            print(traceback.format_exc())

    # Buat task baru dan jalankan di event loop yang ada
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Jika loop sudah berjalan, tambahkan task ke loop yang ada
            loop.create_task(create_tasks())
        else:
            # Jika belum ada loop yang berjalan, jalankan task secara langsung
            loop.run_until_complete(create_tasks())
    except RuntimeError:
        # Jika tidak ada event loop di thread ini, buat loop baru
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(create_tasks())
        finally:
            loop.close()
    except Exception as e:
        print(f"[DEBUG] Error in run_async_function: {e}")

async def main(page: ft.Page):
    # Konfigurasi PWA dan responsif
    page.web_only = True
    page.title = "Telethod Tools"
    page.theme_mode = "dark"
    page.padding = 10
    page.scroll = "auto"
    page.spacing = 10
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Konfigurasi responsif
    page.responsive = True
    page.update()
    
    # PWA metadata
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
    )
    
    # Tambahkan meta tags untuk PWA
    meta_tags = [
        '<link rel="manifest" href="/manifest.json">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />',
        '<meta name="theme-color" content="#2196f3"/>',
        '<meta name="mobile-web-app-capable" content="yes"/>',
        '<meta name="apple-mobile-web-app-capable" content="yes"/>',
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>',
        '<meta name="apple-mobile-web-app-title" content="Telethod Tools"/>',
        '<link rel="icon" type="image/svg+xml" href="https://fonts.gstatic.com/s/i/materialicons/telegram/v1/24px.svg"/>',
    ]
    
    # Service Worker script
    sw_script = """
        <script>
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                    navigator.serviceWorker.register('/sw.js');
                });
            }
        </script>
    """
    
    page.head = ''.join(meta_tags) + sw_script
    
    # Komponen UI untuk Create Session
    phone_input = ft.TextField(
        label="Nomor Telepon",
        hint_text="+628xxxxxxxxxx",
        expand=True,
        width=None,
        text_align=ft.TextAlign.LEFT,
        content_padding=10,
    )
    
    code_input = ft.TextField(
        label="Kode Verifikasi",
        expand=True,
        width=None,
        visible=False,
        text_align=ft.TextAlign.LEFT,
        content_padding=10,
    )
    
    status_text = ft.Text(
        size=14,
        color=ft.Colors.GREEN,
        text_align=ft.TextAlign.CENTER,
        weight=ft.FontWeight.W_500,
    )
    
    client = None
    
    async def update_status(message):
        status_text.value = message
        page.update()
    
    async def create_session_clicked(e):
        if not phone_input.value:
            await update_status("Mohon masukkan nomor telepon!")
            return
            
        telegram_manager = TelegramManager()
        nonlocal client
        client = await telegram_manager.create_session(
            phone_input.value,
            update_status
        )
        
        if client:
            code_input.visible = True
            verify_button.visible = True
            create_button.visible = False
            page.update()
    
    async def verify_code_clicked(e):
        if not code_input.value:
            await update_status("Mohon masukkan kode verifikasi!")
            return
            
        try:
            await client.sign_in(phone_input.value, code_input.value)
            await update_status(f"Sesi berhasil dibuat dan disimpan sebagai sessions/{phone_input.value}.session")
            refresh_sessions()
            
            # Reset form
            phone_input.value = ""
            code_input.value = ""
            code_input.visible = False
            verify_button.visible = False
            create_button.visible = True
            page.update()
            
        except Exception as e:
            await update_status(f"Gagal verifikasi: {str(e)}")
    
    create_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.ADD),
            ft.Text("Buat Sesi", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_600,
        ),
        width=200,
        on_click=create_session_clicked
    )
    
    verify_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE),
            ft.Text("Verifikasi Kode", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_600,
        ),
        width=200,
        visible=False,
        on_click=verify_code_clicked
    )

    # Komponen UI Lainnya
    output_text = ft.Text(size=16, color="white", selectable=True)
    username_input = ft.TextField(label="Username Baru", width=300)
    firstname_input = ft.TextField(label="Nama Depan", width=300)
    lastname_input = ft.TextField(label="Nama Belakang", width=300)

    def get_session_files():
        # Ambil hanya nama file sesi tanpa path lengkap
        return [os.path.basename(session).replace('.session', '') 
                for session in glob.glob('sessions/*.session')]

    session_dropdown = ft.Dropdown(
        width=300,
        label="Pilih Sesi",
        options=[
            ft.dropdown.Option(text=session) 
            for session in get_session_files()
        ]
    )

    def refresh_sessions():
        session_dropdown.options = [
            ft.dropdown.Option(text=session)
            for session in get_session_files()
        ]
        page.update()

    def delete_session_handler(e):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi yang akan dihapus!"
            page.update()
            return

        try:
            session_path = os.path.join("sessions", f"{session_dropdown.value}.session")
            if os.path.exists(session_path):
                os.remove(session_path)
                output_text.value = f"Sesi {session_dropdown.value} berhasil dihapus"
                refresh_sessions()  # Perbarui daftar sesi
                session_dropdown.value = None  # Reset pilihan dropdown
            else:
                output_text.value = f"File sesi tidak ditemukan: {session_path}"
        except Exception as e:
            output_text.value = f"Error saat menghapus sesi: {str(e)}"
        finally:
            page.update()

    # Tombol hapus sesi
    delete_session_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.DELETE_FOREVER),
            ft.Text("Hapus Sesi", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_600,
        ),
        width=200,
        on_click=delete_session_handler
    )

    def change_username_handler(e, page, session_dropdown, username_input, output_text):
        if not session_dropdown.value or not username_input.value:
            output_text.value = "Pilih sesi dan masukkan username baru!"
            page.update()
            return
        run_async_function(page, change_username_clicked, e, page, session_dropdown, username_input, output_text)

    async def change_username_clicked(e, page, session_dropdown, username_input, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return

        if not username_input.value:
            output_text.value = "Masukkan username baru!"
            page.update()
            return

        try:
            session_path = os.path.join("sessions", f"{session_dropdown.value}.session")
            output_text.value = f"Mencoba membuka sesi: {session_path}"
            page.update()

            if not os.path.exists(session_path):
                output_text.value = f"Error: File sesi tidak ditemukan di {session_path}\nSilakan buat sesi baru."
                page.update()
                return

            try:
                with open(session_path, 'rb') as f:
                    pass
            except PermissionError:
                output_text.value = f"Error: Tidak memiliki izin untuk membaca file sesi {session_path}"
                page.update()
                return
            except Exception as e:
                output_text.value = f"Error saat mencoba membaca file sesi: {str(e)}"
                page.update()
                return

            output_text.value = "Mencoba membuat koneksi client..."
            page.update()

            async with TelegramClient(session_path, API_ID, API_HASH) as client:
                output_text.value = "Mencoba menghubungkan ke Telegram..."
                page.update()
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    output_text.value = "Error: Sesi tidak valid atau telah kadaluarsa"
                    page.update()
                    return

                output_text.value = "Mengubah username..."
                page.update()

                await client(UpdateUsernameRequest(username_input.value))
                output_text.value = f"Username berhasil diubah menjadi: {username_input.value}"

        except Exception as e:
            error_detail = f"""
Error saat mengubah username:
- Tipe Error: {type(e).__name__}
- Detail Error: {str(e)}
- File Sesi: {session_dropdown.value}
            """
            output_text.value = error_detail
            print(error_detail)
            import traceback
            print("Full traceback:")
            print(traceback.format_exc())
        finally:
            page.update()

    def change_name_handler(e, page, session_dropdown, firstname_input, lastname_input, output_text):
        if not session_dropdown.value or not firstname_input.value:
            output_text.value = "Pilih sesi dan masukkan nama depan!"
            page.update()
            return
        run_async_function(page, change_name_clicked, e, page, session_dropdown, firstname_input, lastname_input, output_text)

    async def change_name_clicked(e, page, session_dropdown, firstname_input, lastname_input, output_text):
        if not session_dropdown.value or not firstname_input.value:
            output_text.value = "Pilih sesi dan masukkan nama depan!"
            page.update()
            return

        try:
            async with TelegramClient(f"sessions/{session_dropdown.value}", API_ID, API_HASH) as client:
                await client.connect()
                if await client.is_user_authorized():
                    await client(UpdateProfileRequest(
                        first_name=firstname_input.value,
                        last_name=lastname_input.value if lastname_input.value else None
                    ))
                    output_text.value = f"Nama berhasil diubah menjadi: {firstname_input.value} {lastname_input.value or ''}"
                else:
                    output_text.value = "Sesi tidak valid. Silakan buat sesi baru."
        except Exception as e:
            output_text.value = f"Error: {str(e)}"
        page.update()

    def check_sessions_handler(e, page, session_dropdown, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return
        run_async_function(page, check_sessions_clicked, e, page, session_dropdown, output_text)

    async def check_sessions_clicked(e, page, session_dropdown, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return

        try:
            session_path = os.path.join("sessions", f"{session_dropdown.value}.session")
            output_text.value = f"Mencoba membuka sesi: {session_path}"
            page.update()

            if not os.path.exists(session_path):
                output_text.value = f"Error: File sesi tidak ditemukan di {session_path}\nSilakan buat sesi baru."
                page.update()
                return

            try:
                with open(session_path, 'rb') as f:
                    pass
            except PermissionError:
                output_text.value = f"Error: Tidak memiliki izin untuk membaca file sesi {session_path}"
                page.update()
                return
            except Exception as e:
                output_text.value = f"Error saat mencoba membaca file sesi: {str(e)}"
                page.update()
                return

            output_text.value = "Mencoba membuat koneksi client..."
            page.update()

            async with TelegramClient(session_path, API_ID, API_HASH) as client:
                output_text.value = "Mencoba menghubungkan ke Telegram..."
                page.update()
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    output_text.value = "Error: Sesi tidak valid atau telah kadaluarsa"
                    page.update()
                    return

                output_text.value = "Mengecek sesi aktif..."
                page.update()

                result = await client(GetAuthorizationsRequest())
                if result.authorizations:
                    sessions_info = ["Sesi Aktif:"]
                    for session in result.authorizations:
                        sessions_info.extend([
                            f"\nPerangkat: {session.device_model}",
                            f"Platform: {session.platform}",
                            f"Versi App: {session.app_version}",
                            f"IP: {session.ip}",
                            f"Negara: {session.country}",
                            f"Terakhir Aktif: {session.date_active}",
                            f"App Resmi: {'Ya' if session.official_app else 'Tidak'}"
                        ])
                    output_text.value = "\n".join(sessions_info)
                else:
                    output_text.value = "Tidak ada sesi aktif."

        except Exception as e:
            error_detail = f"""
Error saat mengecek sesi:
- Tipe Error: {type(e).__name__}
- Detail Error: {str(e)}
- File Sesi: {session_dropdown.value}
            """
            output_text.value = error_detail
            print(error_detail)
            import traceback
            print("Full traceback:")
            print(traceback.format_exc())
        finally:
            page.update()

    def leave_channels_handler(e, page, session_dropdown, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return
        # Gunakan run_async_function untuk menjalankan fungsi async
        run_async_function(page, leave_all_channels_clicked, e, page, session_dropdown, output_text)

    async def leave_all_channels_clicked(e, page, session_dropdown, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return

        try:
            session_path = os.path.join("sessions", f"{session_dropdown.value}.session")
            output_text.value = f"Mencoba membuka sesi: {session_path}"
            page.update()

            if not os.path.exists(session_path):
                output_text.value = f"Error: File sesi tidak ditemukan di {session_path}\nSilakan buat sesi baru."
                page.update()
                return

            try:
                with open(session_path, 'rb') as f:
                    pass
            except PermissionError:
                output_text.value = f"Error: Tidak memiliki izin untuk membaca file sesi {session_path}"
                page.update()
                return
            except Exception as e:
                output_text.value = f"Error saat mencoba membaca file sesi: {str(e)}"
                page.update()
                return

            output_text.value = "Mencoba membuat koneksi client..."
            page.update()

            async with TelegramClient(session_path, API_ID, API_HASH) as client:
                output_text.value = "Mencoba menghubungkan ke Telegram..."
                page.update()
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    output_text.value = "Error: Sesi tidak valid atau telah kadaluarsa"
                    page.update()
                    return

                output_text.value = "Mengambil daftar channel..."
                page.update()

                dialogs = await client.get_dialogs()
                count = 0
                for dialog in dialogs:
                    if dialog.is_channel or dialog.is_group:
                        await client(LeaveChannelRequest(dialog.id))
                        count += 1
                        output_text.value = f"Sedang keluar dari channel... ({count} channel)"
                        page.update()
                
                output_text.value = f"Berhasil keluar dari {count} channel dan grup"

        except Exception as e:
            error_detail = f"""
Error saat keluar dari channel:
- Tipe Error: {type(e).__name__}
- Detail Error: {str(e)}
- File Sesi: {session_dropdown.value}
            """
            output_text.value = error_detail
            print(error_detail)
            import traceback
            print("Full traceback:")
            print(traceback.format_exc())
        finally:
            page.update()

    def read_chat_history_handler(e, page, session_dropdown, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return
        run_async_function(page, read_chat_history, e, page, session_dropdown, output_text)

    async def read_chat_history(e, page, session_dropdown, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return

        try:
            # Perbaikan path file sesi - gunakan nama file saja
            session_path = os.path.join("sessions", f"{session_dropdown.value}.session")
            
            output_text.value = f"Mencoba membuka sesi: {session_path}"
            page.update()

            # Debug info
            print(f"Session dropdown value: {session_dropdown.value}")
            print(f"Full session path: {session_path}")
            print(f"File exists: {os.path.exists(session_path)}")

            # Cek apakah file sesi ada
            if not os.path.exists(session_path):
                output_text.value = f"Error: File sesi tidak ditemukan di {session_path}\nSilakan buat sesi baru."
                page.update()
                return

            # Cek permission file
            try:
                with open(session_path, 'rb') as f:
                    pass
            except PermissionError:
                output_text.value = f"Error: Tidak memiliki izin untuk membaca file sesi {session_path}"
                page.update()
                return
            except Exception as e:
                output_text.value = f"Error saat mencoba membaca file sesi: {str(e)}"
                page.update()
                return

            output_text.value = "Mencoba membuat koneksi client..."
            page.update()

            async with TelegramClient(session_path, API_ID, API_HASH) as client:
                output_text.value = "Mencoba menghubungkan ke Telegram..."
                page.update()
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    output_text.value = "Error: Sesi tidak valid atau telah kadaluarsa"
                    page.update()
                    return

                output_text.value = "Mengambil daftar dialog..."
                page.update()
                
                dialogs = await client.get_dialogs()
                notification_dialog = next((dialog for dialog in dialogs if dialog.name == "Telegram"), None)

                if not notification_dialog:
                    output_text.value = "Error: Tidak dapat menemukan dialog notifikasi Telegram"
                    page.update()
                    return

                output_text.value = "Mengambil riwayat chat..."
                page.update()

                messages = await client(GetHistoryRequest(
                    peer=notification_dialog.input_entity,
                    limit=100,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                chat_history = ["Riwayat Chat:"]
                for message in messages.messages[:10]:
                    chat_history.append(f"\n[{message.date}] {message.message}")
                output_text.value = "\n".join(chat_history)

        except Exception as e:
            error_detail = f"""
Error saat membaca riwayat chat:
- Tipe Error: {type(e).__name__}
- Detail Error: {str(e)}
- File Sesi: {session_dropdown.value}
            """
            output_text.value = error_detail
            # Print untuk debugging di console
            print(error_detail)
            import traceback
            print("Full traceback:")
            print(traceback.format_exc())
        finally:
            page.update()

    def list_channels_handler(e, page, session_dropdown, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return
        # Gunakan run_async_function untuk menjalankan fungsi async
        run_async_function(page, list_channels_clicked, e, page, session_dropdown, output_text)

    async def list_channels_clicked(e, page, session_dropdown, output_text):
        if not session_dropdown.value:
            output_text.value = "Pilih sesi terlebih dahulu!"
            page.update()
            return

        try:
            session_path = os.path.join("sessions", f"{session_dropdown.value}.session")
            output_text.value = f"Mencoba membuka sesi: {session_path}"
            page.update()

            if not os.path.exists(session_path):
                output_text.value = f"Error: File sesi tidak ditemukan di {session_path}\nSilakan buat sesi baru."
                page.update()
                return

            try:
                with open(session_path, 'rb') as f:
                    pass
            except PermissionError:
                output_text.value = f"Error: Tidak memiliki izin untuk membaca file sesi {session_path}"
                page.update()
                return
            except Exception as e:
                output_text.value = f"Error saat mencoba membaca file sesi: {str(e)}"
                page.update()
                return

            output_text.value = "Mencoba membuat koneksi client..."
            page.update()

            async with TelegramClient(session_path, API_ID, API_HASH) as client:
                output_text.value = "Mencoba menghubungkan ke Telegram..."
                page.update()
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    output_text.value = "Error: Sesi tidak valid atau telah kadaluarsa"
                    page.update()
                    return

                output_text.value = "Mengambil daftar channel..."
                page.update()

                dialogs = await client.get_dialogs()
                channels = [dialog for dialog in dialogs if dialog.is_channel or dialog.is_group]
                
                if channels:
                    channels_info = ["Channel dan Grup yang Diikuti:"]
                    for channel in channels:
                        channels_info.append(f"\n- {channel.title} (ID: {channel.id})")
                    output_text.value = "\n".join(channels_info)
                else:
                    output_text.value = "Tidak ada channel atau grup yang diikuti."

        except Exception as e:
            error_detail = f"""
Error saat mengambil daftar channel:
- Tipe Error: {type(e).__name__}
- Detail Error: {str(e)}
- File Sesi: {session_dropdown.value}
            """
            output_text.value = error_detail
            print("[DEBUG] Error detail:", error_detail)
            import traceback
            print("[DEBUG] Full traceback:")
            print(traceback.format_exc())
        finally:
            page.update()

    # Tombol-tombol dengan ikon dan warna
    change_username_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.EDIT),
            ft.Text("Ubah Username", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_600,
        ),
        width=200,
        on_click=lambda e: change_username_handler(e, page, session_dropdown, username_input, output_text)
    )

    change_name_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.PERSON),
            ft.Text("Ubah Nama", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_600,
        ),
        width=200,
        on_click=lambda e: change_name_handler(e, page, session_dropdown, firstname_input, lastname_input, output_text)
    )

    check_sessions_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.LIST_ALT),
            ft.Text("Cek Sesi Aktif", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.PURPLE_600,
        ),
        width=200,
        on_click=lambda e: check_sessions_handler(e, page, session_dropdown, output_text)
    )

    leave_channels_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.EXIT_TO_APP),
            ft.Text("Keluar Channel", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_600,
        ),
        width=200,
        on_click=lambda e: leave_channels_handler(e, page, session_dropdown, output_text)
    )

    list_channels_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.FORMAT_LIST_BULLETED),
            ft.Text("Daftar Channel", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.TEAL_600,
        ),
        width=200,
        on_click=lambda e: list_channels_handler(e, page, session_dropdown, output_text)
    )

    exit_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.POWER_SETTINGS_NEW),
            ft.Text("Keluar Aplikasi", size=16)
        ]),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_900,
        ),
        width=200,
        on_click=lambda _: page.window.destroy()
    )

    # Container untuk menampung menu yang aktif
    active_menu = ft.Container(padding=20)

    def show_session_menu():
        active_menu.content = ft.Container(
            content=ft.Column([
                ft.Text("Manajemen Sesi", size=24, weight="bold", color=ft.Colors.BLUE),
                ft.Container(
                    content=ft.Column([
                        username_input,
                        firstname_input,
                        lastname_input,
                        ft.Row(
                            [change_username_btn, change_name_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20
                        ),
                    ], spacing=20),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_50,
                ),
                ft.Container(
                    content=ft.Text(
                        "Catatan: Pastikan username belum digunakan oleh pengguna lain",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True
                    ),
                    padding=ft.padding.only(top=10),
                ),
            ], spacing=20),
            padding=20,
        )
        page.update()

    def show_channel_menu():
        active_menu.content = ft.Container(
            content=ft.Column([
                ft.Text("Manajemen Channel", size=24, weight="bold", color=ft.Colors.PURPLE),
                ft.Container(
                    content=ft.Column([
                        ft.Row(
                            [check_sessions_btn, leave_channels_btn, list_channels_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                            wrap=True,
                        ),
                    ], spacing=20),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.PURPLE_200),
                    border_radius=10,
                    bgcolor=ft.Colors.PURPLE_50,
                ),
                ft.Container(
                    content=ft.Text(
                        "Peringatan: Keluar dari channel tidak dapat dibatalkan",
                        size=12,
                        color=ft.Colors.RED_400,
                        italic=True
                    ),
                    padding=ft.padding.only(top=10),
                ),
            ], spacing=20),
            padding=20,
        )
        page.update()

    def show_history_menu():
        active_menu.content = ft.Container(
            content=ft.Column([
                ft.Text("Riwayat Chat", size=24, weight="bold", color=ft.Colors.TEAL),
                ft.Container(
                    content=ft.Column([
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.HISTORY),
                                ft.Text("Lihat Riwayat Chat", size=16)
                            ]),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.TEAL_600,
                            ),
                            width=200,
                            on_click=lambda e: read_chat_history_handler(e, page, session_dropdown, output_text)
                        ),
                    ], spacing=20),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.TEAL_200),
                    border_radius=10,
                    bgcolor=ft.Colors.TEAL_50,
                ),
                ft.Container(
                    content=ft.Text(
                        "Info: Menampilkan 10 pesan terakhir dari riwayat chat",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True
                    ),
                    padding=ft.padding.only(top=10),
                ),
            ], spacing=20),
            padding=20,
        )
        page.update()

    # Modifikasi menu_items untuk navigasi ke halaman baru
    menu_items = [
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.MANAGE_ACCOUNTS_ROUNDED,
                        size=50,
                        color=ft.Colors.BLUE,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_50,
                ),
                ft.Container(
                    content=ft.Text(
                        "Manajemen Sesi", 
                        size=14, 
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=5,
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            on_click=lambda _: page.go("/session"),
            padding=15,
            border_radius=10,
            ink=True,
            bgcolor=ft.Colors.BLUE_ACCENT,
            width=150,
            height=150,
        ),
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.PERSON_ROUNDED,
                        size=50,
                        color=ft.Colors.GREEN,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.GREEN_50,
                ),
                ft.Text("Pengaturan Profil", 
                    size=14, 
                    color=ft.Colors.GREEN,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            on_click=lambda _: page.go("/profile"),
            padding=15,
            border_radius=10,
            ink=True,
            bgcolor=ft.Colors.GREEN_ACCENT,
            width=150,
            height=150,
        ),
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.GROUPS_ROUNDED,
                        size=50,
                        color=ft.Colors.PURPLE,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.PURPLE_50,
                ),
                ft.Text("Manajemen Channel", 
                    size=14, 
                    color=ft.Colors.PURPLE,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            on_click=lambda _: page.go("/channel"),
            padding=15,
            border_radius=10,
            ink=True,
            bgcolor=ft.Colors.PURPLE_ACCENT,
            width=150,
            height=150,
        ),
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.HISTORY_ROUNDED,
                        size=50,
                        color=ft.Colors.TEAL,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.TEAL_50,
                ),
                ft.Text("Riwayat Chat", 
                    size=14, 
                    color=ft.Colors.TEAL,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            on_click=lambda _: page.go("/history"),
            padding=15,
            border_radius=10,
            ink=True,
            bgcolor=ft.Colors.TEAL_ACCENT,
            width=150,
            height=150,
        ),
    ]

    # Container untuk menu dengan layout responsif
    menu_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=menu_item,
                            col={"sm": 12, "md": 6, "lg": 3},
                    padding=5,
                ) for menu_item in menu_items
            ],
            alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=10,
        margin=ft.margin.only(top=20, bottom=20),
    )

    # Output area dengan style yang lebih baik
    output_area = ft.Container(
        content=ft.Column([
            ft.Text("Output", size=20, weight="bold"),
            ft.Container(
                content=output_text,
                padding=20,
                bgcolor=ft.Colors.BLACK12,
                border_radius=5,
                expand=True,
            ),
        ], spacing=20),
        padding=20,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=10,
    )

    def route_change(route):
        page.views.clear()
        
        # Halaman Utama
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(
                                            "Telethod Tools",
                                            size=40,
                                            weight="bold",
                                            color=ft.Colors.BLUE,
                                            text_align=ft.TextAlign.CENTER,
                                            style=ft.TextStyle(
                                                shadow=ft.BoxShadow(
                                                    blur_radius=10,
                                                    color=ft.Colors.BLUE_200,
                                                    offset=ft.Offset(0, 0),
                                                    spread_radius=1,
                                                )
                                            )
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                "by @Rendibagus",
                                                size=18,
                                                color=ft.Colors.BLUE_GREY_400,
                                                italic=True,
                                                text_align=ft.TextAlign.CENTER,
                                                style=ft.TextStyle(
                                                    shadow=ft.BoxShadow(
                                                        blur_radius=5,
                                                        color=ft.Colors.BLUE_GREY_100,
                                                        offset=ft.Offset(0, 0),
                                                        spread_radius=1,
                                                    )
                                                )
                                            ),
                                            margin=ft.margin.only(top=5),
                                        ),
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                    padding=30,
                                    border_radius=10,
                                    gradient=ft.LinearGradient(
                                        begin=ft.alignment.top_center,
                                        end=ft.alignment.bottom_center,
                                        colors=[
                                            ft.Colors.BLUE_50,
                                            ft.Colors.WHITE,
                                        ],
                                    ),
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            alignment=ft.alignment.center,
                        ),
                        ft.Divider(height=30, color=ft.Colors.BLUE_100),
                        # Container untuk Create Session
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Buat Sesi Baru", size=20, weight="bold", color=ft.Colors.BLUE),
                                phone_input,
                                code_input,
                                ft.Row(
                                    [create_button, verify_button],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                status_text,
                            ], spacing=20),
                            padding=20,
                            border=ft.border.all(1, ft.Colors.BLUE_200),
                            border_radius=10,
                            bgcolor=ft.Colors.BLUE_50,
                        ),
                        ft.Divider(),
                        menu_container,
                        ft.Divider(),
                        ft.Container(
                            content=exit_btn,
                            alignment=ft.alignment.center,
                            padding=20,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        # Halaman Manajemen Sesi
        elif page.route == "/session":
            page.views.append(
                ft.View(
                    "/session",
                    [
                        ft.AppBar(
                            title=ft.Text("Manajemen Sesi"),
                            bgcolor=ft.Colors.RED,
                            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        ),
                        ft.Container(
                            content=ft.Column([
                                # Container untuk Cek Sesi Aktif
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Cek Sesi Aktif", size=20, weight="bold", color=ft.Colors.BLUE),
                                        session_dropdown,
                                        ft.Row(
                                            [check_sessions_btn],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                    ], spacing=20),
                                    padding=20,
                                    border=ft.border.all(1, ft.Colors.BLUE_200),
                                    border_radius=10,
                                    bgcolor=ft.Colors.BLUE_50,
                                ),
                                # Container untuk Hapus Sesi
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Hapus Sesi", size=20, weight="bold", color=ft.Colors.RED),
                                        ft.Row(
                                            [delete_session_btn],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                        ft.Text(
                                            "Peringatan: Sesi yang dihapus tidak dapat dikembalikan!",
                                            size=12,
                                            color=ft.Colors.RED_400,
                                            italic=True
                                        ),
                                    ], spacing=20),
                                    padding=20,
                                    border=ft.border.all(1, ft.Colors.RED_200),
                                    border_radius=10,
                                    bgcolor=ft.Colors.RED_50,
                                ),
                                output_area,
                            ], spacing=20),
                            padding=20,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        # Halaman Pengaturan Profil
        elif page.route == "/profile":
            page.views.append(
                ft.View(
                    "/profile",
                    [
                        ft.AppBar(
                            title=ft.Text("Pengaturan Profil"),
                            bgcolor=ft.Colors.GREEN,
                            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        ),
                        ft.Container(
                            content=ft.Column([
                                # Container untuk Pilih Sesi
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Pilih Sesi", size=20, weight="bold", color=ft.Colors.BLUE),
                                        session_dropdown,
                                    ], spacing=20),
                                    padding=20,
                                    border=ft.border.all(1, ft.Colors.BLUE_200),
                                    border_radius=10,
                                    bgcolor=ft.Colors.BLUE_50,
                                ),
                                # Container untuk Ubah Username
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Ubah Username", size=20, weight="bold", color=ft.Colors.GREEN),
                                        username_input,
                                        ft.Row(
                                            [change_username_btn],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                        ft.Text(
                                            "Catatan: Username harus unik dan belum digunakan",
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                            italic=True
                                        ),
                                    ], spacing=20),
                                    padding=20,
                                    border=ft.border.all(1, ft.Colors.GREEN_200),
                                    border_radius=10,
                                    bgcolor=ft.Colors.GREEN_50,
                                ),
                                # Container untuk Ubah Nama
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Ubah Nama", size=20, weight="bold", color=ft.Colors.TEAL),
                                        firstname_input,
                                        lastname_input,
                                        ft.Row(
                                            [change_name_btn],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                        ft.Text(
                                            "Catatan: Nama depan wajib diisi, nama belakang opsional",
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                            italic=True
                                        ),
                                    ], spacing=20),
                                    padding=20,
                                    border=ft.border.all(1, ft.Colors.TEAL_200),
                                    border_radius=10,
                                    bgcolor=ft.Colors.TEAL_50,
                                ),
                                output_area,
                            ], spacing=20),
                            padding=20,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        # Halaman Manajemen Channel
        elif page.route == "/channel":
            page.views.append(
                ft.View(
                    "/channel",
                    [
                        ft.AppBar(
                            title=ft.Text("Manajemen Channel"),
                            bgcolor=ft.Colors.PURPLE,
                            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Column([
                                        session_dropdown,  # Tambahkan di awal
                                        ft.Row(
                                            [leave_channels_btn, list_channels_btn],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=20,
                                            wrap=True,
                                        ),
                                    ], spacing=20),
                                    padding=20,
                                    border=ft.border.all(1, ft.Colors.PURPLE_200),
                                    border_radius=10,
                                    bgcolor=ft.Colors.PURPLE_50,
                                ),
                                output_area,
                            ], spacing=20),
                            padding=20,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        # Halaman Riwayat Chat
        elif page.route == "/history":
            page.views.append(
                ft.View(
                    "/history",
                    [
                        ft.AppBar(
                            title=ft.Text("Riwayat Chat"),
                            bgcolor=ft.Colors.TEAL,
                            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Column([
                                        session_dropdown,  # Tambahkan di awal
                                        ft.ElevatedButton(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.HISTORY),
                                                ft.Text("Lihat Riwayat Chat", size=16)
                                            ]),
                                            style=ft.ButtonStyle(
                                                color=ft.Colors.WHITE,
                                                bgcolor=ft.Colors.TEAL_600,
                                            ),
                                            width=200,
                                            on_click=lambda e: read_chat_history_handler(e, page, session_dropdown, output_text)
                                        ),
                                    ], spacing=20),
                                    padding=20,
                                    border=ft.border.all(1, ft.Colors.TEAL_200),
                                    border_radius=10,
                                    bgcolor=ft.Colors.TEAL_50,
                                ),
                                output_area,
                            ], spacing=20),
                            padding=20,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    try:
        # Create assets directory if not exists
        if not os.path.exists("assets"):
            os.makedirs("assets")
            
        # Dapatkan semua alamat IP yang tersedia
        import socket
        hostname = socket.gethostname()
        ip_addresses = []
        
        # Coba dapatkan alamat IP
        try:
            # Dapatkan semua alamat IP yang terkait dengan hostname
            ips = socket.gethostbyname_ex(hostname)[2]
            # Filter hanya IP lokal (192.168.x.x, 10.x.x.x, dll)
            ip_addresses = [ip for ip in ips if ip.startswith(('192.168.', '10.', '172.'))]
        except Exception as e:
            print(f"Error mendapatkan IP: {e}")
            # Fallback ke localhost jika gagal
            ip_addresses = ['127.0.0.1']
        
        # Jalankan aplikasi
        port = 8550
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            port=port,
            assets_dir="assets"
        )
        
        print(f"\nAplikasi berjalan!")
        print(f"Akses melalui browser di HP dengan salah satu alamat berikut:")
        for ip in ip_addresses:
            print(f"http://{ip}:{port}")
            
    except Exception as e:
        print(f"[DEBUG] Error starting app: {e}") 