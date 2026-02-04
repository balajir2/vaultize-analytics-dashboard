# Import Dashboards Script (PowerShell)
#
# Automatically imports saved objects (index patterns, visualizations, dashboards)
# into OpenSearch Dashboards.
#
# Authors: Balaji Rajan and Claude (Anthropic)
# License: Apache 2.0

# Configuration
$DashboardsUrl = if ($env:DASHBOARDS_URL) { $env:DASHBOARDS_URL } else { "http://localhost:5601" }
$SavedObjectsDir = Join-Path $PSScriptRoot "saved-objects"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "OpenSearch Dashboards Import Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboards URL: $DashboardsUrl"
Write-Host "Saved Objects Directory: $SavedObjectsDir"
Write-Host ""

# Check if OpenSearch Dashboards is running
Write-Host "Checking OpenSearch Dashboards connectivity... " -NoNewline
try {
    $status = Invoke-WebRequest -Uri "$DashboardsUrl/api/status" -Method Get -UseBasicParsing -ErrorAction Stop
    Write-Host "OK" -ForegroundColor Green
} catch {
    Write-Host "FAILED" -ForegroundColor Red
    Write-Host "Error: Cannot connect to OpenSearch Dashboards at $DashboardsUrl" -ForegroundColor Red
    Write-Host "Make sure OpenSearch Dashboards is running:"
    Write-Host "  docker compose up -d opensearch-dashboards"
    exit 1
}

Write-Host ""

# Function to import saved objects
function Import-SavedObjects {
    param (
        [string]$FilePath
    )

    $name = [System.IO.Path]::GetFileNameWithoutExtension($FilePath)
    Write-Host "Importing $name... " -NoNewline

    try {
        # Read file content
        $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $fileContent = [System.Text.Encoding]::UTF8.GetString($fileBytes)

        # Create multipart form data
        $boundary = [System.Guid]::NewGuid().ToString()
        $LF = "`r`n"

        $bodyLines = (
            "--$boundary",
            "Content-Disposition: form-data; name=`"file`"; filename=`"$name.ndjson`"",
            "Content-Type: application/ndjson$LF",
            $fileContent,
            "--$boundary--$LF"
        ) -join $LF

        # Make request
        $response = Invoke-WebRequest `
            -Uri "$DashboardsUrl/api/saved_objects/_import?overwrite=true" `
            -Method Post `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $bodyLines `
            -Headers @{ "osd-xsrf" = "true" } `
            -UseBasicParsing `
            -ErrorAction Stop

        Write-Host "SUCCESS" -ForegroundColor Green

        # Parse response
        $result = $response.Content | ConvertFrom-Json
        if ($result.success -or $result.successCount -gt 0) {
            $count = if ($result.successCount) { $result.successCount } else { 1 }
            Write-Host "  └─ Imported $count objects" -ForegroundColor Gray
        }

    } catch {
        Write-Host "FAILED" -ForegroundColor Red
        Write-Host "  └─ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Import in correct order (dependencies first)
Write-Host "Importing saved objects..." -ForegroundColor Cyan
Write-Host ""

$files = @(
    "index-pattern.ndjson",
    "visualizations.ndjson",
    "dashboards.ndjson"
)

foreach ($file in $files) {
    $filePath = Join-Path $SavedObjectsDir $file
    if (Test-Path $filePath) {
        Import-SavedObjects -FilePath $filePath
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Import Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your dashboards at:"
Write-Host "  $DashboardsUrl/app/dashboards" -ForegroundColor Yellow
Write-Host ""
Write-Host "Available dashboards:"
Write-Host "  - Operations Dashboard (real-time monitoring)"
Write-Host "  - Analytics Dashboard (historical analysis)"
Write-Host ""
