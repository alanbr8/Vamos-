from pathlib import Path
import shutil
import sys

root=Path(sys.argv[1])
source=Path(__file__).resolve().parent
backend=root/'backend/src'
app=root/'vamos_app/lib'

def edit(path,old,new):
    text=path.read_text()
    if new in text:return
    if old not in text:raise SystemExit(f'No se encontró el punto de aplicación en {path}: {old[:80]}')
    path.write_text(text.replace(old,new,1))

for name in ['women-policy.ts','women-mode.migration.ts','women-mode.spec.ts']:
    shutil.copyfile(source/name,backend/name)
module=backend/'app.module.ts'
edit(module,"import { Module }", "import { WomenMode1795737600000 } from './women-mode.migration';\nimport { Module }")
edit(module,'        synchronize: false,','        synchronize: false,\n        migrations: [WomenMode1795737600000],\n        migrationsTableName: \'vamos_feature_migrations\',\n        migrationsRun: true,')
dtos=backend/'dtos.ts'
edit(dtos,'export class RegisterDto {', "export class RegisterDto {\n  @IsOptional() @IsIn(['MALE','FEMALE']) gender?: 'MALE' | 'FEMALE';")
edit(dtos,'export class SearchTripsDto {', "export class SearchTripsDto {\n  @IsOptional() @IsIn([true,false]) womenOnly?: boolean;")
edit(dtos,'export class LoginDto', "export class ProfileGenderDto { @IsIn(['MALE','FEMALE']) gender!: 'MALE' | 'FEMALE'; }\nexport class LoginDto")
auth=backend/'auth.service.ts'
edit(auth,'password_hash,usage_mode)', 'password_hash,usage_mode,gender)')
edit(auth,'VALUES($1,$2,lower($3),$4,$5,$6)', 'VALUES($1,$2,lower($3),$4,$5,$6,$7)')
edit(auth,'email,phone,usage_mode AS "usageMode"`','email,phone,usage_mode AS "usageMode",gender`')
edit(auth,"dto.usageMode??'PASSENGER'],", "dto.usageMode??'PASSENGER',dto.gender??null],")
edit(auth,'usageMode:user.usage_mode }','usageMode:user.usage_mode, gender:user.gender }')
api=backend/'api.service.ts'
edit(api,"import { randomInt }", "import { womenOnly, requireWoman, requireWomenBooking } from './women-policy';\nimport { randomInt }")
edit(api,'u.id,u.usage_mode AS "usageMode"','u.id,u.gender,u.usage_mode AS "usageMode"')
edit(api,'  vehicles(userId: string)',(source/'profile-gender.ts').read_text()+'  vehicles(userId: string)')
edit(api,"    await manager.query('SELECT id FROM users WHERE id=$1 FOR UPDATE',[userId]);", """    const [identity] = await manager.query('SELECT id,gender FROM users WHERE id=$1 FOR UPDATE',[userId]);
    if (womenOnly(dto.preferences)) requireWoman(identity?.gender);""")
edit(api,'  search(userId: string, dto: SearchTripsDto) {', """  async search(userId: string, dto: SearchTripsDto) {
    if (dto.womenOnly) {
      const [self] = await this.db.query('SELECT gender FROM users WHERE id=$1',[userId]);
      requireWoman(self?.gender);
    }""")
edit(api,'SELECT t.id,t.origin_label AS origin,t.destination_label AS destination,t.departure_at AS "departureAt",', 'SELECT t.id,(t.preferences->>\'womenOnly\'=\'true\') AS "womenOnly",t.origin_label AS origin,t.destination_label AS destination,t.departure_at AS "departureAt",')
edit(api,"       AND vamos_community_access(t.community_id,$8)", """       AND vamos_community_access(t.community_id,$8)
       AND (NOT $9::boolean OR (t.preferences->>'womenOnly'='true' AND u.gender='FEMALE'))
       AND (COALESCE(t.preferences->>'womenOnly','false')<>'true' OR (u.gender='FEMALE' AND EXISTS(SELECT 1 FROM users passenger WHERE passenger.id=$8 AND passenger.gender='FEMALE')))""")
edit(api,'dto.maxDistanceMeters, userId]);','dto.maxDistanceMeters, userId, dto.womenOnly === true]);')
edit(api,'  async saveSearch(userId: string, dto: SaveSearchDto) {', """  async saveSearch(userId: string, dto: SaveSearchDto) {
    if (dto.womenOnly) {
      const [self] = await this.db.query('SELECT gender FROM users WHERE id=$1',[userId]);
      requireWoman(self?.gender);
    }""")
edit(api,'const criteria = {originLat,originLng,destinationLat,destinationLng,maxDistanceMeters:', 'const criteria = {womenOnly:dto.womenOnly===true,originLat,originLng,destinationLat,destinationLng,maxDistanceMeters:')
edit(api,'      AND vamos_community_access(t.community_id,s.user_id)', """      AND vamos_community_access(t.community_id,s.user_id)
      AND (COALESCE(s.criteria->>'womenOnly','false')<>'true' OR (t.preferences->>'womenOnly'='true' AND u.gender='FEMALE' AND EXISTS(SELECT 1 FROM users passenger WHERE passenger.id=s.user_id AND passenger.gender='FEMALE')))
      AND (COALESCE(t.preferences->>'womenOnly','false')<>'true' OR (u.gender='FEMALE' AND EXISTS(SELECT 1 FROM users passenger WHERE passenger.id=s.user_id AND passenger.gender='FEMALE')))""")
# Check the restriction after the trip lock, including direct API requests.
edit(api,'      const [booking] = await manager.query(', """      const [access] = await manager.query(`SELECT (t.preferences->>'womenOnly'='true') AS "womenOnly",driver.gender AS "driverGender",passenger.gender AS "passengerGender"
        FROM trips t JOIN users driver ON driver.id=t.driver_id JOIN users passenger ON passenger.id=$2 WHERE t.id=$1`, [dto.tripId,userId]);
      if (!access) throw new ForbiddenException('No se pudo comprobar el acceso al viaje');
      requireWomenBooking(access,access.passengerGender,dto.seats);
      const [booking] = await manager.query(""")
edit(api,"      if (action === 'accept') {", """      if (action === 'accept') {
        const [access] = await manager.query(`SELECT (t.preferences->>'womenOnly'='true') AS "womenOnly",driver.gender AS "driverGender",passenger.gender AS "passengerGender"
          FROM trips t JOIN users driver ON driver.id=t.driver_id JOIN users passenger ON passenger.id=$2 WHERE t.id=$1`, [row.tripId,row.passengerId]);
        if (!access) throw new ForbiddenException('No se pudo comprobar el acceso al viaje');
        requireWomenBooking(access,access.passengerGender,row.seats);""")
controller=backend/'api.controller.ts'
edit(controller,'ActionReasonDto, SaveSearchDto','ProfileGenderDto, ActionReasonDto, SaveSearchDto')
edit(controller,"  @UseGuards(JwtAuthGuard) @Get('users/me')", """  @UseGuards(JwtAuthGuard) @Patch('users/me/gender') setGender(@Req() req: AuthRequest,@Body() dto: ProfileGenderDto) { return this.api.setGender(req.userId,dto.gender); }
  @UseGuards(JwtAuthGuard) @Get('users/me')""")
# SQL also supports freshly initialized databases used in integration checks.
sql=root/'database/init.sql'
if 'ADD COLUMN IF NOT EXISTS gender' not in sql.read_text():
    with sql.open('a') as file:file.write("\nALTER TABLE users ADD COLUMN IF NOT EXISTS gender varchar(6) CHECK(gender IN ('MALE','FEMALE'));\n")
client=app/'services/api_client.dart'
edit(client,"    String usageMode = 'PASSENGER',", "    String usageMode = 'PASSENGER',\n    String? gender,")
edit(client,"        'usageMode': usageMode,", "        'usageMode': usageMode,\n        if (gender != null) 'gender': gender,")
edit(client,'  Future<Map<String, dynamic>> profile()', "  Future<Map<String, dynamic>> setGender(String gender) => _request('PATCH', '/users/me/gender', body: {'gender': gender});\n\n  Future<Map<String, dynamic>> profile()")
register=app/'screens/auth/register_screen.dart'
edit(register,"  String _usageMode = 'PASSENGER';", "  String _usageMode = 'PASSENGER';\n  String? _gender;")
edit(register,'        usageMode: _usageMode,','        usageMode: _usageMode,\n        gender: _gender,')
edit(register,'              TextFormField(\n                controller: _firstName,', """              DropdownButtonFormField<String>(
                initialValue: _gender,
                decoration: const InputDecoration(labelText: '¿Eres hombre o mujer?'),
                items: const [DropdownMenuItem(value:'MALE',child:Text('Hombre')),DropdownMenuItem(value:'FEMALE',child:Text('Mujer'))],
                validator:(value)=>value==null ? 'Selecciona una opción' : null,
                onChanged:_loading ? null : (value)=>setState(()=>_gender=value),
              ),
              const Text('Este dato permite acceder a la modalidad Solo mujeres. Es una declaración de la persona y no una verificación adicional de identidad.'),
              const SizedBox(height:12),
              TextFormField(
                controller: _firstName,""")
profile=app/'screens/profile/profile_screen.dart'
edit(profile,'  double average(String key)', """  Future<void> completeGender() async {
    final selected = await showDialog<String>(context:context,builder:(dialogContext)=>SimpleDialog(
      title:const Text('¿Eres hombre o mujer?'),
      children:[
        const Padding(padding:EdgeInsets.all(16),child:Text('Se utilizará para la modalidad Solo mujeres. Para corregirlo después, contacta a soporte.')),
        SimpleDialogOption(onPressed:()=>Navigator.pop(dialogContext,'MALE'),child:const Text('Hombre')),
        SimpleDialogOption(onPressed:()=>Navigator.pop(dialogContext,'FEMALE'),child:const Text('Mujer')),
      ],
    ));
    if(selected==null || !mounted)return;
    try {await ApiClient.instance.setGender(selected);if(mounted)await load();}
    on ApiException catch(e){if(mounted)ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text(e.message)));}
  }

  double average(String key)""")
edit(profile,'    children: [\n      ListTile(leading: const Icon(Icons.emergency)', """    children: [
      ListTile(
        leading:const Icon(Icons.person_outline),
        title:Text(profile['gender']=='FEMALE' ? 'Mujer' : profile['gender']=='MALE' ? 'Hombre' : 'Completar Hombre/Mujer'),
        subtitle:Text(profile['gender']==null ? 'Necesario para acceder a Solo mujeres' : 'Dato declarado. Para corregirlo, contacta a soporte.'),
        onTap:profile['gender']==null ? completeGender : null,
      ),
      ListTile(leading: const Icon(Icons.emergency)""")
# Add reusable switch to the existing search and publish forms.
shutil.copyfile(source/'women_only_switch.dart',app/'widgets/women_only_switch.dart')
search=app/'screens/trips/search_trip_screen.dart'
edit(search,"import '../../widgets/trip_points_map.dart';", "import '../../widgets/women_only_switch.dart';\nimport '../../widgets/trip_points_map.dart';")
edit(search,'  bool searched = false;','  bool searched = false;\n  bool womenOnly = false;')
edit(search,"      final c = record['criteria'] as Map;", "      final c = record['criteria'] as Map;\n      womenOnly = c['womenOnly']==true;")
edit(search,"        'maxDistanceMeters': 1500,", "        'maxDistanceMeters': 1500,\n        'womenOnly': womenOnly,")
edit(search,'      ElevatedButton.icon(\n        onPressed: loading ? null : search,', """      WomenOnlySwitch(value:womenOnly,publishing:false,onChanged:(value){if(loading)return;setState(() {womenOnly=value;saved=false;searched=false;liveMatches=[];});}),
      ElevatedButton.icon(
        onPressed: loading ? null : search,""")
edit(search,'      if (saved) const Padding', "      if(womenOnly)const Padding(padding:EdgeInsets.all(12),child:Text('Solo mujeres · conductoras y pasajeras. Una cuenta por asiento.')),\n      if (saved) const Padding")
# Badge accompanies ordinary search results too.
model=app/'models/trip_match.dart'
edit(model,'    this.driverVerified=false,','    this.womenOnly=false,\n    this.driverVerified=false,')
edit(model,'  final bool driverVerified;','  final bool womenOnly;\n  final bool driverVerified;')
edit(search,'  return TripMatch(','  return TripMatch(\n    womenOnly: data[\'womenOnly\']==true,')
edit(search,'                      if(match.driverVerified)', "                      if(match.womenOnly)const Text('Solo mujeres · un asiento por cuenta',style:TextStyle(fontWeight:FontWeight.bold)),\n                      if(match.driverVerified)")
publish=app/'screens/trips/publish_trip_screen.dart'
text=publish.read_text()
if "import '../../widgets/women_only_switch.dart';" not in text:publish.write_text("import '../../widgets/women_only_switch.dart';\n"+text)
edit(publish,'  bool _recurring = false;','  bool _recurring = false;\n  bool _womenOnly = false;')
edit(publish,"      final prefs = t['preferences'] as Map? ?? {};", "      final prefs = t['preferences'] as Map? ?? {};\n      _womenOnly = prefs['womenOnly']==true;")
edit(publish,"preferences: {...trip.preferences.toJson(),'routeEstimate':", "preferences: {...trip.preferences.toJson(),'womenOnly':_womenOnly,'routeEstimate':")
edit(publish,"        SwitchListTile(\n          contentPadding: EdgeInsets.zero,\n          title: const Text('Guardar días habituales'),", """        WomenOnlySwitch(value:_womenOnly,publishing:true,onChanged:(value)=>setState(()=>_womenOnly=value)),
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          title: const Text('Guardar días habituales'),""")

edit(search,'List.generate(match.seats.clamp(0,7).toInt(),', 'List.generate((match.womenOnly ? 1 : match.seats.clamp(0,7).toInt()),')

shutil.copyfile(source/'women_mode_test.dart', root/'vamos_app/test/women_mode_test.dart')
