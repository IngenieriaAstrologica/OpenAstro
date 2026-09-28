# OpenAstro — Software libre de astrología profesional (Python 3 + GTK 3) | Free Professional Astrology Software

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](COPYING)
[![Python 3](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![GTK 3](https://img.shields.io/badge/GUI-GTK%203-orange.svg)](https://www.gtk.org/)

> Software de astrología de código abierto, actualizado y corregido para el ecosistema moderno de Python 3 (GTK 3). Fork de **OpenAstro.org 1.1.57** de Pelle van der Scheer.

**OpenAstro** es un programa libre de **astrología profesional**: cartas natales, **revoluciones solares y lunares**, **progresiones secundarias**, **sinastría**, **direcciones primarias topocéntricas** (Polich-Page), **dodecatemorias**, **antiscios**, **estrellas fijas** y **tránsitos** en doble rueda, con **efemérides suizas** (pyswisseph) y atlas offline de ~150.000 ciudades.

**OpenAstro** is a free **professional astrology** program: natal charts, **solar and lunar returns**, **secondary progressions**, **synastry**, **topocentric primary directions** (Polich-Page), **dodecatemoria**, **antiscia**, **fixed stars** and **transits** in bi-wheel charts, with **Swiss Ephemeris** (pyswisseph) and an offline atlas of ~150,000 cities.

> Palabras clave / Keywords: astrología profesional, professional astrology, carta natal, natal chart, revolución solar, solar return, revolución lunar, lunar return, progresiones secundarias, secondary progressions, sinastría, synastry, direcciones primarias, primary directions, dodecatemorias, antiscios, estrellas fijas, fixed stars, tránsitos, transits, Swiss Ephemeris, software astrología libre, free astrology software, OpenAstro, GTK.

## Descarga / Download

```bash
git clone https://github.com/IngenieriaAstrologica/OpenAstro
cd OpenAstro
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-rsvg-2.0
pip install -r requirements.txt
python3 openastro
```

- [Código fuente / Source code](https://github.com/IngenieriaAstrologica/OpenAstro) · [Versiones / Releases](https://github.com/IngenieriaAstrologica/OpenAstro/releases).
- **Windows:** mediante WSL con Ubuntu + WSLg (doble clic en `OpenAstro.bat`).

![OpenAstro](icons/openastro.svg)

[Repositorio en GitHub](https://github.com/IngenieriaAstrologica/OpenAstro)

[Licencia (GPL v3)](COPYING)

---

## ✨ Características Principales
Una herramienta completa para el cálculo y trazado de cartas astrológicas:

- 🪐 **Cartas natales, de tránsitos, sinastría, combinadas y compuestas.**
- 🔄 **Revolución solar, revolución lunar y progresiones secundarias en doble rueda** (natal dentro, carta derivada fuera), con el selector **Chart View** para ver solo la interior, solo la exterior o ambas — también en tránsitos y sinastría (añadido en este fork).
- 🌗 **Carta de dodecatemorias en doble rueda** (radix dentro, dodecatemorias fuera, calculadas como en Morinus).
- 🧭 **Direcciones primarias topocéntricas** (sistema Polich-Page) en doble rueda: clave de Naibod, Ptolomeo o arco solar en AR; directas o conversas; carta eclíptica, ascensional o mixta (como en carta-natal.es); y rejilla con orbe de arco en GMS y marca de aplicativa/separativa.
- ✴️ **Estrellas fijas:** catálogo de 222 estrellas con color según su naturaleza, orbe propio por brillo, anillo exterior sin solapes y tabla en orden zodiacal (datos de Morinus, incluidos y autoinstalables).
- 🪞 **Carta de antiscios y contraantiscios en doble rueda** (eje Cáncer 0°/Capricornio 0°), con tabla imprimible y exportable a PDF.
- ⏱️ **Tránsitos en medida ascensional** (contactos en el mundo por ascensión oblicua) además de la eclíptica habitual.
- ↩️ **Marcas R/S** de planeta retrógrado y estacionario en las ruedas y en la rejilla.
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
- **Ficheros de Swiss Ephemeris** (p. ej. `seas_18.se1`) → colócalos en `~/.openastro.org/swiss_ephemeris`. El catálogo de estrellas fijas (`sefstars.txt`, datos de Morinus) **sí** viene incluido y se instala solo al arrancar si falta.

## 🔧 Cambios de este fork
Respecto a OpenAstro.org 1.1.57, todo detallado en **[CHANGELOG.md](CHANGELOG.md)**.

### Técnicas nuevas
- **Direcciones primarias topocéntricas** (Polich-Page) en doble rueda: claves Naibod/Ptolomeo/arco solar, directas o conversas, cartas eclíptica/ascensional/mixta y rejilla con orbe de arco y marca de aplicativa/separativa.
- **Revolución lunar**, **dodecatemorias** y **antiscios/contraantiscios**, cada una como carta derivada en doble rueda.
- **Tránsitos en medida ascensional** (contactos en el mundo por ascensión oblicua), además de la eclíptica.
- **Estrellas fijas**: catálogo de 222 con color por naturaleza y orbe propio según el brillo.
- **Lotes de Fortuna, Espíritu e Infortunio** (por jipejavier@gmail.com).

### Correcciones
- Los planetas no se dibujaban (todos caían en 18° de Sagitario), y nodos y Lilith tampoco.
- Los números de casa lanzaban `TypeError` y no llegaban a pintarse.
- El nodo sur nunca mostraba su ℞ pese a ser siempre retrógrado.
- Los cuerpos cuyo nombre lleva un espacio —12 de 36, entre ellos el Lote de Fortuna— faltaban en las listas de aspectos.
- Las oposiciones daban un orbe de arco 180° desviado en direcciones primarias.
- El color de cada planeta se leía de una tabla obsoleta que discrepa en 13 de 36 cuerpos.
- Los lotes ignoraban la secta en cartas nocturnas; el diálogo de carta nueva se congelaba en redes lentas.

### Rendimiento
- El atlas de ciudades va indexado: abrir **New Chart** o **Edit Event** pasa de **5,6 s a 0,1 s**.

### Presentación
- Paleta de signos generada en **CIELAB LCh** (elemento = tono, modalidad = luminosidad), con croma ajustado al gamut sRGB y transparencia por capa.
- Cúspides finas discontinuas, con punta de flecha en Ascendente y Medio Cielo en lugar de glifo, y color único en la rueda exterior.
- Glifo **℞** en el color del planeta y marcas **R/S** de retrogradación y estación.
- Rejillas sin nombres redundantes, columnas ajustadas al margen y grados junto a cada planeta en ambas ruedas.
- Coordenadas editables y atlas de ciudades offline incluido.

### Compatibilidad
- Puesta al día para **Python 3** y **GTK 3**, con zonas horarias por `zoneinfo` (sin `pytz`) y lanzador para Windows vía WSL.

## 🔗 Enlaces / Links

- [OpenAstro.org](http://www.openastro.org) — programa original de Pelle van der Scheer del que parte este fork.
- [carta-natal.es](https://carta-natal.es/) — referencia para el cálculo de direcciones primarias (carta eclíptica, ascensional o mixta).
- [Swiss Ephemeris (AstroDienst)](https://www.astro.com/swisseph/) — efemérides de alta precisión ([pyswisseph](https://pypi.org/project/pyswisseph/) en Python).
- [GeoNames](https://www.geonames.org/) — atlas de ciudades online.
- [GTK](https://www.gtk.org/) — interfaz gráfica del programa.

## 🙏 Créditos
- Software original **OpenAstro.org** por **Pelle van der Scheer** — <http://www.openastro.org>
- Cambios del fork (Lotes de Fortuna, Espíritu e Infortunio, entre otros): **jipejavier@gmail.com**
- Símbolo del Lot of Infortune: cruz potenzada de Wikimedia Commons (dominio público).
- Símbolo del Lot of Spirit (ɸ): glifo de Noto Sans (SIL Open Font License 1.1).

## ❓ Preguntas frecuentes / FAQ

**¿OpenAstro es gratis? / Is OpenAstro free?**
Sí, es software libre bajo licencia GPLv3. Yes, it is free software under the GPLv3 license.

**¿Qué programa calcula direcciones primarias topocéntricas gratis? / Which free program calculates topocentric primary directions?**
OpenAstro calcula direcciones primarias topocéntricas (Polich-Page) en doble rueda, con claves de Naibod, Ptolomeo o arco solar.

**¿Funciona en Windows? / Does it work on Windows?**
Sí mediante WSL con Ubuntu + WSLg (`OpenAstro.bat`). Yes, via WSL with Ubuntu + WSLg.

**¿En qué idiomas está disponible? / Which languages are available?**
Multilingüe con numerosos idiomas en `locale/`. Multilingual, with many languages included in `locale/`.

## 📄 Licencia
Distribuido bajo la **GNU General Public License v3** (ver [COPYING](COPYING)).
