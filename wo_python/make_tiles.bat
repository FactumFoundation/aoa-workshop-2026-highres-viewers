@echo off
rem ---------------------------------------------------------------------
rem  make_tiles.bat
rem  Cuts images\albedo, relief and overlay into Zoomify tiles in
rem  viewer\tiles and writes the image size into the viewer.
rem  Double-click to run. Running it again rebuilds the tiles.
rem ---------------------------------------------------------------------

rem Where vips.exe is (see README.md, step 1)
set "VIPS=C:\vips\vips-dev-8.18\bin\vips.exe"
rem Extension of the input images: jpg, or tif for pieces over 30,000 px
set "EXT=jpg"

cd /d "%~dp0"

if not exist "%VIPS%" (
  echo Cannot find vips at %VIPS%
  echo Install it as explained in README.md, or fix the VIPS line in this file.
  pause
  exit /b 1
)
if not exist "viewer\tiles" mkdir "viewer\tiles"

for %%N in (albedo relief overlay) do (
  if exist "images\%%N.%EXT%" (
    echo Tiling %%N.%EXT% ...
    if exist "viewer\tiles\%%N" rmdir /s /q "viewer\tiles\%%N"
    "%VIPS%" dzsave "images\%%N.%EXT%" "viewer\tiles\%%N" --layout zoomify --suffix .jpg[Q=90]
  ) else (
    echo Missing images\%%N.%EXT% - skipped.
  )
)

if exist "viewer\tiles\albedo\ImageProperties.xml" (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$x=[xml](Get-Content 'viewer\tiles\albedo\ImageProperties.xml'); $w=$x.IMAGE_PROPERTIES.WIDTH; $h=$x.IMAGE_PROPERTIES.HEIGHT; foreach ($p in 'viewer\viewer.html','viewer\viewer_minimal.html') { $f=(Resolve-Path $p).Path; $c=[IO.File]::ReadAllText($f); $c=$c -replace 'width: (null|\d+),',('width: '+$w+','); $c=$c -replace 'height: (null|\d+),',('height: '+$h+','); [IO.File]::WriteAllText($f,$c) }; Write-Host ('Image size written into the viewer: '+$w+' x '+$h+' px')"
)

echo.
echo Done. Double-click viewer\viewer.html
pause
