# Execute in PowerShell on the INGENIX custodian's own computer, outside the Git repository.
$ErrorActionPreference = 'Stop'
$signingFolder = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'INGENIX-Vamos-Firma'
New-Item -ItemType Directory -Force -Path $signingFolder | Out-Null
$keyFile = Join-Path $signingFolder 'vamos-production.jks'
if (Test-Path $keyFile) { throw 'Ya existe una clave de producción. No se reemplazará. Conserva y utiliza la existente.' }
# keytool requests the password interactively. No password is stored by this script.
& keytool -genkeypair -v -keystore $keyFile -storetype JKS -alias vamos-production -keyalg RSA -keysize 3072 -validity 10000 -dname 'CN=INGENIX Vamos, OU=Desarrollo, O=INGENIX, L=Santa Cruz, C=BO'
if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar la clave.' }
[Convert]::ToBase64String([IO.File]::ReadAllBytes($keyFile)) | Set-Content -NoNewline -Encoding ascii (Join-Path $signingFolder 'VAMOS_RELEASE_KEYSTORE.txt')
Write-Host "Clave creada en $signingFolder. Guarda una copia privada y las contraseñas en un lugar seguro. No subas estos archivos al repositorio ni los envíes a Sofía."
