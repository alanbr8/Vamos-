import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/routes/app_routes.dart';
import '../../services/api_client.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, required this.bookingId, required this.otherUserName});
  final String bookingId;
  final String otherUserName;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final composer = TextEditingController();
  final scrollController = ScrollController();
  List<Map<String, dynamic>> messages = [];
  bool loading = true;
  bool sending = false;
  bool fetching = false;
  String? error;
  Timer? timer;
  Timer? closeTimer;
  bool canSend = false;
  bool statusKnown = false;

  @override
  void initState() {
    super.initState();
    load();
    timer = Timer.periodic(const Duration(seconds: 10), (_) => load(silent: true));
  }

  @override
  void dispose() {
    timer?.cancel();
    closeTimer?.cancel();
    composer.dispose();
    scrollController.dispose();
    super.dispose();
  }

  Future<void> load({bool silent = false}) async {
    if (fetching) return;
    fetching = true;
    if (!silent) setState(() { loading = true; error = null; });
    try {
      final response = await ApiClient.instance.messages(widget.bookingId);
      if (!mounted) return;
      final next = response.map((item) => Map<String, dynamic>.from(item as Map)).toList();
      final changed = next.length != messages.length ||
          (next.isNotEmpty && messages.isNotEmpty && next.last['id'] != messages.last['id']);
      setState(() { messages = next; error = null; });
      if (changed || !silent) _scrollToBottom();
      await loadChatStatus();
    } on ApiException catch (apiError) {
      if (!silent && mounted) setState(() => error = apiError.message);
    } finally {
      fetching = false;
      if (!silent && mounted) setState(() => loading = false);
    }
  }

  Future<void> loadChatStatus() async {
    try {
      final status = await ApiClient.instance.chatStatus(widget.bookingId);
      if (!mounted) return;
      closeTimer?.cancel();
      setState(() {
        statusKnown = true;
        canSend = status['canSend'] == true;
      });
      final closesAt = DateTime.tryParse(status['closesAt']?.toString() ?? '');
      final serverNow = DateTime.tryParse(status['serverNow']?.toString() ?? '');
      if (canSend && closesAt != null && serverNow != null) {
        final remaining = closesAt.difference(serverNow);
        if (remaining <= Duration.zero) {
          setState(() => canSend = false);
        } else {
          closeTimer = Timer(remaining, () {
            if (mounted) setState(() => canSend = false);
          });
        }
      }
    } on ApiException {
      if (mounted) setState(() { canSend = false; statusKnown = false; });
    }
  }

  Future<void> send() async {
    final body = composer.text.trim();
    if (body.isEmpty || sending || !canSend) return;
    setState(() => sending = true);
    try {
      final response = await ApiClient.instance.sendMessage(widget.bookingId, body);
      if (!mounted) return;
      composer.clear();
      setState(() => messages.add(Map<String, dynamic>.from(response)));
      _scrollToBottom();
    } on ApiException catch (apiError) {
      await loadChatStatus();
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiError.message)));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (scrollController.hasClients) {
        scrollController.animateTo(
          scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 220),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.otherUserName)),
    body: Column(children: [
      Container(
        width: double.infinity,
        color: const Color(0xFFFFF4D6),
        padding: const EdgeInsets.all(10),
        child: const Text('El chat permite coordinar el viaje y se cierra una hora después de finalizarlo. El historial queda disponible.', textAlign: TextAlign.center, style: TextStyle(fontSize: 12)),
      ),
      Expanded(
        child: loading
            ? const Center(child: CircularProgressIndicator())
            : error != null
                ? Center(child: Column(mainAxisSize: MainAxisSize.min, children: [Text(error!), const SizedBox(height: 12), ElevatedButton(onPressed: () => load(), child: const Text('REINTENTAR'))]))
                : RefreshIndicator(
                    onRefresh: load,
                    child: messages.isEmpty
                        ? ListView(controller: scrollController, children: const [SizedBox(height: 180), Center(child: Text('Inicia la conversación para coordinar el encuentro.'))])
                        : ListView.builder(
                            controller: scrollController,
                            padding: const EdgeInsets.all(16),
                            itemCount: messages.length,
                            itemBuilder: (_, index) => _MessageBubble(message: messages[index]),
                          ),
                  ),
      ),
      if (!canSend)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Column(children: [
            Text(statusKnown
                ? 'Chat cerrado. Puedes consultar el historial.'
                : 'Comprobando disponibilidad del chat.'),
            TextButton.icon(
              onPressed: () => Navigator.pushNamed(context, AppRoutes.support),
              icon: const Icon(Icons.support_agent),
              label: const Text('Contactar a soporte'),
            ),
          ]),
        ),
      if (canSend)
      SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(12, 8, 8, 8),
          child: Row(crossAxisAlignment: CrossAxisAlignment.end, children: [
            Expanded(child: TextField(
              controller: composer,
              minLines: 1,
              maxLines: 4,
              maxLength: 1000,
              decoration: const InputDecoration(labelText: 'Mensaje', counterText: ''),
              onSubmitted: (_) => send(),
            )),
            const SizedBox(width: 8),
            IconButton.filled(onPressed: sending ? null : send, icon: sending ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.send)),
          ]),
        ),
      ),
    ]),
  );
}

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({required this.message});
  final Map<String, dynamic> message;

  @override
  Widget build(BuildContext context) {
    final mine = message['isMine'] == true;
    return Align(
      alignment: mine ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 300),
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.fromLTRB(14, 10, 10, 7),
        decoration: BoxDecoration(
          color: mine ? AppColors.green : Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 3)],
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(message['body']?.toString() ?? '', style: TextStyle(color: mine ? Colors.white : Colors.black87)),
          const SizedBox(height: 3),
          Row(mainAxisSize: MainAxisSize.min, children: [
            Text(_time(message['createdAt']), style: TextStyle(fontSize: 10, color: mine ? Colors.white70 : Colors.black54)),
            if (mine) ...[
              const SizedBox(width: 4),
              Icon(message['readAt'] == null ? Icons.done : Icons.done_all, size: 14, color: Colors.white70),
            ],
          ]),
        ]),
      ),
    );
  }
}

String _time(dynamic value) {
  final date = DateTime.tryParse(value?.toString() ?? '')?.toLocal();
  if (date == null) return '';
  return '${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
}
