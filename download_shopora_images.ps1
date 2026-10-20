$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.\manage.py')) {
    throw 'Run this script from your Django project root (the folder containing manage.py).'
}

$mediaDir = Join-Path (Get-Location) 'media\products'
New-Item -ItemType Directory -Path $mediaDir -Force | Out-Null

# Use direct Unsplash CDN image URLs (not Unsplash webpage/download URLs).
$images = @(
    @{ Product = 'Coffee Maker'; File = 'coffee-maker.jpg'; Url = 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=85' },
    @{ Product = 'Laptop Pro 15'; File = 'laptop-pro-15.jpg'; Url = 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=1200&q=85' },
    @{ Product = 'Power Bank 10000mAh'; File = 'power-bank.jpg'; Url = 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=1200&q=85' },
    @{ Product = 'Smartphone 128GB'; File = 'smartphone-128gb.jpg'; Url = 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1200&q=85' },
    @{ Product = 'Bluetooth Speaker'; File = 'bluetooth-speaker.jpg'; Url = 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=1200&q=85' }
)

$downloaded = @()
foreach ($item in $images) {
    $destination = Join-Path $mediaDir $item.File
    Write-Host "Downloading $($item.Product)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $item.Url -OutFile $destination -Headers @{ 'User-Agent' = 'Mozilla/5.0' }
    $file = Get-Item $destination
    if ($file.Length -lt 5000) {
        throw "Download for $($item.Product) looks too small ($($file.Length) bytes). No database paths have been changed yet."
    }
    Write-Host "Saved $($item.File) ($($file.Length) bytes)" -ForegroundColor Green
    $downloaded += $item
}

$pythonCode = "from products.models import Product; mapping = {'Coffee Maker': 'coffee-maker.jpg', 'Laptop Pro 15': 'laptop-pro-15.jpg', 'Power Bank 10000mAh': 'power-bank.jpg', 'Smartphone 128GB': 'smartphone-128gb.jpg', 'Bluetooth Speaker': 'bluetooth-speaker.jpg'}; [(Product.objects.filter(name=name).update(image='products/' + filename), print(name, '->', filename)) for name, filename in mapping.items()]"
Write-Host 'Linking downloaded images to matching Django products...' -ForegroundColor Cyan
python manage.py shell -c $pythonCode
if ($LASTEXITCODE -ne 0) { throw 'Django image-path update failed. The images may be downloaded, but database links were not confirmed.' }

Write-Host ''
Write-Host 'Done. Refresh Shopora with Ctrl+F5 and check the product cards.' -ForegroundColor Green
