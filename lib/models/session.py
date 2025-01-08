from datetime import datetime
from typing import Dict, Any

class Session:
    def __init__(self, phone_number: str, session_file: str, created_at: datetime, is_active: bool = False):
        """
        Inisialisasi objek Session
        
        Args:
            phone_number (str): Nomor telepon pengguna
            session_file (str): Path file sesi
            created_at (datetime): Waktu pembuatan sesi
            is_active (bool, optional): Status aktif sesi. Defaults ke False
        """
        self.phone_number = phone_number
        self.session_file = session_file
        self.created_at = created_at
        self.is_active = is_active

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'Session':
        """
        Membuat instance Session dari data JSON
        
        Args:
            json_data (Dict[str, Any]): Data JSON yang berisi informasi sesi
            
        Returns:
            Session: Instance baru dari kelas Session
        """
        return cls(
            phone_number=json_data['phone_number'],
            session_file=json_data['session_file'],
            created_at=datetime.fromisoformat(json_data['created_at']),
            is_active=json_data.get('is_active', False)
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Mengkonversi objek Session ke format JSON
        
        Returns:
            Dict[str, Any]: Representasi JSON dari objek Session
        """
        return {
            'phone_number': self.phone_number,
            'session_file': self.session_file,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        } 