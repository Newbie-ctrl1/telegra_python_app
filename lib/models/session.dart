class Session {
  final String phoneNumber;
  final String sessionFile;
  final DateTime createdAt;
  bool isActive;

  Session({
    required this.phoneNumber,
    required this.sessionFile,
    required this.createdAt,
    this.isActive = false,
  });

  factory Session.fromJson(Map<String, dynamic> json) {
    return Session(
      phoneNumber: json['phone_number'],
      sessionFile: json['session_file'],
      createdAt: DateTime.parse(json['created_at']),
      isActive: json['is_active'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'phone_number': phoneNumber,
      'session_file': sessionFile,
      'created_at': createdAt.toIso8601String(),
      'is_active': isActive,
    };
  }
} 