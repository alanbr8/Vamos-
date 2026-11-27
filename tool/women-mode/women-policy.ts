import { BadRequestException, ForbiddenException } from '@nestjs/common';

export function womenOnly(preferences?: Record<string, unknown>): boolean {
  const value = preferences?.womenOnly;
  if (value !== undefined && typeof value !== 'boolean') {
    throw new BadRequestException('La opción Solo mujeres debe ser verdadera o falsa');
  }
  return value === true;
}

export function requireWoman(gender: unknown): void {
  if (gender !== 'FEMALE') {
    throw new ForbiddenException('Para usar Solo mujeres debes tener Mujer registrado en tu perfil. Completa el dato en Mi perfil o contacta a soporte para corregirlo.');
  }
}

export function requireWomenBooking(trip: { womenOnly?: boolean; driverGender?: string }, passengerGender: unknown, seats: number): void {
  if (!trip.womenOnly) return;
  requireWoman(trip.driverGender);
  requireWoman(passengerGender);
  if (seats !== 1) throw new BadRequestException('En Solo mujeres cada pasajera debe solicitar su propio asiento desde su cuenta');
}
