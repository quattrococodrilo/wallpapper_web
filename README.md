## Wallpapper_web

Script que extrae una imagen de https://www.pexels.com/ según el tamaño de la pantalla y la asigna como fondo de pantalla.

### Uso
En setting.py cambiar los valores de images_dir (en dónde se guardarán las imágenes) y url (la url de búsqueda de imágenes, p.j.: https://www.pexels.com/search/landscape/)

Ejecutar tests.py

**Notas**:
-  Por ahora solo lo he probado en Ubuntu 18.04 con Gnome.
- Usa Python 3
- Requiere Imagemagick
- Instalar las dependencias en requirements.txt 

**TODOS**:
- ~~Agregar a la foto el nombre del autor y su cuenta en pexel.~~
- ~~Crear una base de datos en YAML para evitar que se repitan las imágenes.~~
- Agregar soporte para Windows.
- Pasar el script a una aplicación de línea de comandos con click
