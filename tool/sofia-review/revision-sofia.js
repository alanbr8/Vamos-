const base = '/admin/revision-sofia';
const labels = {
  overview: 'Resumen', documents: 'Documentos', profilePhotos: 'Fotos de perfil',
  vehicles: 'Vehículos', incidents: 'Incidentes', users: 'Usuarios',
  communities: 'Comunidades', ledger: 'Bitácora ATT', audit: 'Auditoría',
};
const $ = id => document.getElementById(id);
let token = '';
let view = 'overview';
let expiresAt = 0;
let generation = 0;

function logout(message = '') {
  generation++;
  token = '';
  expiresAt = 0;
  $('appView').hidden = true;
  $('loginView').hidden = false;
  $('password').value = '';
  $('loginError').textContent = message;
  document.querySelectorAll('tbody').forEach(element => element.replaceChildren());
  $('metrics').replaceChildren();
}

async function load() {
  const current = ++generation;
  try {
    const response = await fetch(base + '/datos', {
      headers: { Authorization: 'Bearer ' + token }, cache: 'no-store',
    });
    if (!response.ok) {
      logout('La clave es incorrecta o el acceso ha vencido.');
      return;
    }
    const data = await response.json();
    if (current !== generation || !token) return;
    expiresAt = Date.parse(data.expiresAt);
    $('loginView').hidden = true;
    $('appView').hidden = false;
    $('globalMessage').textContent = 'Solo consulta · Todos los registros son ficticios.';
    $('metrics').replaceChildren(...data.metrics.map(([label, value]) => {
      const card = document.createElement('article');
      card.className = 'metric';
      const text = document.createElement('p');
      text.textContent = label;
      const number = document.createElement('strong');
      number.textContent = value;
      card.append(text, number);
      return card;
    }));
    for (const [id, rows] of Object.entries(data.tables)) {
      const body = $(id);
      const filter = document.querySelector('#' + body.closest('.panel-view').id + ' select');
      // Communities has separate selectors for creation and membership.
      const selector = id === 'communityRows' ? $('communityFilter')
        : id === 'communityCreationRows' ? $('communityCreationFilter') : filter;
      const filtered = rows.filter(row => !selector?.value || row.status === selector.value);
      body.replaceChildren(...filtered.map(row => {
        const tr = document.createElement('tr');
        for (const value of row.cells) {
          const td = document.createElement('td');
          td.textContent = value;
          tr.append(td);
        }
        return tr;
      }));
      if (!filtered.length) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = body.closest('table').querySelectorAll('thead th').length;
        td.textContent = 'No hay registros de prueba para este filtro.';
        tr.append(td);
        body.append(tr);
      }
    }
    showView(view);
  } catch {
    $('loginError').textContent = 'No se pudo consultar. Intenta nuevamente.';
    $('globalMessage').textContent = 'No se pudo actualizar la consulta.';
  }
}

function showView(next) {
  view = next;
  document.querySelectorAll('.panel-view').forEach(el => el.hidden = el.id !== next + 'Panel');
  document.querySelectorAll('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.view === next));
  $('pageTitle').textContent = labels[next];
}

$('loginForm').addEventListener('submit', async event => {
  event.preventDefault();
  token = $('password').value.trim();
  $('password').value = '';
  await load();
});
$('logout').addEventListener('click', () => logout());
$('refresh').addEventListener('click', load);
document.querySelectorAll('[data-view]').forEach(el => el.addEventListener('click', () => {
  showView(el.dataset.view);
  load();
}));
document.querySelectorAll('[data-jump]').forEach(el => el.addEventListener('click', () => {
  showView(el.dataset.jump);
  load();
}));
document.querySelectorAll('select').forEach(el => el.addEventListener('change', load));
setInterval(() => {
  if (token && expiresAt && Date.now() >= expiresAt) logout('El acceso temporal ha vencido.');
}, 1000);
setInterval(() => { if (token) load(); }, 60000);
logout();
