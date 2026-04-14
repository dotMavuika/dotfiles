#!/bin/bash

# Ruta donde se guardará temporalmente la captura
CAPTURE_PATH="/tmp/screenshot.png"

# Tomar la captura de pantalla y guardarla en un archivo temporal
scrot -s "$CAPTURE_PATH"

# Copiar la captura al portapapeles en formato PNG
xclip -selection clipboard -t image/png < "$CAPTURE_PATH"

# Eliminar la captura de pantalla del archivo temporal
rm "$CAPTURE_PATH"

# Mostrar una notificación

