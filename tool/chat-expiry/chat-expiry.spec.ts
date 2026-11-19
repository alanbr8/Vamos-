import { ApiService } from './api.service';
import { DataSource } from 'typeorm';

describe('Vigencia del chat por reserva', () => {
  const booking = { passengerId: 'passenger', driverId: 'driver', status: 'COMPLETED' };
  it('conserva el historial del participante después del cierre', async () => {
    const query = jest.fn().mockResolvedValueOnce([booking]).mockResolvedValueOnce([])
      .mockResolvedValueOnce([{ body: 'Mensaje anterior' }]);
    const service = new ApiService({ transaction: (run: any) => run({ query }) } as unknown as DataSource);
    expect(await service.messages('passenger', 'booking')).toEqual([{ body: 'Mensaje anterior' }]);
  });
  it('rechaza el envío cerrado y no genera notificaciones', async () => {
    const query = jest.fn().mockResolvedValueOnce([booking]).mockResolvedValueOnce([]);
    const service = new ApiService({ transaction: (run: any) => run({ query }) } as unknown as DataSource);
    await expect(service.sendMessage('passenger', 'booking', { body: 'Hola' }))
      .rejects.toThrow('El chat se cerró');
    expect(query).toHaveBeenCalledTimes(2);
    expect(query.mock.calls[1][0]).toContain("clock_timestamp() - interval '1 hour'");
  });
  it('autoriza al participante y notifica cuando la inserción está permitida', async () => {
    const query = jest.fn().mockResolvedValueOnce([{ ...booking, status: 'ACCEPTED' }])
      .mockResolvedValueOnce([{ id: 'message', body: 'Hola' }]).mockResolvedValueOnce([]);
    const service = new ApiService({ transaction: (run: any) => run({ query }) } as unknown as DataSource);
    expect(await service.sendMessage('passenger', 'booking', { body: 'Hola' })).toEqual({ id: 'message', body: 'Hola' });
    expect(query.mock.calls[2][1][0]).toBe('driver');
  });
  it('impide mensajes y consultas de personas ajenas', async () => {
    const query = jest.fn().mockResolvedValue([booking]);
    const service = new ApiService({ query, transaction: (run: any) => run({ query }) } as unknown as DataSource);
    await expect(service.sendMessage('outsider', 'booking', { body: 'Hola' })).rejects.toThrow();
    await expect(service.messages('outsider', 'booking')).rejects.toThrow();
    await expect(service.chatStatus('outsider', 'booking')).rejects.toThrow();
    expect(query).toHaveBeenCalledTimes(3);
  });
  it('devuelve la fecha de cierre y hora del servidor sin datos personales', async () => {
    const query = jest.fn().mockResolvedValue([{ ...booking, canSend: false, closesAt: 'deadline', serverNow: 'now' }]);
    const service = new ApiService({ query } as unknown as DataSource);
    expect(await service.chatStatus('driver', 'booking')).toEqual({ canSend: false, closesAt: 'deadline', serverNow: 'now' });
  });
});
