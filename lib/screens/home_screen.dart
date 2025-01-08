import 'package:flutter/material.dart';
import '../services/telegram_manager.dart';
import 'package:flutter/services.dart';
import 'dart:io';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TelegramManager _telegramManager = TelegramManager();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _codeController = TextEditingController();
  final _storage = const FlutterSecureStorage();
  List<String> _chatHistory = [];
  bool _isLoading = false;

  // Tambahkan color scheme yang modern
  final _colorScheme = {
    'primary': const Color(0xFF6C63FF),      // Ungu modern
    'secondary': const Color(0xFF00BFA6),    // Tosca
    'accent': const Color(0xFFFF6584),       // Pink
    'background': const Color(0xFFF8F9FE),   // Abu-abu sangat muda
    'card': Colors.white,
    'text': const Color(0xFF2D3748),         // Abu-abu gelap
  };

  @override
  void initState() {
    super.initState();
  }

  void _showSnackBar(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
    );
  }

  void _setLoading(bool value) {
    if (!mounted) return;
    setState(() => _isLoading = value);
  }

  Future<void> _showSessionDialog() async {
    _setLoading(true);
    try {
      final sessions = await _telegramManager.listSessions();
      if (!mounted) return;
      
      final selectedSession = await showDialog<String>(
        context: context,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Column(
            children: [
              Icon(Icons.history, size: 48, color: Colors.blue),
              SizedBox(height: 8),
              Text('Pilih Sesi untuk Lihat Chat'),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: sessions.map((session) => 
                Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: ListTile(
                    title: Text(
                      session,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: const Text('Ketuk untuk melihat riwayat'),
                    leading: const CircleAvatar(
                      child: Icon(Icons.person),
                    ),
                    trailing: const Icon(Icons.chat_bubble_outline),
                    onTap: () => Navigator.pop(context, session),
                  ),
                ),
              ).toList(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Tutup'),
            ),
          ],
        ),
      );

      if (selectedSession != null && mounted) {
        await _telegramManager.selectSession(selectedSession);
        await _showChatHistory(selectedSession);
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Error: $e');
      }
    } finally {
      if (mounted) {
        _setLoading(false);
      }
    }
  }

  Future<void> _createSession() async {
    if (_phoneController.text.isEmpty) {
      _showSnackBar('Masukkan nomor telepon');
      return;
    }

    _setLoading(true);
    try {
      await _telegramManager.createSession(_phoneController.text);
      _showSnackBar('Kode verifikasi telah dikirim');
    } catch (e) {
      _showSnackBar('Error: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> _verifyCode() async {
    if (_codeController.text.isEmpty) {
      _showSnackBar('Masukkan kode verifikasi');
      return;
    }

    _setLoading(true);
    try {
      await _telegramManager.verifyCode(_codeController.text);
      _showSnackBar('Sesi berhasil dibuat');
      _codeController.clear();
    } catch (e) {
      _showSnackBar('Error: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> _showChatHistory(String session) async {
    _setLoading(true);
    try {
      final chatHistory = await _telegramManager.getChatHistory();
      if (!mounted) return;
      setState(() => _chatHistory = chatHistory);
      
      if (!mounted) return;
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: Column(
            children: [
              const Icon(Icons.chat_bubble, size: 48, color: Colors.blue),
              const SizedBox(height: 8),
              const Text('Riwayat Chat'),
              Text(
                'Sesi: $session',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: _chatHistory.map((message) => 
                Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Text(message),
                  ),
                ),
              ).toList(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Tutup'),
            ),
          ],
        ),
      );
    } catch (e) {
      _showSnackBar('Error: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> _showChangeUsernameDialog(String session) async {
    final usernameController = TextEditingController();
    
    final username = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: const Column(
          children: [
            Icon(Icons.alternate_email, size: 48, color: Colors.blue),
            SizedBox(height: 8),
            Text('Ubah Username'),
          ],
        ),
        content: TextField(
          controller: usernameController,
          decoration: InputDecoration(
            labelText: 'Username Baru',
            hintText: 'Masukkan username tanpa @',
            prefixIcon: const Icon(Icons.alternate_email),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(15),
            ),
            filled: true,
            fillColor: Colors.grey[100],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, usernameController.text),
            style: ElevatedButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
            ),
            child: const Text('Simpan'),
          ),
        ],
      ),
    );

    if (username != null && mounted) {
      _setLoading(true);
      try {
        await _telegramManager.changeUsername(username);
        _showSnackBar('Username berhasil diubah');
      } catch (e) {
        _showSnackBar('Error: $e');
      } finally {
        _setLoading(false);
      }
    }
  }

  Future<void> _showChangeNameDialog(String session) async {
    final firstNameController = TextEditingController();
    final lastNameController = TextEditingController();
    
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: const Column(
          children: [
            Icon(Icons.person_outline, size: 48, color: Colors.blue),
            SizedBox(height: 8),
            Text('Ubah Nama'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: firstNameController,
              decoration: InputDecoration(
                labelText: 'Nama Depan',
                hintText: 'Masukkan nama depan',
                prefixIcon: const Icon(Icons.person),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                filled: true,
                fillColor: Colors.grey[100],
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: lastNameController,
              decoration: InputDecoration(
                labelText: 'Nama Belakang (Opsional)',
                hintText: 'Masukkan nama belakang',
                prefixIcon: const Icon(Icons.person_outline),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                filled: true,
                fillColor: Colors.grey[100],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, {
              'firstName': firstNameController.text,
              'lastName': lastNameController.text,
            }),
            style: ElevatedButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
            ),
            child: const Text('Simpan'),
          ),
        ],
      ),
    );

    if (result != null && mounted) {
      _setLoading(true);
      try {
        await _telegramManager.changeName(
          result['firstName']!,
          result['lastName']!.isEmpty ? null : result['lastName'],
        );
        _showSnackBar('Nama berhasil diubah');
      } catch (e) {
        _showSnackBar('Error: $e');
      } finally {
        _setLoading(false);
      }
    }
  }

  Future<void> _showFeatureDialog() async {
    _setLoading(true);
    try {
      final sessions = await _telegramManager.listSessions();
      if (!mounted) return;
      
      final selectedSession = await showDialog<String>(
        context: context,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Column(
            children: [
              Icon(Icons.settings, size: 48, color: Colors.blue),
              SizedBox(height: 8),
              Text('Pilih Sesi'),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: sessions.map((session) => 
                Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: ListTile(
                    title: Text(
                      session,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: const Text('Ketuk untuk memilih'),
                    leading: const CircleAvatar(
                      child: Icon(Icons.person),
                    ),
                    onTap: () => Navigator.pop(context, session),
                  ),
                ),
              ).toList(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Tutup'),
            ),
          ],
        ),
      );

      if (selectedSession != null && mounted) {
        await _telegramManager.selectSession(selectedSession);
        
        if (!mounted) return;
        final feature = await showDialog<String>(
          context: context,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            title: const Column(
              children: [
                Icon(Icons.settings, size: 48, color: Colors.blue),
                SizedBox(height: 8),
                Text('Pilih Fitur'),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ListTile(
                  leading: const CircleAvatar(
                    child: Icon(Icons.alternate_email),
                  ),
                  title: const Text('Ubah Username'),
                  onTap: () => Navigator.pop(context, 'username'),
                ),
                ListTile(
                  leading: const CircleAvatar(
                    child: Icon(Icons.person),
                  ),
                  title: const Text('Ubah Nama'),
                  onTap: () => Navigator.pop(context, 'name'),
                ),
              ],
            ),
          ),
        );

        if (feature != null && mounted) {
          if (feature == 'username') {
            await _showChangeUsernameDialog(selectedSession);
          } else if (feature == 'name') {
            await _showChangeNameDialog(selectedSession);
          }
        }
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Error: $e');
      }
    } finally {
      if (mounted) {
        _setLoading(false);
      }
    }
  }

  Future<void> _showChannelDialog() async {
    _setLoading(true);
    try {
      final sessions = await _telegramManager.listSessions();
      if (!mounted) return;
      
      final selectedSession = await showDialog<String>(
        context: context,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Column(
            children: [
              Icon(Icons.groups, size: 48, color: Colors.blue),
              SizedBox(height: 8),
              Text('Pilih Sesi'),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: sessions.map((session) => 
                Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: ListTile(
                    title: Text(
                      session,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: const Text('Ketuk untuk memilih'),
                    leading: const CircleAvatar(
                      child: Icon(Icons.person),
                    ),
                    onTap: () => Navigator.pop(context, session),
                  ),
                ),
              ).toList(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Tutup'),
            ),
          ],
        ),
      );

      if (selectedSession != null && mounted) {
        await _telegramManager.selectSession(selectedSession);
        
        if (!mounted) return;
        final action = await showDialog<String>(
          context: context,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            title: const Column(
              children: [
                Icon(Icons.groups, size: 48, color: Colors.blue),
                SizedBox(height: 8),
                Text('Pilih Aksi'),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ListTile(
                  leading: const CircleAvatar(
                    child: Icon(Icons.list),
                  ),
                  title: const Text('Lihat Channel & Grup'),
                  onTap: () => Navigator.pop(context, 'list'),
                ),
                ListTile(
                  leading: const CircleAvatar(
                    child: Icon(Icons.exit_to_app),
                  ),
                  title: const Text('Keluar dari Semua'),
                  onTap: () => Navigator.pop(context, 'leave'),
                ),
              ],
            ),
          ),
        );

        if (action != null && mounted) {
          if (action == 'list') {
            await _showChannelList();
          } else if (action == 'leave') {
            await _leaveAllChannels();
          }
        }
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Error: $e');
      }
    } finally {
      if (mounted) {
        _setLoading(false);
      }
    }
  }

  Future<void> _showChannelList() async {
    _setLoading(true);
    try {
      final channels = await _telegramManager.listChannels();
      if (!mounted) return;
      
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Column(
            children: [
              Icon(Icons.groups, size: 48, color: Colors.blue),
              SizedBox(height: 8),
              Text('Channel & Grup'),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: channels.map((channel) => 
                Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: ListTile(
                    title: Text(
                      channel['title'],
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      'ID: ${channel['id']}\nTipe: ${channel['type']}',
                    ),
                    leading: CircleAvatar(
                      child: Icon(
                        channel['type'] == 'channel' 
                          ? Icons.campaign 
                          : Icons.group
                      ),
                    ),
                  ),
                ),
              ).toList(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Tutup'),
            ),
          ],
        ),
      );
    } catch (e) {
      _showSnackBar('Error: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> _leaveAllChannels() async {
    _setLoading(true);
    try {
      await _telegramManager.leaveAllChannels();
      _showSnackBar('Berhasil keluar dari semua channel dan grup');
    } catch (e) {
      _showSnackBar('Error: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> _showDeleteSessionDialog() async {
    _setLoading(true);
    try {
      final sessions = await _telegramManager.listSessions();
      if (!mounted) return;
      
      final selectedSession = await showDialog<String>(
        context: context,
        builder: (context) => AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Column(
            children: [
              Icon(Icons.delete_forever, size: 48, color: Colors.red),
              SizedBox(height: 8),
              Text('Hapus Sesi'),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Peringatan: Menghapus sesi akan menghapus semua data terkait, termasuk riwayat chat.',
                  style: TextStyle(color: Colors.red),
                ),
                const SizedBox(height: 16),
                ...sessions.map((session) => 
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: ListTile(
                      title: Text(
                        session,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: const Text('Ketuk untuk menghapus'),
                      leading: const CircleAvatar(
                        backgroundColor: Colors.red,
                        child: Icon(Icons.delete_outline, color: Colors.white),
                      ),
                      onTap: () => Navigator.pop(context, session),
                    ),
                  ),
                ).toList(),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Batal'),
            ),
          ],
        ),
      );

      if (selectedSession != null && mounted) {
        final confirm = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            title: const Column(
              children: [
                Icon(Icons.warning, size: 48, color: Colors.orange),
                SizedBox(height: 8),
                Text('Konfirmasi'),
              ],
            ),
            content: Text(
              'Anda yakin ingin menghapus sesi untuk nomor $selectedSession?\n\n'
              'Semua data terkait akan dihapus dan tidak dapat dikembalikan.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Batal'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
                child: const Text('Hapus'),
              ),
            ],
          ),
        );

        if (confirm == true && mounted) {
          await _telegramManager.deleteSession(selectedSession);
          _showSnackBar('Sesi berhasil dihapus');
        }
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Error: $e');
      }
    } finally {
      if (mounted) {
        _setLoading(false);
      }
    }
  }

  Future<void> _showExitDialog() async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: _colorScheme['card'],
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: Column(
          children: [
            Icon(Icons.exit_to_app, size: 48, color: _colorScheme['accent']),
            const SizedBox(height: 8),
            Text(
              'Keluar Aplikasi',
              style: TextStyle(color: _colorScheme['text']),
            ),
          ],
        ),
        content: Text(
          'Anda yakin ingin keluar dari aplikasi?',
          style: TextStyle(color: _colorScheme['text']),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(
              'Batal',
              style: TextStyle(color: _colorScheme['text']),
            ),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: _colorScheme['accent'],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
            ),
            child: const Text('Keluar'),
          ),
        ],
      ),
    );

    if (result == true) {
      if (mounted) {
        SystemNavigator.pop();
      }
    }
  }

  Future<void> _showApiSettingsDialog() async {
    final apiIdController = TextEditingController();
    final apiHashController = TextEditingController();
    
    // Baca nilai API credentials yang ada
    final apiId = await _storage.read(key: 'API_ID');
    final apiHash = await _storage.read(key: 'API_HASH');
    
    apiIdController.text = apiId ?? '';
    apiHashController.text = apiHash ?? '';

    if (!mounted) return;
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: _colorScheme['card'],
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: Column(
          children: [
            Icon(Icons.api, size: 48, color: _colorScheme['primary']),
            const SizedBox(height: 8),
            Text(
              'API Settings',
              style: TextStyle(color: _colorScheme['text']),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: apiIdController,
              decoration: InputDecoration(
                labelText: 'API ID',
                hintText: 'Masukkan API ID',
                prefixIcon: Icon(Icons.numbers, color: _colorScheme['primary']),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                  borderSide: BorderSide(color: _colorScheme['primary']!.withAlpha(77)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                  borderSide: BorderSide(color: _colorScheme['primary']!),
                ),
                filled: true,
                fillColor: _colorScheme['background'],
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: apiHashController,
              decoration: InputDecoration(
                labelText: 'API Hash',
                hintText: 'Masukkan API Hash',
                prefixIcon: Icon(Icons.key, color: _colorScheme['primary']),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                  borderSide: BorderSide(color: _colorScheme['primary']!.withAlpha(77)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                  borderSide: BorderSide(color: _colorScheme['primary']!),
                ),
                filled: true,
                fillColor: _colorScheme['background'],
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Dapatkan API credentials di my.telegram.org',
              style: TextStyle(
                fontSize: 12,
                color: _colorScheme['text']!.withAlpha(179),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Batal',
              style: TextStyle(color: _colorScheme['text']),
            ),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, {
              'apiId': apiIdController.text,
              'apiHash': apiHashController.text,
            }),
            style: ElevatedButton.styleFrom(
              backgroundColor: _colorScheme['primary'],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
            ),
            child: const Text('Simpan'),
          ),
        ],
      ),
    );

    if (result != null && mounted) {
      _setLoading(true);
      try {
        // Simpan API credentials
        await _storage.write(key: 'API_ID', value: result['apiId']);
        await _storage.write(key: 'API_HASH', value: result['apiHash']);
        
        // Update file .env
        final envContent = '''API_ID=${result['apiId']}
API_HASH=${result['apiHash']}''';
        
        await File('.env').writeAsString(envContent);
        
        _showSnackBar('API credentials berhasil disimpan');
      } catch (e) {
        _showSnackBar('Error: $e');
      } finally {
        _setLoading(false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _colorScheme['background'],
      appBar: AppBar(
        title: Text(
          'Telegram Manager',
          style: TextStyle(
            color: _colorScheme['text'],
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
        elevation: 0,
        backgroundColor: _colorScheme['background'],
        actions: [
          IconButton(
            tooltip: 'API Settings',
            icon: Icon(Icons.api, color: _colorScheme['primary']),
            onPressed: _showApiSettingsDialog,
          ),
          IconButton(
            tooltip: 'Keluar',
            icon: Icon(Icons.exit_to_app, color: _colorScheme['accent']),
            onPressed: _showExitDialog,
          ),
        ],
      ),
      body: Stack(
        children: [
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  _colorScheme['primary']!.withAlpha(13),
                  _colorScheme['secondary']!.withAlpha(13),
                ],
              ),
            ),
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Card untuk membuat sesi
                  Card(
                    elevation: 2,
                    color: _colorScheme['card'],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          Text(
                            'Buat Sesi Baru',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: _colorScheme['text'],
                            ),
                          ),
                          const SizedBox(height: 16),
                          TextField(
                            controller: _phoneController,
                            decoration: InputDecoration(
                              labelText: 'Nomor Telepon',
                              hintText: 'Contoh: +628123456789',
                              prefixIcon: Icon(Icons.phone, color: _colorScheme['primary']),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(15),
                              ),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(15),
                                borderSide: BorderSide(color: _colorScheme['primary']!.withAlpha(77)),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(15),
                                borderSide: BorderSide(color: _colorScheme['primary']!),
                              ),
                              filled: true,
                              fillColor: _colorScheme['background'],
                            ),
                            keyboardType: TextInputType.phone,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            onPressed: _isLoading ? null : _createSession,
                            icon: const Icon(Icons.add),
                            label: const Text('Buat Sesi'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _colorScheme['primary'],
                              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(15),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Card untuk verifikasi kode
                  Card(
                    elevation: 2,
                    color: _colorScheme['card'],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          Text(
                            'Verifikasi Kode',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: _colorScheme['text'],
                            ),
                          ),
                          const SizedBox(height: 16),
                          TextField(
                            controller: _codeController,
                            decoration: InputDecoration(
                              labelText: 'Kode Verifikasi',
                              hintText: 'Masukkan kode yang dikirim via Telegram',
                              prefixIcon: Icon(Icons.lock, color: _colorScheme['primary']),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(15),
                              ),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(15),
                                borderSide: BorderSide(color: _colorScheme['primary']!.withAlpha(77)),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(15),
                                borderSide: BorderSide(color: _colorScheme['primary']!),
                              ),
                              filled: true,
                              fillColor: _colorScheme['background'],
                            ),
                            keyboardType: TextInputType.number,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            onPressed: _isLoading ? null : _verifyCode,
                            icon: const Icon(Icons.check),
                            label: const Text('Verifikasi Kode'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _colorScheme['secondary'],
                              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(15),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  // Grid fitur-fitur
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    children: [
                      _buildFeatureButton(
                        icon: Icons.history,
                        label: 'Riwayat Chat',
                        onPressed: _isLoading ? null : _showSessionDialog,
                        description: 'Lihat riwayat chat Telegram',
                        color: _colorScheme['primary']!,
                      ),
                      _buildFeatureButton(
                        icon: Icons.manage_accounts,
                        label: 'Pengaturan Profil',
                        onPressed: _isLoading ? null : _showFeatureDialog,
                        description: 'Ubah username dan nama',
                        color: _colorScheme['secondary']!,
                      ),
                      _buildFeatureButton(
                        icon: Icons.groups,
                        label: 'Kelola Channel',
                        onPressed: _isLoading ? null : _showChannelDialog,
                        description: 'Lihat dan keluar dari channel',
                        color: _colorScheme['accent']!,
                      ),
                      _buildFeatureButton(
                        icon: Icons.delete_forever,
                        label: 'Hapus Sesi',
                        onPressed: _isLoading ? null : _showDeleteSessionDialog,
                        description: 'Hapus sesi Telegram',
                        color: Colors.red,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          if (_isLoading)
            Container(
              color: Colors.black54,
              child: Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(_colorScheme['primary']!),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildFeatureButton({
    required IconData icon,
    required String label,
    required String description,
    required VoidCallback? onPressed,
    required Color color,
  }) {
    return Card(
      elevation: 2,
      color: _colorScheme['card'],
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.all(16.0),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                color.withAlpha(26),
                color.withAlpha(13),
              ],
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 48, color: color),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: _colorScheme['text'],
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(
                  fontSize: 12,
                  color: _colorScheme['text']!.withAlpha(179),
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _codeController.dispose();
    super.dispose();
  }
} 