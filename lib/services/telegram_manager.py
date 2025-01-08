import os
import logging
import requests
import asyncio
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

class TelegramManager:
    """
    Kelas untuk mengelola sesi dan interaksi dengan Telegram
    """
    
    def __init__(self):
        # Setup logging
        self.logger = logging.getLogger('TelegramManager')
        self.logger.setLevel(logging.INFO)
        
        # Konfigurasi handler dan formatter
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Konfigurasi base URL dan session
        self.base_url = 'http://localhost:5000'  # URL server backend
        self.session = requests.Session()
        self.phone_number = None
        
        # Load environment variables
        load_dotenv()

        self.selected_session = None
        
        # Pastikan folder sessions ada
        if not os.path.exists('sessions'):
            os.makedirs('sessions')

    async def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Membuat HTTP request dengan async"""
        try:
            loop = asyncio.get_event_loop()
            if method.upper() == 'GET':
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.session.get(f'{self.base_url}/{endpoint}')
                )
            else:  # POST
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.session.post(f'{self.base_url}/{endpoint}', json=data)
                )
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f'Error making request to {endpoint}: {str(e)}')
            raise

    async def create_session(self, phone_number: str) -> None:
        """Membuat sesi baru"""
        try:
            data = await self._make_request('POST', 'create_session', {'phone_number': phone_number})
            if data['status'] == 'success':
                self.phone_number = phone_number
            else:
                raise Exception(data['message'])
        except Exception as e:
            self.logger.error(f'Error creating session: {str(e)}')
            raise

    async def verify_code(self, code: str) -> None:
        """Verifikasi kode"""
        if not self.phone_number:
            raise Exception('Silakan kirim kode verifikasi terlebih dahulu')
            
        try:
            data = await self._make_request('POST', 'verify_code', {
                'phone_number': self.phone_number,
                'code': code
            })
            
            if data['status'] != 'success':
                raise Exception(data['message'])
        except Exception as e:
            self.logger.error(f'Error verifying code: {str(e)}')
            raise

    async def get_chat_history(self) -> List[str]:
        """Mendapatkan riwayat chat"""
        if not self.selected_session:
            raise Exception('Silakan pilih sesi terlebih dahulu')
            
        try:
            data = await self._make_request('POST', 'chat_history', {
                'phone_number': self.selected_session
            })
            
            if data['status'] == 'success':
                return data['chat_history']
            else:
                raise Exception(data['message'])
        except Exception as e:
            self.logger.error(f'Error getting chat history: {str(e)}')
            raise

    async def change_username(self, username: str) -> None:
        """Mengubah username"""
        if not self.selected_session:
            raise Exception('Silakan pilih sesi terlebih dahulu')
            
        try:
            data = await self._make_request('POST', 'change_username', {
                'phone_number': self.selected_session,
                'username': username
            })
            
            if data['status'] != 'success':
                raise Exception(data['message'])
        except Exception as e:
            self.logger.error(f'Error changing username: {str(e)}')
            raise

    async def change_name(self, first_name: str, last_name: Optional[str] = None) -> None:
        """Mengubah nama profil"""
        if not self.selected_session:
            raise Exception('Silakan pilih sesi terlebih dahulu')
            
        try:
            data = await self._make_request('POST', 'change_name', {
                'phone_number': self.selected_session,
                'first_name': first_name,
                'last_name': last_name
            })
            
            if data['status'] != 'success':
                raise Exception(data['message'])
        except Exception as e:
            self.logger.error(f'Error changing name: {str(e)}')
            raise

    async def list_channels(self) -> List[Dict[str, Any]]:
        """Mendapatkan daftar channel dan grup"""
        if not self.selected_session:
            raise Exception('Silakan pilih sesi terlebih dahulu')
            
        try:
            data = await self._make_request('POST', 'list_channels', {
                'phone_number': self.selected_session
            })
            
            if data['status'] == 'success':
                return data['channels']
            else:
                raise Exception(data['message'])
        except Exception as e:
            self.logger.error(f'Error listing channels: {str(e)}')
            raise

    async def leave_all_channels(self) -> None:
        """Keluar dari semua channel dan grup"""
        if not self.selected_session:
            raise Exception('Silakan pilih sesi terlebih dahulu')
            
        try:
            data = await self._make_request('POST', 'leave_all_channels', {
                'phone_number': self.selected_session
            })
            
            if data['status'] != 'success':
                raise Exception(data['message'])
        except Exception as e:
            self.logger.error(f'Error leaving channels: {str(e)}')
            raise

    async def delete_session(self, phone_number: str) -> None:
        """Menghapus sesi"""
        try:
            data = await self._make_request('POST', 'delete_session', {
                'phone_number': phone_number
            })
            
            if data['status'] == 'success':
                if self.selected_session == phone_number:
                    self.selected_session = None
                if self.phone_number == phone_number:
                    self.phone_number = None
            else:
                raise Exception(data['message'])
        except Exception as e:
            self.logger.error(f'Error deleting session: {str(e)}')
            raise 

    async def list_sessions(self) -> List[str]:
        """Mendapatkan daftar sesi yang tersedia"""
        try:
            response = await self._make_request('GET', 'list_sessions')
            if response['status'] == 'success':
                return response['sessions']
            else:
                raise Exception(response['message'])
        except Exception as e:
            self.logger.error(f'Error listing sessions: {str(e)}')
            raise 

    async def select_session(self, phone_number: str) -> None:
        """Memilih sesi yang akan digunakan"""
        try:
            # Cek apakah file sesi ada
            session_file = os.path.join('sessions', f"{phone_number}.session")
            if not os.path.exists(session_file):
                raise Exception(f"Sesi untuk nomor {phone_number} tidak ditemukan")
            
            # Set sesi yang dipilih
            self.selected_session = phone_number
            self.logger.info(f"Selected session: {phone_number}")
        except Exception as e:
            self.logger.error(f"Error selecting session: {str(e)}")
            raise 