from pathlib import Path
import shutil
import sys

project = Path(sys.argv[1])
backend = project / "backend/src"
service_file = backend / "api.service.ts"
service = service_file.read_text()
if "async chatStatus(" not in service:
    method = """
  async chatStatus(userId: string, bookingId: string) {
    const [booking] = await this.db.query(
      `SELECT b.passenger_id AS "passengerId",t.driver_id AS "driverId",b.status,
       CASE WHEN b.status='COMPLETED' THEN b.completed_at + interval '1 hour' END AS "closesAt",
       clock_timestamp() AS "serverNow",
       (b.status='ACCEPTED' OR (b.status='COMPLETED'
         AND b.completed_at > clock_timestamp() - interval '1 hour')) AS "canSend"
       FROM bookings b JOIN trips t ON t.id=b.trip_id WHERE b.id=$1`, [bookingId]);
    if (!booking || ![booking.passengerId, booking.driverId].includes(userId) ||
        !['ACCEPTED', 'COMPLETED'].includes(booking.status)) {
      throw new ForbiddenException('El chat está disponible solo para reservas aceptadas');
    }
    return { canSend: booking.canSend === true, closesAt: booking.closesAt,
      serverNow: booking.serverNow };
  }

"""
    service = service.replace("  async messages(userId:", method + "  async messages(userId:", 1)
    old = "VALUES($1,$2,$3,$4)\n         RETURNING id,sender_id"
    new = """SELECT $1,$2,$3,$4 FROM bookings
         WHERE id=$1 AND (status='ACCEPTED' OR (status='COMPLETED'
           AND completed_at > clock_timestamp() - interval '1 hour'))
         RETURNING id,sender_id"""
    if service.count(old) != 1:
        raise SystemExit("No se encontró el envío de mensajes esperado.")
    service = service.replace(old, new)
    anchor = "      await manager.query(\n        `INSERT INTO notifications(user_id,type,title,body,data)\n         VALUES($1,'CHAT_MESSAGE'"
    guard = """      if (!message) {
        throw new ForbiddenException('El chat se cerró una hora después de finalizar el viaje. Puedes consultar el historial y contactar a soporte.');
      }
"""
    if anchor not in service:
        raise SystemExit("No se encontró la notificación del chat.")
    service = service.replace(anchor, guard + anchor)
    service_file.write_text(service)
controller_file = backend / "api.controller.ts"
controller = controller_file.read_text()
if "@Get('bookings/:id/chat-status')" not in controller:
    anchor = "  @UseGuards(JwtAuthGuard) @Get('bookings/:id/messages')"
    if anchor not in controller:
        raise SystemExit("No se encontró la ruta de mensajes.")
    controller = controller.replace(anchor, "  @UseGuards(JwtAuthGuard) @Get('bookings/:id/chat-status') chatStatus(@Req() req: AuthRequest, @Param('id') id: string) { return this.api.chatStatus(req.userId, id); }\n" + anchor)
    controller_file.write_text(controller)
client_file = project / "vamos_app/lib/services/api_client.dart"
client = client_file.read_text()
if "chatStatus(String bookingId)" not in client:
    anchor = "  Future<List<dynamic>> messages(String bookingId)"
    if anchor not in client:
        raise SystemExit("No se encontró el cliente de mensajes.")
    client = client.replace(anchor, "  Future<Map<String, dynamic>> chatStatus(String bookingId) =>\n      _request('GET', '/bookings/$bookingId/chat-status');\n\n" + anchor)
    client_file.write_text(client)
shutil.copyfile(Path(__file__).with_name("chat_screen.dart"), project / "vamos_app/lib/screens/chat/chat_screen.dart")
shutil.copyfile(Path(__file__).with_name("chat-expiry.spec.ts"), backend / "chat-expiry.spec.ts")
