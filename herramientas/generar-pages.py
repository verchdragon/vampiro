#!/usr/bin/env python3
"""Genera docs/index.html (versión para GitHub Pages) a partir de web/index.html.

web/index.html es la versión que se publica en Claude: no trae <!doctype>, <head>
ni <body> porque Claude los agrega al publicar. GitHub Pages necesita el documento
completo, así que este script envuelve el mismo juego con esas etiquetas.
Uso:  python3 herramientas/generar-pages.py
"""
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent

cabecera = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="{color}">
<!-- Permite "Agregar a pantalla de inicio" y abrir el juego a pantalla completa -->
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="description" content="{descripcion}">
<style>
  /* Lo mismo que agrega Claude al publicar: márgenes seguros del celular y reinicio básico */
  :root { color-scheme: dark; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); box-sizing: border-box; }
  body { margin: 0; font: 14px system-ui, sans-serif; }
  img { max-width: 100%; }
  [hidden] { display: none !important; }
</style>
</head>
<body>
"""
pie = "\n</body>\n</html>\n"

def generar(origen, destino, descripcion, color):
    """Envuelve un juego (sin <head>) con el documento completo para GitHub Pages."""
    juego = (raiz / origen).read_text(encoding='utf-8')
    cab = cabecera.replace('{descripcion}', descripcion).replace('{color}', color)
    archivo = raiz / destino
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(cab + juego + pie, encoding='utf-8')
    print('Generado', archivo.relative_to(raiz))


# VAMPIRO → https://verchdragon.github.io/vampiro/
generar('web/index.html', 'docs/index.html',
        'VAMPIRO: sobrevive 10 noches. Juego de celular con ranking entre amigos.', '#0b0916')

# Mansión Embrujada → https://verchdragon.github.io/vampiro/mansion/
generar('mansion/index.html', 'docs/mansion/index.html',
        'Mansión Embrujada: juego de detective de caricatura. Encuentra pistas y descubre qué fantasma miente.', '#251a40')
# Su música (licencia libre CC0) va junto al juego
import shutil
shutil.copytree(raiz / 'mansion' / 'sonidos', raiz / 'docs' / 'mansion' / 'sonidos', dirs_exist_ok=True)

# Escuadrón Cometa → https://verchdragon.github.io/vampiro/naves/
generar('naves/index.html', 'docs/naves/index.html',
        'Escuadrón Cometa: detén a la flota de aliens antes de que llegue a la Tierra.', '#070a1f')
shutil.copytree(raiz / 'naves' / 'sonidos', raiz / 'docs' / 'naves' / 'sonidos', dirs_exist_ok=True)

# Carrera Peluda → https://verchdragon.github.io/vampiro/carrera/
generar('carrera/index.html', 'docs/carrera/index.html',
        'Carrera Peluda: corre, salta y usa poderes para ganarle a tres rivales.', '#8fd6ff')
shutil.copytree(raiz / 'carrera' / 'sonidos', raiz / 'docs' / 'carrera' / 'sonidos', dirs_exist_ok=True)

# Pipo Saltarín → https://verchdragon.github.io/vampiro/pipo/
generar('pipo/index.html', 'docs/pipo/index.html',
        'Pipo Saltarín: juego de plataformas. Salta, aplasta enemigos y recupera la campana.', '#9fe3ff')
shutil.copytree(raiz / 'pipo' / 'sonidos', raiz / 'docs' / 'pipo' / 'sonidos', dirs_exist_ok=True)
