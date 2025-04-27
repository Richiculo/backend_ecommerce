# Database connection parameters
$DB_HOST = "dpg-d00lvu49c44c73bbep80-a.virginia-postgres.render.com"
$DB_PORT = "5432"
$DB_USER = "bdparcialsi2_user"
$DB_NAME = "bdparcialsi2"

# List of all your Django apps
$APPS = @("admin", "auth", "authtoken", "contenttypes", "direcciones", "pedidos", "productos", "sessions", "sucursales", "usuarios")

# 1. Generate Django migration SQL
Write-Output "Generating Django migration SQL..."
Remove-Item "esquema_django.sql" -ErrorAction SilentlyContinue

foreach ($app in $APPS) {
    Write-Output "-- ===== SCHEMA FOR APP $app =====" | Out-File -Append -FilePath "esquema_django.sql"
    python manage.py sqlmigrate $app 0001_initial | Out-File -Append -FilePath "esquema_django.sql"
    Write-Output "" | Out-File -Append -FilePath "esquema_django.sql"
    Write-Output "-- ===== END APP $app =====" | Out-File -Append -FilePath "esquema_django.sql"
    Write-Output "" | Out-File -Append -FilePath "esquema_django.sql"
}

# 2. Export complete schema from PostgreSQL (will prompt for password)
Write-Output "Exporting complete schema from PostgreSQL..."
$env:PGPASSWORD = Read-Host -Prompt "Enter your PostgreSQL password" -AsSecureString | ConvertFrom-SecureString -AsPlainText
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -s --no-owner --no-privileges -f "esquema_postgresql_complete.sql"

# 3. Combine both files
Write-Output "Combining files..."
Get-Content "esquema_django.sql", "esquema_postgresql_complete.sql" | Set-Content "esquema_final.sql"

Write-Output "`nScripts generated:"
Write-Output "1. esquema_django.sql (Django migration SQL)"
Write-Output "2. esquema_postgresql_complete.sql (Complete PostgreSQL schema)"
Write-Output "3. esquema_final.sql (Combined schema)"

Write-Output "`nTo import into another database:"
Write-Output "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d NEW_DB_NAME -f esquema_final.sql"