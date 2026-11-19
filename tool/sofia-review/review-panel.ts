import type { INestApplication } from '@nestjs/common';
import type { Request, Response } from 'express';
import { createHash, timingSafeEqual } from 'node:crypto';
import { resolve } from 'node:path';

export function mountReviewPanel(app: INestApplication) {
  app.use('/admin/revision-sofia', (req: Request, res: Response) => {
    res.set({
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Referrer-Policy': 'no-referrer',
      'Content-Security-Policy': "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
    });
    const hash = process.env.SOFIA_REVIEW_TOKEN_SHA256 ?? '';
    const expiry = Date.parse(process.env.SOFIA_REVIEW_EXPIRES_AT ?? '');
    if (!/^[a-f0-9]{64}$/.test(hash) || !Number.isFinite(expiry) || Date.now() >= expiry) {
      return res.status(404).send('Acceso de revisión no disponible.');
    }
    if (req.method !== 'GET') return res.status(405).end();

    const root = resolve(__dirname, '../../admin');
    if (req.path === '/') return res.sendFile('revision-sofia.html', { root });
    if (req.path === '/styles.css') return res.sendFile('styles.css', { root });
    if (req.path === '/consulta.js') return res.sendFile('revision-sofia.js', { root });
    if (req.path !== '/datos') return res.status(404).end();

    const token = /^Bearer ([a-f0-9]{64})$/.exec(req.get('authorization') ?? '')?.[1];
    if (!token || !timingSafeEqual(createHash('sha256').update(token).digest(), Buffer.from(hash, 'hex'))) {
      return res.status(401).end();
    }

    const readOnly = 'Solo consulta';
    const row = (status: string, ...cells: string[]) => ({ status, cells });
    return res.json({
      expiresAt: new Date(expiry).toISOString(),
      metrics: [['Usuarios', 3], ['Viajes publicados', 2], ['Vehículos pendientes', 1],
        ['Incidentes abiertos', 1], ['Comunidades por aprobar', 1], ['Ingresos a comunidades', 1]],
      tables: {
        documentRows: [
          row('PENDING', 'Ana Prueba · ana@example.invalid', 'Carnet · DEMO-001', 'Sin vencimiento', 'Pendiente', readOnly),
          row('APPROVED', 'Luis Ejemplo · luis@example.invalid', 'Licencia · DEMO-002', '31/12/2027', 'Aprobado', readOnly),
        ],
        profilePhotoRows: [
          row('PENDING', 'Ana Prueba', 'Pendiente', '19/11/2026', 'Pendiente', readOnly),
          row('APPROVED', 'Luis Ejemplo', 'Verificada', '18/11/2026', 'Aprobada', readOnly),
        ],
        vehicleRows: [
          row('PENDING', 'Toyota Corolla · 2022 · Blanco · 4 asientos', 'Luis Ejemplo · luis@example.invalid', 'DEMO-01', 'Pendiente', readOnly),
          row('VERIFIED', 'Suzuki Swift · 2023 · Gris · 3 asientos', 'Eva Prueba · eva@example.invalid', 'DEMO-02', 'Aprobado', readOnly),
        ],
        incidentRows: [
          row('RECEIVED', 'Retraso · Ejemplo de reporte de llegada', 'Ana Prueba / Luis Ejemplo', '19/11/2026', 'Recibido', readOnly),
          row('RESOLVED', 'Consulta · Ejemplo de respuesta administrativa', 'Eva Prueba', '18/11/2026', 'Resuelto', readOnly),
        ],
        userRows: [
          row('ACTIVE', 'Ana Prueba · ana@example.invalid', 'Usuario', '1', 'Activo', readOnly),
          row('ACTIVE', 'Luis Ejemplo · luis@example.invalid', 'Usuario', '2', 'Activo', readOnly),
          row('SUSPENDED', 'Eva Prueba · eva@example.invalid', 'Usuario', '1', 'Suspendido', readOnly),
        ],
        communityCreationRows: [
          row('PENDING', 'Sofía · Comunidad de prueba', 'Responsable ficticio', 'Piloto de movilidad compartida', 'Pendiente', readOnly),
        ],
        communityRows: [
          row('PENDING', 'Sofía · Comunidad de prueba', 'Ana Prueba', 'Sede y cargo de ejemplo', 'Pendiente', readOnly),
          row('APPROVED', 'Sofía · Comunidad de prueba', 'Luis Ejemplo', 'Sede y cargo de ejemplo', 'Aprobado', readOnly),
        ],
        ledgerRows: [
          row('COMPLETED', 'Zona Norte → Sede de prueba', 'Luis Ejemplo / Ana Prueba · 1 asiento', 'Toyota Corolla · DEMO-01', '19/11/2026 · 07:30', 'Finalizado'),
          row('ACCEPTED', 'Sede de prueba → Zona Centro', 'Eva Prueba / Luis Ejemplo · 1 asiento', 'Suzuki Swift · DEMO-02', '19/11/2026 · 17:30', 'Aceptado'),
        ],
        auditRows: [
          row('APPROVED', 'Revisión de documento', 'Documento DEMO-002', 'Operador ficticio', '18/11/2026', 'Pendiente → Aprobado'),
          row('SUSPENDED', 'Estado de usuario', 'Eva Prueba', 'Operador ficticio', '18/11/2026', 'Activo → Suspendido'),
        ],
      },
    });
  });
}
