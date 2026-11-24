"""Apply administrator user corrections and activity statistics to the extracted source."""
from pathlib import Path
import re
import shutil
import sys

project = Path(sys.argv[1])
source = Path(__file__).resolve().parent
backend = project / 'backend/src'

def replace_file(path, transform):
    text = path.read_text()
    path.write_text(transform(text))

for name in ['admin.service.ts','admin.controller.ts']:
    replace_file(backend/name, lambda text: text.replace('AdminUserStatusDto,', 'AdminUserNameDto, AdminUserStatusDto,') if 'AdminUserNameDto,' not in text else text)
service = backend/'admin.service.ts'
if 'async updateUserName(' not in service.read_text():
    replace_file(service, lambda text: re.sub(r'  users\(status\?: string\) \{.*?(?=  tripLedger\()', (source/'user-methods.ts').read_text(), text, count=1, flags=re.S))
controller = backend/'admin.controller.ts'
if "@Patch('users/:id/name')" not in controller.read_text():
    replace_file(controller, lambda text: text.replace("  @Get('trip-ledger')", """  @Patch('users/:id/name') userName(@Req() req: AuthRequest, @Param('id') id: string, @Body() dto: AdminUserNameDto) {
    return this.admin.updateUserName(req.userId, id, dto);
  }
  @Get('users/:id/driver-trips') userDriverTrips(@Param('id') id: string) { return this.admin.userDriverTrips(id); }
  @Get('trip-ledger')"""))
dtos = backend/'dtos.ts'
if 'export class AdminUserNameDto' not in dtos.read_text():
    with dtos.open('a') as file:
        file.write('''\nexport class AdminUserNameDto {
  @IsString() @MinLength(2) @MaxLength(80) firstName!: string;
  @IsString() @MinLength(2) @MaxLength(80) lastName!: string;
}\n''')
admin = project/'admin'
app = admin/'app.js'
if 'function userDate(' not in app.read_text():
    text = app.read_text()
    text = re.sub(r'async function loadUsers\(\).*?(?=function confirmUser\()', '', text, count=1, flags=re.S)
    text = text.replace("VEHICLE_STATUS_CHANGED:'Estado de vehículo'", "USER_NAME_CHANGED:'Corrección de nombre',VEHICLE_STATUS_CHANGED:'Estado de vehículo'")
    old = "change.append(node('small',`${statusText[item.previousData?.status]"
    new = "if(item.action==='USER_NAME_CHANGED')change.append(node('small',`${item.previousData?.firstName||''} ${item.previousData?.lastName||''} → ${item.newData?.firstName||''} ${item.newData?.lastName||''}`));else change.append(node('small',`${statusText[item.previousData?.status]"
    assert old in text
    text = text.replace(old,new)
    app.write_text(text+'\n'+(source/'users-ui.js').read_text())
html = admin/'index.html'
if 'id="userNameDialog"' not in html.read_text():
    text=html.read_text().replace('Consulta actividad y controla el acceso a la comunidad.', 'Hasta 100 usuarios recientes. Viajes finalizados por rol y cancelaciones propias según registros disponibles. Las cancelaciones del conductor no se atribuyen al pasajero. Fechas en hora de Bolivia. Pulsa Actualizar para ver nuevas cuentas.')
    text=text.replace('<th>Usuario</th><th>Rol</th><th>Viajes</th><th>Estado</th><th>Acciones</th>', '<th>Usuario</th><th>Registro (Bolivia)</th><th>Rol</th><th>Viajes finalizados</th><th>Cancelaciones propias</th><th>Estado</th><th>Acciones</th>')
    text=text.replace('  <script src="app.js"></script>',(source/'dialogs.html').read_text()+'\n  <script src="app.js"></script>')
    html.write_text(text)
css=admin/'styles.css'
if '#userNameForm label' not in css.read_text():
    with css.open('a') as file:
        file.write('\n#userNameForm label{display:grid;gap:.4rem;margin:1rem 0}#userNameForm input{border:1px solid var(--line);border-radius:9px;padding:.7rem;width:100%}#driverTripsDialog{width:1000px;max-width:94vw}#driverTripsClose{margin-top:1rem}\n')
shutil.copyfile(source/'admin-users.spec.ts', backend/'admin-users.spec.ts')
assert 'async updateUserName(' in service.read_text(), 'Admin service patch did not apply'
