  users(status?: string) {
    if (status && !['ACTIVE', 'SUSPENDED', 'BLOCKED'].includes(status)) {
      throw new BadRequestException('Estado de usuario inválido');
    }
    return this.db.query(`SELECT u.id,u.first_name AS "firstName",u.last_name AS "lastName",u.email,
      u.status,u.role,u.identity_verified AS "identityVerified",u.created_at AS "createdAt",
      (SELECT count(*)::int FROM trips t WHERE t.driver_id=u.id) AS "tripCount",
      (SELECT count(*)::int FROM trips t WHERE t.driver_id=u.id AND t.status='COMPLETED') AS "driverTrips",
      (SELECT count(DISTINCT b.trip_id)::int FROM bookings b WHERE b.passenger_id=u.id AND b.status='COMPLETED') AS "passengerTrips",
      (SELECT count(*)::int FROM trips t WHERE t.driver_id=u.id AND t.status='CANCELLED') AS "driverCancellations",
      ((SELECT count(*) FROM notifications n JOIN bookings b ON n.data->>'bookingId'=b.id::text
        JOIN trips t ON t.id=b.trip_id WHERE b.passenger_id=u.id AND n.type='BOOKING_CANCELLED' AND n.user_id=t.driver_id)
       + (SELECT count(*) FROM bookings b WHERE b.passenger_id=u.id AND b.status='CANCELLED'
        AND NULLIF(trim(b.cancellation_reason),'') IS NOT NULL
        AND NOT EXISTS(SELECT 1 FROM notifications n WHERE n.type='BOOKING_CANCELLED' AND n.data->>'bookingId'=b.id::text)))::int AS "passengerCancellations"
      FROM users u WHERE ($1::text IS NULL OR u.status::text=$1)
      ORDER BY u.created_at DESC,u.id LIMIT 100`, [status || null]);
  }

  async userDriverTrips(id: string) {
    const [user] = await this.db.query('SELECT id FROM users WHERE id=$1', [id]);
    if (!user) throw new NotFoundException('Usuario no encontrado');
    return this.db.query(`SELECT t.id,t.origin_label AS origin,t.destination_label AS destination,
      t.departure_at AS "departureAt",t.status,
      count(b.id) FILTER (WHERE b.encounter_verified_at IS NOT NULL)::int AS "confirmedPassengers",
      COALESCE(sum(b.seats) FILTER (WHERE b.encounter_verified_at IS NOT NULL),0)::int AS "confirmedSeats",
      count(b.id) FILTER (WHERE b.status IN ('ACCEPTED','COMPLETED'))::int AS "acceptedBookings"
      FROM trips t LEFT JOIN bookings b ON b.trip_id=t.id WHERE t.driver_id=$1
      GROUP BY t.id ORDER BY t.departure_at DESC,t.id LIMIT 200`, [id]);
  }

  async updateUserName(adminId: string, id: string, dto: AdminUserNameDto) {
    const firstName = typeof dto.firstName === 'string' ? dto.firstName.trim() : '';
    const lastName = typeof dto.lastName === 'string' ? dto.lastName.trim() : '';
    if ([firstName,lastName].some(value => value.length < 2 || value.length > 80)) {
      throw new BadRequestException('Nombres y apellidos deben tener entre 2 y 80 caracteres');
    }
    return this.db.transaction(async manager => {
      const [previous] = await manager.query(`SELECT id,first_name AS "firstName",last_name AS "lastName" FROM users WHERE id=$1 FOR UPDATE`, [id]);
      if (!previous) throw new NotFoundException('Usuario no encontrado');
      if (previous.firstName === firstName && previous.lastName === lastName) return previous;
      const [updated] = await manager.query(`WITH changed AS (UPDATE users SET first_name=$2,last_name=$3,updated_at=now() WHERE id=$1
        RETURNING id,first_name AS "firstName",last_name AS "lastName") SELECT * FROM changed`, [id,firstName,lastName]);
      await this.audit(manager,adminId,'USER_NAME_CHANGED','USER',id,previous,updated);
      return updated;
    });
  }

