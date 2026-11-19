import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class IngenixCredit extends StatelessWidget {
  const IngenixCredit({super.key});

  Future<void> _openContact(BuildContext context) async {
    try {
      final opened = await launchUrl(
        Uri.https('wa.me', '/59176008546', {
          'text': 'Hola, quiero consultar sobre los servicios de INGENIX.',
        }),
        mode: LaunchMode.externalApplication,
        webOnlyWindowName: '_blank',
      );
      if (!opened && context.mounted) _showPhone(context);
    } catch (_) {
      if (context.mounted) _showPhone(context);
    }
  }

  void _showPhone(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Contacto INGENIX: +591 76008546')),
    );
  }

  @override
  Widget build(BuildContext context) => ListTile(
    leading: const Icon(Icons.code),
    title: const Text('Desarrollado por INGENIX'),
    subtitle: const Text('Contacto · +591 76008546'),
    trailing: const Icon(Icons.open_in_new, size: 18),
    onTap: () => _openContact(context),
  );
}
