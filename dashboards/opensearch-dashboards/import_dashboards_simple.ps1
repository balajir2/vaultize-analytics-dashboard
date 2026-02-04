# Simple Import Script
# Authors: Balaji Rajan and Claude (Anthropic)

$url = "http://localhost:5601"
$dir = "$PSScriptRoot\saved-objects"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "OpenSearch Dashboards Import (Simple)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check connectivity
Write-Host "Checking connectivity... " -NoNewline
try {
    $null = Invoke-WebRequest "$url/api/status" -UseBasicParsing -TimeoutSec 5
    Write-Host "OK" -ForegroundColor Green
}
catch {
    Write-Host "FAILED" -ForegroundColor Red
    Write-Host "Make sure OpenSearch Dashboards is running at $url"
    exit 1
}

Write-Host ""

# Import function
function Import-File($file) {
    Write-Host "Importing $file... " -NoNewline

    $result = & curl.exe -s -X POST "$url/api/saved_objects/_import?overwrite=true" `
        -H "osd-xsrf: true" `
        -F "file=@$dir\$file"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS" -ForegroundColor Green
    }
    else {
        Write-Host "FAILED" -ForegroundColor Red
    }
}

# Import files in order
Import-File "index-pattern.ndjson"
Import-File "visualizations.ndjson"
Import-File "dashboards.ndjson"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Import Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View dashboards at: $url/app/dashboards" -ForegroundColor Yellow
Write-Host ""
