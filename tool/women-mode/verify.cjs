const {PGlite}=require('@electric-sql/pglite');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const project=process.argv[2];
(async()=>{
 const db=new PGlite();
 await db.exec(`CREATE TABLE users(id uuid PRIMARY KEY,first_name text);
 INSERT INTO users VALUES ('00000000-0000-4000-8000-000000000001','Cuenta anterior');`);
 const {WomenMode1795737600000}=require(path.resolve(project,'backend/dist/women-mode.migration.js'));
 const migration=new WomenMode1795737600000();
 const runner={query:(sql,args)=>db.query(sql,args)};
 await migration.up(runner);await migration.up(runner);
 assert.equal((await db.query('SELECT gender FROM users')).rows[0].gender,null);
 await assert.rejects(db.query("UPDATE users SET gender='INVALID'"));
 await db.exec(`UPDATE users SET gender='FEMALE';
 INSERT INTO users VALUES ('00000000-0000-4000-8000-000000000002','Hombre','MALE'),('00000000-0000-4000-8000-000000000003','Sin dato',null);
 CREATE TABLE trips(id text,driver_id uuid,preferences jsonb);
 INSERT INTO trips VALUES
 ('female-only','00000000-0000-4000-8000-000000000001','{"womenOnly":true}'),
 ('mixed','00000000-0000-4000-8000-000000000001','{}'),
 ('man','00000000-0000-4000-8000-000000000002','{}'),
 ('invalid-exclusive','00000000-0000-4000-8000-000000000002','{"womenOnly":true}');`);
 const source=fs.readFileSync(path.resolve(project,'backend/src/api.service.ts'),'utf8');
 const clauses=source.match(/AND \(NOT \$9::boolean[\s\S]*?(?=\n       AND t.departure_at)/)[0].replaceAll('$9','$2').replaceAll('$8','$1');
 const query=`SELECT t.id FROM trips t JOIN users u ON u.id=t.driver_id WHERE true ${clauses} ORDER BY t.id`;
 const woman='00000000-0000-4000-8000-000000000001',man='00000000-0000-4000-8000-000000000002',unknown='00000000-0000-4000-8000-000000000003';
 assert.deepEqual((await db.query(query,[woman,true])).rows.map(r=>r.id),['female-only']);
 for(const id of [man,unknown])assert.deepEqual((await db.query(query,[id,false])).rows.map(r=>r.id),['man','mixed']);
 await db.exec('CREATE TABLE saved_searches(user_id uuid,criteria jsonb);');
 await db.query('INSERT INTO saved_searches VALUES ($1,$2),($3,$4)',[woman,{womenOnly:true},man,{womenOnly:true}]);
 const savedClauses=source.match(/AND \(COALESCE\(s.criteria->>'womenOnly'[\s\S]*?(?=\n      AND ST_DWithin)/)[0];
 const matches=(await db.query(`SELECT t.id,s.user_id FROM saved_searches s CROSS JOIN trips t JOIN users u ON u.id=t.driver_id WHERE true ${savedClauses}`)).rows;
 assert.equal(matches.length,1);assert.equal(matches[0].id,'female-only');assert.equal(matches[0].user_id,woman);
 await db.close();console.log('OK: repeatable migration; existing users preserved; SQL search and saved-alert restrictions for women, men and missing gender.');
})().catch(error=>{console.error(error);process.exit(1)});
