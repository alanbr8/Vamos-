import { validate } from 'class-validator';
import { requireWoman, requireWomenBooking, womenOnly } from './women-policy';
import { ApiService } from './api.service';
import { ProfileGenderDto, SearchTripsDto } from './dtos';

describe('Solo mujeres',()=>{
  it.each(['MALE',null,undefined])('excluye un perfil no registrado como Mujer: %s',gender=>{
    expect(()=>requireWoman(gender)).toThrow();
    expect(()=>requireWomenBooking({womenOnly:true,driverGender:'FEMALE'},gender,1)).toThrow();
  });
  it('solo permite una pasajera por cuenta y una conductora mujer',()=>{
    expect(()=>requireWomenBooking({womenOnly:true,driverGender:'FEMALE'},'FEMALE',1)).not.toThrow();
    expect(()=>requireWomenBooking({womenOnly:true,driverGender:'MALE'},'FEMALE',1)).toThrow();
    expect(()=>requireWomenBooking({womenOnly:true,driverGender:'FEMALE'},'FEMALE',2)).toThrow('propio asiento');
    expect(()=>requireWomenBooking({womenOnly:false},'MALE',3)).not.toThrow();
  });
  it.each(['true','false',1,null])('no interpreta valores falsos o ambiguos como un booleano: %s',value=>{
    expect(()=>womenOnly({womenOnly:value})).toThrow();
  });
  it('mantiene los viajes normales para cuentas antiguas',()=>{
    expect(womenOnly({})).toBe(false);expect(womenOnly({womenOnly:false})).toBe(false);
  });
  it('rechaza el filtro antes de consultar rutas si la persona no es mujer',async()=>{
    const query=jest.fn().mockResolvedValue([{gender:'MALE'}]);
    const service=new ApiService({query} as never);
    await expect(service.search('user',{womenOnly:true} as any)).rejects.toThrow('Solo mujeres');
    expect(query).toHaveBeenCalledTimes(1);
  });
  it('completa el dato de una cuenta antigua dentro de una transacción',async()=>{
    const query=jest.fn().mockResolvedValueOnce([{gender:null}]).mockResolvedValueOnce([{gender:'FEMALE'}]);
    const service=new ApiService({transaction:async(fn:Function)=>fn({query})} as never);
    await expect(service.setGender('user','FEMALE')).resolves.toEqual({gender:'FEMALE'});
    expect(query.mock.calls[0][0]).toContain('FOR UPDATE');
  });
  it('requiere soporte para cambiar un dato ya declarado',async()=>{
    const query=jest.fn().mockResolvedValue([{gender:'MALE'}]);
    const service=new ApiService({transaction:async(fn:Function)=>fn({query})} as never);
    await expect(service.setGender('user','FEMALE')).rejects.toThrow('soporte');
    expect(query).toHaveBeenCalledTimes(1);
  });
  it('valida el género y el booleano recibido por la API',async()=>{
    expect((await validate(Object.assign(new ProfileGenderDto(),{gender:'inventado'}))).length).toBeGreaterThan(0);
    const errors=await validate(Object.assign(new SearchTripsDto(),{womenOnly:'false'}));
    expect(errors.some(e=>e.property==='womenOnly')).toBe(true);
  });
});


describe('Controles de Solo mujeres en operaciones directas',()=>{
  it('impide publicar un viaje exclusivo a un hombre o perfil sin completar',async()=>{
    const query=jest.fn().mockResolvedValue([{id:'driver',gender:'MALE'}]);
    const service=new ApiService({transaction:async(fn:Function)=>fn({query})} as never);
    await expect(service.createTrip('driver',{
      originLat:1,originLng:1,destinationLat:2,destinationLng:2,route:[[1,1],[2,2]],
      departureAt:new Date(Date.now()+3600000).toISOString(),preferences:{womenOnly:true}
    } as any)).rejects.toThrow('Solo mujeres');
    expect(query).toHaveBeenCalledTimes(1);
  });
  it('bloquea una reserva directa de un hombre aunque omita el filtro de búsqueda',async()=>{
    const query=jest.fn().mockResolvedValueOnce([])
      .mockResolvedValueOnce([{driverId:'driver',availableSeats:3}])
      .mockResolvedValueOnce([{womenOnly:true,driverGender:'FEMALE',passengerGender:'MALE'}]);
    const service=new ApiService({transaction:async(fn:Function)=>fn({query})} as never);
    await expect(service.createBooking('passenger',{
      tripId:'trip',seats:1,meetingLat:1,meetingLng:1,
      passengerOriginLat:1,passengerOriginLng:1,passengerDestinationLat:2,passengerDestinationLng:2,passengerRoute:[[1,1],[2,2]]
    } as any)).rejects.toThrow('Solo mujeres');
    expect(query.mock.calls.some(call=>call[0].includes('INSERT INTO bookings'))).toBe(false);
  });
  it('impide aceptar reservas incompatibles con la modalidad',async()=>{
    const query=jest.fn().mockResolvedValueOnce([{driverId:'driver',passengerId:'passenger',tripId:'trip',status:'PENDING',seats:1}])
      .mockResolvedValueOnce([{womenOnly:true,driverGender:'FEMALE',passengerGender:null}]);
    const service=new ApiService({transaction:async(fn:Function)=>fn({query})} as never);
    await expect(service.bookingAction('driver','booking','accept')).rejects.toThrow('Solo mujeres');
    expect(query).toHaveBeenCalledTimes(2);
  });
});
