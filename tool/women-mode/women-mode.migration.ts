import { MigrationInterface, QueryRunner } from 'typeorm';

export class WomenMode1795737600000 implements MigrationInterface {
  name = 'WomenMode1795737600000';
  async up(runner: QueryRunner): Promise<void> {
    await runner.query(`ALTER TABLE users ADD COLUMN IF NOT EXISTS gender varchar(6)
      CHECK (gender IN ('MALE','FEMALE'))`);
  }
  async down(): Promise<void> {
    // Preserve declared data even when application code is rolled back.
  }
}
