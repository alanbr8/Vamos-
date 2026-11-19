from pathlib import Path
import re
import shutil
import sys

project = Path(sys.argv[1])
source = Path(__file__).resolve().parent
admin = project / "admin"
html = (admin / "index.html").read_text()
html = html.replace("Panel de operaciones", "Revisión de Operaciones")
html = html.replace("Acceso exclusivo para cuentas administradoras.", "Sofía · Solo consulta · Datos ficticios · Acceso temporal de 72 horas.")
html = re.sub(r'<label>Correo<input[^>]+></label>', '', html)
html = re.sub(r'<label>Dirección de la API<input[^>]+></label>', '', html)
html = html.replace('Contraseña<input', 'Clave temporal<input')
html = html.replace('autocomplete="current-password"', 'autocomplete="off" maxlength="64"')
html = html.replace('href="styles.css"', 'href="/admin/revision-sofia/styles.css"')
html = html.replace('src="app.js"', 'src="/admin/revision-sofia/consulta.js"')
html = html.replace('<p class="eyebrow">OPERACIONES</p>', '<p class="eyebrow">REVISIÓN SOFÍA · SOLO CONSULTA · DATOS FICTICIOS</p>')
html = re.sub(r'<button id="exportLedger"[^>]*>.*?</button>', '', html)
html = html.replace("Atiende primero verificaciones e incidentes abiertos.", "Consulta ejemplos de verificaciones e incidentes del piloto.")
html = html.replace("Aprueba los datos o registra el motivo del rechazo.", "Consulta los datos y estados de los vehículos de prueba.")
html = html.replace("Clasifica y cierra los reportes de seguridad.", "Consulta los reportes de seguridad de prueba.")
html = html.replace("Consulta actividad y controla el acceso a la comunidad.", "Consulta la actividad de usuarios de prueba.")
html = html.replace("La exportación incluye hasta los 1.000 registros más recientes.", "Se muestran recorridos ficticios para esta revisión.")
html = html.replace("<th>Acciones</th>", "<th>Permiso</th>")
(admin / "revision-sofia.html").write_text(html)
shutil.copyfile(source / "revision-sofia.js", admin / "revision-sofia.js")
shutil.copyfile(source / "review-panel.ts", project / "backend/src/review-panel.ts")
