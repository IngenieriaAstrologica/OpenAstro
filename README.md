# 🌌 OpenAstro — Edición Python 3

> Software de astrología de código abierto, actualizado y corregido para el ecosistema moderno de Python 3 (GTK 3). Fork de **OpenAstro.org 1.1.57** de Pelle van der Scheer.

![OpenAstro](icons/openastro.svg)

[Repositorio en GitHub](https://github.com/IngenieriaAstrologica/OpenAstro)

[Licencia (GPL v3)](COPYING)

---

## ✨ Características Principales
Una herramienta completa para el cálculo y trazado de cartas astrológicas:

- 🪐 **Cartas natales, de tránsitos, sinastría, combinadas y compuestas.**
- ☄️ **Cuerpos adicionales:** Quirón, Pholus, Ceres, Palas, Juno y Vesta.
- ⊗ **Puntos y Lotes:** Nodos Norte/Sur, Lilith y los **Lotes de Fortuna, Espíritu e Infortunio** (añadidos en este fork).
- 🌍 **Atlas de ciudades:** online (geonames) y offline (~150.000 ciudades, incluido).
- 🎨 **Personalizable:** planetas y aspectos configurables, colores de signos por elemento.
- 💾 **Importar / exportar:** skylendar (`*.skif`), oroboros (`*.xml`), astrolog32 (`*.dat`), Zet8 (`*.zbs`); guardar como PNG, JPG y SVG.
- 🔭 **Efemérides Suizas** mediante `pyswisseph`.
- 🌐 **Multilingüe:** numerosos idiomas incluidos en `locale/`.

## 🚀 Instalación Rápida
Requiere **Python 3.9+** con PyGObject (GTK 3 y librsvg 2), pycairo y pyswisseph. Las zonas horarias usan `zoneinfo` de la biblioteca estándar (sin `pytz`).

### Debian / Ubuntu
```bash
git clone https://github.com/IngenieriaAstrologica/OpenAstro
cd OpenAstro
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-rsvg-2.0
pip install -r requirements.txt
python3 openastro
```

> 💡 La exportación a **PNG/JPG** usa el comando `convert` de ImageMagick (opcional): `sudo apt install imagemagick`. La exportación a SVG es nativa.

### Windows (mediante WSL)
Con **Ubuntu + WSLg** instalado, haz doble clic en **`OpenAstro.bat`** (que ejecuta `launch.sh`).

> ⚠️ **La ventana no aparece / sale minimizada bajo WSL:** es un problema del
> compositor de WSLg (afecta a *todas* las apps GUI, no solo a esta — se puede
> comprobar con `xclock`), no del programa. Se soluciona reiniciando WSLg desde
> PowerShell de Windows: `wsl --update` y `wsl --shutdown`, y volver a abrir WSL.

## 💾 Bases de datos incluidas
- **`famous.sql`** (~364 KB) — base de datos de personajes famosos.
- **`geonames.sql`** (~31 MB) — atlas de ciudades offline (~150.000 lugares) para la búsqueda de ciudades.

## 📂 No incluido en el repositorio
- **Ficheros de Swiss Ephemeris** (p. ej. `seas_18.se1`) → colócalos en `~/.openastro.org/swiss_ephemeris`.

## 🔧 Cambios de este fork
Los cambios respecto a OpenAstro.org 1.1.57 están detallados en **[CHANGELOG.md](CHANGELOG.md)**: corrección del dibujado de planetas, nodos y Lilith; coordenadas editables; colores de signos por elemento; y la incorporación de los **Lotes de Fortuna, Espíritu e Infortunio** (por jipejavier@gmail.com).

## 🙏 Créditos
- Software original **OpenAstro.org** por **Pelle van der Scheer** — <http://www.openastro.org>
- Cambios del fork (Lotes de Fortuna, Espíritu e Infortunio, entre otros): **jipejavier@gmail.com**
- Símbolo del Lot of Infortune: cruz potenzada de Wikimedia Commons (dominio público).
- Símbolo del Lot of Spirit (ɸ): glifo de Noto Sans (SIL Open Font License 1.1).

## 📄 Licencia
Distribuido bajo la **GNU General Public License v3** (ver [COPYING](COPYING)).
