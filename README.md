## Wallpapper_web

Script que extrae una imagen de https://www.pexels.com/ según el tamaño de la pantalla y la asigna como fondo de pantalla.

### Uso
En el archivo setWallpapper.py en la llamda a la función **run** se debe pasar como parámetro la dirección absoluta del directorio donde se guardarán las imágenes.

```python
. . .
if __name__ == '__main__':
    run('/La/dirección/de/tu/directorio')
```


**Notas**:
-  Por ahora solo funciona para Ubuntu 18.04 con Gnome.
- Usa Python 3

**TODOS**:
- ~~Agregar a la foto el nombre del autor y su cuenta en pexel.~~
- ~~Crear una base de datos en YAML para evitar que se repitan las imágenes.~~
- Agregar soporte para Windows.
- Pasar el script a una aplicación de línea de comandos con click
