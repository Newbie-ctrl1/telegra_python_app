import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';
import 'package:logging/logging.dart';

class TelegramManager {
  static final _logger = Logger('TelegramManager');
  static const _baseUrl = 'http://192.168.124.233:5000';
  
  final _storage = const FlutterSecureStorage();
  final _dio = Dio();
  String? _phoneNumber;

  Future<void> initialize() async {
    _logger.info('Initializing TelegramManager');
  }

  Future<List<String>> listSessions() async {
    try {
      _logger.info('Mengambil daftar sesi dari $_baseUrl/list_sessions');
      
      final response = await _dio.get(
        '$_baseUrl/list_sessions',
        options: Options(
          headers: {
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        return List<String>.from(response.data['sessions']);
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error listing sessions: $e');
      rethrow;
    }
  }

  Future<void> selectSession(String phoneNumber) async {
    _phoneNumber = phoneNumber;
    await _storage.write(
      key: 'selected_session',
      value: phoneNumber,
    );
    _logger.info('Selected session: $phoneNumber');
  }

  Future<String?> getSelectedSession() async {
    return await _storage.read(key: 'selected_session');
  }

  Future<void> createSession(String phoneNumber) async {
    await initialize();
    _phoneNumber = phoneNumber;
    
    try {
      _logger.info('Mengirim request ke $_baseUrl/create_session');
      _logger.info('Phone number: $phoneNumber');
      
      final response = await _dio.post(
        '$_baseUrl/create_session',
        data: {
          'phone_number': phoneNumber,
        },
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        _logger.info('Kode verifikasi telah dikirim');
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error creating session: $e');
      rethrow;
    }
  }

  Future<void> verifyCode(String code) async {
    if (_phoneNumber == null) {
      throw Exception('Silakan kirim kode verifikasi terlebih dahulu');
    }

    try {
      _logger.info('Mengirim request ke $_baseUrl/verify_code');
      _logger.info('Phone number: $_phoneNumber');
      _logger.info('Code: $code');

      final response = await _dio.post(
        '$_baseUrl/verify_code',
        data: {
          'phone_number': _phoneNumber,
          'code': code,
        },
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        _logger.info('Sesi berhasil dibuat');
        await _storage.write(
          key: 'session_$_phoneNumber',
          value: _phoneNumber,
        );
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error verifying code: $e');
      rethrow;
    }
  }

  Future<List<String>> getChatHistory() async {
    if (_phoneNumber == null) {
      throw Exception('Silakan buat sesi terlebih dahulu');
    }

    try {
      _logger.info('Mengirim request ke $_baseUrl/chat_history');
      _logger.info('Phone number: $_phoneNumber');

      final response = await _dio.post(
        '$_baseUrl/chat_history',
        data: {
          'phone_number': _phoneNumber,
        },
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        _logger.info('Riwayat chat berhasil diambil');
        return List<String>.from(response.data['chat_history']);
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error getting chat history: $e');
      rethrow;
    }
  }

  Future<void> changeUsername(String username) async {
    if (_phoneNumber == null) {
      throw Exception('Silakan buat sesi terlebih dahulu');
    }

    try {
      _logger.info('Mengirim request ke $_baseUrl/change_username');
      _logger.info('Phone number: $_phoneNumber');
      _logger.info('New username: $username');

      final response = await _dio.post(
        '$_baseUrl/change_username',
        data: {
          'phone_number': _phoneNumber,
          'username': username,
        },
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        _logger.info('Username berhasil diubah');
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error changing username: $e');
      rethrow;
    }
  }

  Future<void> changeName(String firstName, String? lastName) async {
    if (_phoneNumber == null) {
      throw Exception('Silakan buat sesi terlebih dahulu');
    }

    try {
      _logger.info('Mengirim request ke $_baseUrl/change_name');
      _logger.info('Phone number: $_phoneNumber');
      _logger.info('New name: $firstName $lastName');

      final response = await _dio.post(
        '$_baseUrl/change_name',
        data: {
          'phone_number': _phoneNumber,
          'first_name': firstName,
          'last_name': lastName,
        },
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        _logger.info('Nama berhasil diubah');
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error changing name: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> listChannels() async {
    if (_phoneNumber == null) {
      throw Exception('Silakan buat sesi terlebih dahulu');
    }

    try {
      _logger.info('Mengirim request ke $_baseUrl/list_channels');
      _logger.info('Phone number: $_phoneNumber');

      final response = await _dio.post(
        '$_baseUrl/list_channels',
        data: {
          'phone_number': _phoneNumber,
        },
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        _logger.info('Daftar channel berhasil diambil');
        return List<Map<String, dynamic>>.from(response.data['channels']);
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error listing channels: $e');
      rethrow;
    }
  }

  Future<void> leaveAllChannels() async {
    if (_phoneNumber == null) {
      throw Exception('Silakan buat sesi terlebih dahulu');
    }

    try {
      _logger.info('Mengirim request ke $_baseUrl/leave_all_channels');
      _logger.info('Phone number: $_phoneNumber');

      final response = await _dio.post(
        '$_baseUrl/leave_all_channels',
        data: {
          'phone_number': _phoneNumber,
        },
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        _logger.info('Berhasil keluar dari semua channel');
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error leaving channels: $e');
      rethrow;
    }
  }

  Future<void> deleteSession(String phoneNumber) async {
    try {
      _logger.info('Mengirim request ke $_baseUrl/delete_session');
      _logger.info('Phone number: $phoneNumber');

      final response = await _dio.post(
        '$_baseUrl/delete_session',
        data: {
          'phone_number': phoneNumber,
        },
        options: Options(
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          validateStatus: (status) => true,
        ),
      );

      _logger.info('Response status: ${response.statusCode}');
      _logger.info('Response data: ${response.data}');

      if (response.statusCode != 200) {
        throw Exception(response.data['message'] ?? 'Unknown error');
      }

      if (response.data['status'] == 'success') {
        _logger.info('Sesi berhasil dihapus');
        // Hapus sesi dari penyimpanan lokal jika itu sesi yang aktif
        final selectedSession = await getSelectedSession();
        if (selectedSession == phoneNumber) {
          await _storage.delete(key: 'selected_session');
          _phoneNumber = null;
        }
        await _storage.delete(key: 'session_$phoneNumber');
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      _logger.severe('Error deleting session: $e');
      rethrow;
    }
  }
} 