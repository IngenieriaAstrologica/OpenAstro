#!/bin/bash
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
#Default UI language: Spanish (also makes the gettext "default" lookup
#resolve to es without hitting the fallback in openastro)
export LANG=es_ES.UTF-8
export LANGUAGE=es_ES:es
cd "$(dirname "$(readlink -f "$0")")"
python3 openastro
