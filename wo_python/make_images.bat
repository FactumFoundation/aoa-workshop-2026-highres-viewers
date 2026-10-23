@echo off
rem ---------------------------------------------------------------------
rem  make_images.bat  (optional shortcut, no Photoshop needed)
rem  Makes images\albedo.jpg, relief.jpg and overlay.jpg with vips from
rem  the Selene exports. Then run make_tiles.bat.
rem
rem  Use:  make_images.bat  data\albedo_m1.tif  data\depthmap_m1_shaded.png
rem  Or edit the two default paths below and double-click.
rem ---------------------------------------------------------------------

set "VIPS=C:\vips\vips-dev-8.18\bin\vips.exe"
set "ALBEDO=data\albedo.tif"
set "RELIEF=data\relief.png"
rem Overlay = albedo x (0.4 + 0.6 x relief), the same as Multiply at 60%% in Photoshop
set "SCALE=0.0023529"
set "OFFSET=0.4"

cd /d "%~dp0"
if not "%~1"=="" set "ALBEDO=%~1"
if not "%~2"=="" set "RELIEF=%~2"

if not exist "%VIPS%" ( echo Cannot find vips at %VIPS% & pause & exit /b 1 )
if not exist "%ALBEDO%" ( echo Cannot find the albedo: %ALBEDO% & pause & exit /b 1 )
if not exist "%RELIEF%" ( echo Cannot find the relief: %RELIEF% & pause & exit /b 1 )
if not exist "images" mkdir "images"

echo Albedo: 16-bit to 8-bit sRGB ...
"%VIPS%" icc_transform "%ALBEDO%" "images\albedo.jpg[Q=95]" srgb --embedded --depth 8
echo Relief: to 8-bit greyscale JPEG ...
"%VIPS%" colourspace "%RELIEF%" "images\relief.jpg[Q=95]" b-w
echo Overlay: albedo multiplied by the relief ...
"%VIPS%" linear "images\relief.jpg" "%TEMP%\psv_factor.v" %SCALE% %OFFSET%
"%VIPS%" multiply "images\albedo.jpg" "%TEMP%\psv_factor.v" "%TEMP%\psv_mult.v"
"%VIPS%" cast "%TEMP%\psv_mult.v" "%TEMP%\psv_overlay.v" uchar
"%VIPS%" copy "%TEMP%\psv_overlay.v" "images\overlay.jpg[Q=95]"
del "%TEMP%\psv_factor.v" "%TEMP%\psv_mult.v" "%TEMP%\psv_overlay.v"

echo.
echo Done: images\albedo.jpg, relief.jpg and overlay.jpg. Now run make_tiles.bat
pause
