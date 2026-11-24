// User activity is read from recorded events; counts cover all available history.
function userDate(value) {
  if (!value || !Number.isFinite(new Date(value).getTime())) return 'Sin fecha disponible';
  return new Intl.DateTimeFormat('es-BO',{dateStyle:'medium',timeStyle:'short',timeZone:'America/La_Paz'}).format(new Date(value));
}
async function loadUsers() {
  const filter=$('userFilter').value;
  const rows=await request(`/admin/users${filter?`?status=${filter}`:''}`);
  $('userRows').replaceChildren(...rows.map(user=>{
    const tr=node('tr'),name=node('td'),role=node('td'),status=node('td'),trips=node('td'),cancellations=node('td'),actions=node('td',undefined,'actions');
    name.append(node('strong',`${user.firstName} ${user.lastName}`),node('small',user.email));
    role.append(badge(user.role));status.append(badge(user.status));
    trips.append(node('small',`Conductor: ${user.driverTrips ?? 0}`),node('small',`Pasajero: ${user.passengerTrips ?? 0}`));
    cancellations.append(node('small',`Conductor: ${user.driverCancellations ?? 0}`),node('small',`Pasajero: ${user.passengerCancellations ?? 0}`));
    actions.append(button('Editar nombre',()=>editUserName(user)),button('Ver viajes de conductor',()=>showDriverTrips(user),'secondary'));
    if(user.status!=='ACTIVE')actions.append(button('Reactivar',()=>updateUser(user.id,'ACTIVE')));
    if(user.status==='ACTIVE')actions.append(button('Suspender',()=>confirmUser(user.id,'SUSPENDED'),'muted'));
    if(user.status!=='BLOCKED')actions.append(button('Bloquear',()=>confirmUser(user.id,'BLOCKED'),'danger'));
    tr.append(name,node('td',userDate(user.createdAt)),role,trips,cancellations,status,actions);return tr;
  }));
  if(!rows.length)$('userRows').append(emptyRow(7,'No hay usuarios para este filtro.'));
}
let editingUserId=null;
function editUserName(user) {
  editingUserId=user.id;
  $('userFirstName').value=user.firstName;$('userLastName').value=user.lastName;
  $('userNameError').textContent='';$('userNameSave').disabled=false;
  $('userNameDialog').showModal();
}
$('userNameCancel').addEventListener('click',()=>$('userNameDialog').close());
$('userNameForm').addEventListener('submit',async event=>{
  event.preventDefault();if($('userNameSave').disabled)return;
  const firstName=$('userFirstName').value.trim(),lastName=$('userLastName').value.trim();
  if([firstName,lastName].some(value=>value.length<2||value.length>80)){
    $('userNameError').textContent='Escribe nombres y apellidos de 2 a 80 caracteres.';return;
  }
  $('userNameSave').disabled=true;$('userNameError').textContent='';
  try {
    await request(`/admin/users/${editingUserId}/name`,{method:'PATCH',body:JSON.stringify({firstName,lastName})});
  } catch(error) {$('userNameError').textContent=error.message;$('userNameSave').disabled=false;return;}
  $('userNameDialog').close();
  try {await loadUsers();showMessage('Nombre corregido. El cambio quedó registrado en Auditoría.');}
  catch(error){showMessage(`El nombre se guardó. Pulsa Actualizar para recargar la lista: ${error.message}`,true);}
  finally {$('userNameSave').disabled=false;}
});
let driverTripsRequest=0;
async function showDriverTrips(user) {
  const requestId=++driverTripsRequest;
  $('driverTripsTitle').textContent=`Viajes como conductor · ${user.firstName} ${user.lastName}`;
  $('driverTripsRows').replaceChildren(emptyRow(6,'Cargando…'));
  $('driverTripsDialog').showModal();
  try {
    const rows=await request(`/admin/users/${user.id}/driver-trips`);
    if(requestId!==driverTripsRequest)return;
    const tripStatus={PUBLISHED:'Publicado',RESERVED:'Reservado',IN_PROGRESS:'En curso',COMPLETED:'Finalizado',CANCELLED:'Cancelado'};
    $('driverTripsRows').replaceChildren(...rows.map(item=>{
      const tr=node('tr');
      tr.append(node('td',`${item.origin} → ${item.destination}`),node('td',userDate(item.departureAt)),node('td',tripStatus[item.status]||item.status),node('td',String(item.acceptedBookings)),node('td',String(item.confirmedPassengers)),node('td',String(item.confirmedSeats)));return tr;
    }));
    if(!rows.length)$('driverTripsRows').append(emptyRow(6,'Este usuario no tiene viajes publicados como conductor.'));
  } catch(error){if(requestId===driverTripsRequest)$('driverTripsRows').replaceChildren(emptyRow(6,error.message));}
}
$('driverTripsClose').addEventListener('click',()=>$('driverTripsDialog').close());
$('driverTripsDialog').addEventListener('close',()=>{driverTripsRequest++;$('driverTripsRows').replaceChildren();});
$('userNameDialog').addEventListener('close',()=>{editingUserId=null;});
