  async setGender(userId: string, gender: 'MALE' | 'FEMALE') {
    if (!['MALE','FEMALE'].includes(gender)) throw new BadRequestException('Selecciona Hombre o Mujer');
    return this.db.transaction(async manager => {
      const [user] = await manager.query('SELECT gender FROM users WHERE id=$1 FOR UPDATE', [userId]);
      if (!user) throw new NotFoundException('Usuario no encontrado');
      if (user.gender && user.gender !== gender) throw new BadRequestException('Para corregir este dato, contacta a soporte');
      const [updated] = await manager.query(`WITH changed AS (UPDATE users SET gender=$2,updated_at=now() WHERE id=$1 RETURNING gender) SELECT * FROM changed`, [userId,gender]);
      return updated;
    });
  }

