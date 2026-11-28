import 'package:flutter/foundation.dart';

class AppConfig {
  static const _configuredUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://vamos-api.onrender.com/api/v1',
  );
  static String get apiBaseUrl {
    final uri = Uri.parse(_configuredUrl);
    if (kReleaseMode && (uri.scheme != 'https' || uri.host.isEmpty)) {
      throw StateError('La versión de producción requiere una API HTTPS.');
    }
    return _configuredUrl;
  }
}
