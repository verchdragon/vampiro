#!/usr/bin/env python3
"""Genera docs/index.html (versión para GitHub Pages) a partir de web/index.html.

web/index.html es la versión que se publica en Claude: no trae <!doctype>, <head>
ni <body> porque Claude los agrega al publicar. GitHub Pages necesita el documento
completo, así que este script envuelve el mismo juego con esas etiquetas.
Uso:  python3 herramientas/generar-pages.py
"""
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
juego = (raiz / 'web' / 'index.html').read_text(encoding='utf-8')

cabecera = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b0916">
<!-- Permite "Agregar a pantalla de inicio" y abrir el juego a pantalla completa -->
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="description" content="VAMPIRO: sobrevive 10 noches. Juego de celular con ranking entre amigos.">
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

destino = raiz / 'docs' / 'index.html'
destino.parent.mkdir(exist_ok=True)
destino.write_text(cabecera + juego + pie, encoding='utf-8')
print('Generado', destino.relative_to(raiz))
