import { BadRequestException, NotFoundException } from '@nestjs/common';
import { AdminService } from './admin.service';
import { AdminController } from './admin.controller';
import { AdminGuard } from './admin.guard';
import { JwtAuthGuard } from './jwt-auth.guard';

describe('Administración de usuarios', () => {
  const previous={id:'user',firstName:'Maria',lastName:'Perez'};
  it('corrige nombres y audita el antes y después dentro de la transacción', async()=>{
    const updated={...previous,firstName:'María',lastName:'Pérez López'};
    const query=jest.fn().mockResolvedValueOnce([previous]).mockResolvedValueOnce([updated]).mockResolvedValueOnce([]);
    const service=new AdminService({transaction:async(fn:Function)=>fn({query})} as never);
    await expect(service.updateUserName('admin','user',{firstName:' María ',lastName:' Pérez López '})).resolves.toEqual(updated);
    expect(query.mock.calls[0][0]).toContain('FOR UPDATE');
    expect(query.mock.calls[1][1]).toEqual(['user','María','Pérez López']);
    expect(query.mock.calls[2][1]).toEqual(['admin','USER_NAME_CHANGED','USER','user',previous,updated]);
  });
  it.each([' ', 'A', 'x'.repeat(81)])('rechaza nombres inválidos',async firstName=>{
    const transaction=jest.fn();
    const service=new AdminService({transaction} as never);
    await expect(service.updateUserName('admin','user',{firstName,lastName:'Perez'})).rejects.toBeInstanceOf(BadRequestException);
    expect(transaction).not.toHaveBeenCalled();
  });
  it('no escribe ni audita si no hubo cambios',async()=>{
    const query=jest.fn().mockResolvedValue([previous]);
    const service=new AdminService({transaction:async(fn:Function)=>fn({query})} as never);
    await service.updateUserName('admin','user',previous);
    expect(query).toHaveBeenCalledTimes(1);
  });
  it('no corrige usuarios inexistentes',async()=>{
    const query=jest.fn().mockResolvedValue([]);
    const service=new AdminService({transaction:async(fn:Function)=>fn({query})} as never);
    await expect(service.updateUserName('admin','missing',previous)).rejects.toBeInstanceOf(NotFoundException);
    expect(query).toHaveBeenCalledTimes(1);
  });
  it('mantiene autenticación y permisos de administrador en las nuevas rutas',()=>{
    expect(Reflect.getMetadata('__guards__',AdminController)).toEqual([JwtAuthGuard,AdminGuard]);
  });
});
