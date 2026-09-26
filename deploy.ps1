<#
.SYNOPSIS
    Script de apoyo para el Integrante 3 (preparación y publicación de la app).

.DESCRIPTION
    Automatiza las tareas repetitivas antes de publicar en Render:
      1. Crea/activa el entorno virtual e instala requirements.txt
      2. Corre la app localmente en modo prueba (opcional)
      3. Verifica que existan los archivos requeridos por Render (Procfile, requirements.txt)
      4. Hace commit y push a main, lo que dispara el auto-deploy en Render
         (si el servicio en Render ya está conectado al repositorio de GitHub)

.USAGE
    Abrir PowerShell en la raíz del proyecto y ejecutar:
        .\deploy.ps1                 -> instala dependencias, valida y hace push
        .\deploy.ps1 -RunLocal       -> además levanta el servidor local para probar
        .\deploy.ps1 -SkipPush       -> solo instala y valida, no hace commit/push

.NOTAS
    - Requiere tener git configurado y el remoto "origin" ya apuntando al repo de GitHub.
    - El primer despliegue en Render se hace manualmente desde render.com
      conectando el repositorio (o usando render.yaml como Blueprint).
      Este script solo automatiza los despliegues siguientes vía git push.
#>

param(
    [switch]$RunLocal,
    [switch]$SkipPush,
    [string]$CommitMessage = "deploy: actualizacion de la aplicacion"
)

$ErrorActionPreference = "Stop"

function Write-Step($mensaje) {
    Write-Host "`n==> $mensaje" -ForegroundColor Cyan
}

# 1. Verificar que estamos en la raíz del proyecto
if (-not (Test-Path ".\app.py")) {
    Write-Host "ERROR: Ejecuta este script desde la carpeta raiz del proyecto (donde esta app.py)." -ForegroundColor Red
    exit 1
}

# 2. Crear / activar entorno virtual
Write-Step "Verificando entorno virtual (venv)"
if (-not (Test-Path ".\venv")) {
    python -m venv venv
    Write-Host "Entorno virtual creado."
} else {
    Write-Host "Entorno virtual ya existe."
}

Write-Step "Activando entorno virtual"
& .\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
Write-Step "Instalando dependencias de requirements.txt"
pip install --upgrade pip | Out-Null
pip install -r requirements.txt

# 4. Validar archivos requeridos para Render
Write-Step "Validando archivos necesarios para el despliegue"
$archivosRequeridos = @("requirements.txt", "Procfile", "app.py")
$faltantes = @()
foreach ($archivo in $archivosRequeridos) {
    if (-not (Test-Path ".\$archivo")) {
        $faltantes += $archivo
    }
}
if ($faltantes.Count -gt 0) {
    Write-Host "ERROR: Faltan archivos requeridos: $($faltantes -join ', ')" -ForegroundColor Red
    exit 1
}
Write-Host "OK: requirements.txt, Procfile y app.py presentes."

if (-not (Test-Path ".\data\dataset.csv") -and -not (Test-Path ".\data\dataset.xlsx")) {
    Write-Host "ADVERTENCIA: No se encontro data\dataset.csv ni data\dataset.xlsx. La app mostrara el aviso de dataset no cargado." -ForegroundColor Yellow
}

# 5. Prueba local opcional
if ($RunLocal) {
    Write-Step "Levantando servidor local en http://127.0.0.1:5000 (Ctrl+C para detener)"
    python app.py
}

# 6. Commit y push (dispara el auto-deploy en Render)
if (-not $SkipPush) {
    Write-Step "Preparando commit y push hacia main"
    git add -A
    $hayCambios = git status --porcelain
    if ([string]::IsNullOrWhiteSpace($hayCambios)) {
        Write-Host "No hay cambios pendientes por confirmar."
    } else {
        git commit -m "$CommitMessage"
        git push origin main
        Write-Host "`nPush realizado. Si el servicio de Render ya esta conectado a este repositorio," -ForegroundColor Green
        Write-Host "el despliegue se iniciara automaticamente. Revisa el estado en el dashboard de Render." -ForegroundColor Green
    }
}

Write-Step "Proceso finalizado"
