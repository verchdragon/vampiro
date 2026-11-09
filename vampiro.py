"""
VAMPIRO - Juego de supervivencia nocturna hecho con pygame.

Objetivo:
    Eres un vampiro. Tu sangre baja con el tiempo: muerde aldeanos para
    recuperarla y esquiva a los cazadores, que son cada vez más.
    Sobrevive el mayor tiempo posible.

Controles:
    Flechas / WASD  -> moverse
    ESPACIO         -> forma de murciélago (impulso rápido, cuesta sangre)
    R               -> reiniciar tras perder
    ESC             -> salir
"""

import random
import sys

import pygame

# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------
ANCHO, ALTO = 900, 600          # Tamaño de la ventana
FPS = 60                        # Cuadros por segundo

# Colores (R, G, B)
NEGRO = (10, 8, 20)
GRIS = (60, 60, 80)
BLANCO = (240, 240, 240)
ROJO = (200, 20, 40)
ROJO_OSCURO = (90, 0, 15)
PIEL = (230, 190, 150)
AZUL = (70, 110, 200)
MARRON = (120, 80, 40)
AMARILLO = (250, 220, 90)
MORADO = (110, 40, 140)

# Parámetros de juego
SANGRE_MAX = 100.0
PERDIDA_SANGRE_SEG = 4.0        # Sangre que se pierde por segundo
SANGRE_POR_MORDIDA = 25.0       # Sangre que da cada aldeano
DANO_CAZADOR = 30.0             # Sangre que quita un cazador al tocarte
COSTO_MURCIELAGO = 10.0         # Sangre que cuesta el impulso
INVULNERABLE_SEG = 1.0          # Tiempo de invulnerabilidad tras un golpe


def distancia(a, b):
    """Distancia euclidiana entre dos vectores pygame."""
    return (a - b).length()


def limitar_a_pantalla(pos, radio):
    """Mantiene una posición dentro de los bordes de la ventana."""
    pos.x = max(radio, min(ANCHO - radio, pos.x))
    pos.y = max(radio, min(ALTO - radio, pos.y))


def punto_en_borde():
    """Devuelve un punto aleatorio en el borde de la pantalla (para spawns)."""
    lado = random.choice(["arriba", "abajo", "izq", "der"])
    if lado == "arriba":
        return pygame.Vector2(random.uniform(0, ANCHO), 15)
    if lado == "abajo":
        return pygame.Vector2(random.uniform(0, ANCHO), ALTO - 15)
    if lado == "izq":
        return pygame.Vector2(15, random.uniform(0, ALTO))
    return pygame.Vector2(ANCHO - 15, random.uniform(0, ALTO))


# ---------------------------------------------------------------------------
# Entidades
# ---------------------------------------------------------------------------
class Vampiro:
    """El jugador."""

    RADIO = 16
    VELOCIDAD = 220             # píxeles por segundo
    VEL_MURCIELAGO = 520        # velocidad durante el impulso
    DURACION_MURCIELAGO = 0.35  # segundos que dura el impulso

    def __init__(self):
        self.pos = pygame.Vector2(ANCHO / 2, ALTO / 2)
        self.direccion = pygame.Vector2(1, 0)   # última dirección de movimiento
        self.sangre = SANGRE_MAX
        self.t_murcielago = 0.0                 # tiempo restante de impulso
        self.t_invulnerable = 0.0               # tiempo restante de invulnerabilidad

    @property
    def es_murcielago(self):
        return self.t_murcielago > 0

    def activar_murcielago(self):
        """Inicia el impulso si hay sangre suficiente y no está ya activo."""
        if not self.es_murcielago and self.sangre > COSTO_MURCIELAGO:
            self.sangre -= COSTO_MURCIELAGO
            self.t_murcielago = self.DURACION_MURCIELAGO

    def actualizar(self, dt, teclas):
        # Leer dirección desde el teclado (flechas o WASD)
        mov = pygame.Vector2(
            (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - (teclas[pygame.K_LEFT] or teclas[pygame.K_a]),
            (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - (teclas[pygame.K_UP] or teclas[pygame.K_w]),
        )
        if mov.length_squared() > 0:
            mov = mov.normalize()
            self.direccion = mov

        # En forma de murciélago se avanza rápido en la última dirección
        if self.es_murcielago:
            self.pos += self.direccion * self.VEL_MURCIELAGO * dt
            self.t_murcielago -= dt
        else:
            self.pos += mov * self.VELOCIDAD * dt

        limitar_a_pantalla(self.pos, self.RADIO)

        # La sangre baja constantemente y los temporizadores avanzan
        self.sangre -= PERDIDA_SANGRE_SEG * dt
        self.t_invulnerable = max(0.0, self.t_invulnerable - dt)

    def recibir_golpe(self):
        """Resta sangre si no es invulnerable. Devuelve True si recibió daño."""
        if self.t_invulnerable > 0 or self.es_murcielago:
            return False  # el murciélago es intocable
        self.sangre -= DANO_CAZADOR
        self.t_invulnerable = INVULNERABLE_SEG
        return True

    def dibujar(self, pantalla):
        # Parpadeo mientras es invulnerable
        if self.t_invulnerable > 0 and int(self.t_invulnerable * 10) % 2 == 0:
            return
        x, y = int(self.pos.x), int(self.pos.y)
        if self.es_murcielago:
            # Murciélago: cuerpo pequeño con dos alas triangulares
            pygame.draw.polygon(pantalla, MORADO, [(x - 22, y - 8), (x, y), (x - 10, y + 6)])
            pygame.draw.polygon(pantalla, MORADO, [(x + 22, y - 8), (x, y), (x + 10, y + 6)])
            pygame.draw.circle(pantalla, NEGRO, (x, y), 7)
            pygame.draw.circle(pantalla, ROJO, (x, y), 7, 2)
        else:
            # Vampiro: capa roja, cara pálida y ojos rojos
            pygame.draw.circle(pantalla, ROJO_OSCURO, (x, y), self.RADIO + 4)
            pygame.draw.circle(pantalla, BLANCO, (x, y), self.RADIO)
            pygame.draw.circle(pantalla, ROJO, (x - 5, y - 3), 3)
            pygame.draw.circle(pantalla, ROJO, (x + 5, y - 3), 3)
            # Colmillos
            pygame.draw.polygon(pantalla, NEGRO, [(x - 4, y + 5), (x - 2, y + 10), (x, y + 5)])
            pygame.draw.polygon(pantalla, NEGRO, [(x, y + 5), (x + 2, y + 10), (x + 4, y + 5)])


class Aldeano:
    """Presa: deambula y huye si el vampiro se acerca."""

    RADIO = 11
    VELOCIDAD = 90
    VEL_HUIDA = 150
    RANGO_MIEDO = 140

    def __init__(self):
        self.pos = pygame.Vector2(random.uniform(40, ANCHO - 40), random.uniform(40, ALTO - 40))
        self.dir = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
        self.t_cambio = random.uniform(1, 3)  # cuándo cambiar de rumbo

    def actualizar(self, dt, vampiro):
        lejania = self.pos - vampiro.pos
        if 0 < lejania.length() < self.RANGO_MIEDO:
            # Huir en dirección opuesta al vampiro
            self.pos += lejania.normalize() * self.VEL_HUIDA * dt
        else:
            # Paseo aleatorio, cambiando de dirección de vez en cuando
            self.t_cambio -= dt
            if self.t_cambio <= 0:
                self.dir = self.dir.rotate(random.uniform(-120, 120))
                self.t_cambio = random.uniform(1, 3)
            self.pos += self.dir * self.VELOCIDAD * dt

        # Rebotar en los bordes
        if not (self.RADIO < self.pos.x < ANCHO - self.RADIO):
            self.dir.x *= -1
        if not (self.RADIO < self.pos.y < ALTO - self.RADIO):
            self.dir.y *= -1
        limitar_a_pantalla(self.pos, self.RADIO)

    def dibujar(self, pantalla):
        x, y = int(self.pos.x), int(self.pos.y)
        pygame.draw.circle(pantalla, AZUL, (x, y + 6), self.RADIO)  # cuerpo
        pygame.draw.circle(pantalla, PIEL, (x, y - 4), 8)           # cabeza


class Cazador:
    """Enemigo: persigue al vampiro."""

    RADIO = 14

    def __init__(self, velocidad):
        self.pos = punto_en_borde()
        self.velocidad = velocidad

    def actualizar(self, dt, vampiro):
        hacia = vampiro.pos - self.pos
        if hacia.length_squared() > 0:
            self.pos += hacia.normalize() * self.velocidad * dt

    def dibujar(self, pantalla):
        x, y = int(self.pos.x), int(self.pos.y)
        pygame.draw.circle(pantalla, MARRON, (x, y), self.RADIO)
        # Sombrero de ala ancha
        pygame.draw.rect(pantalla, NEGRO, (x - 16, y - 12, 32, 5))
        pygame.draw.rect(pantalla, NEGRO, (x - 8, y - 22, 16, 11))
        # Cruz de plata en el pecho
        pygame.draw.line(pantalla, AMARILLO, (x, y - 4), (x, y + 10), 3)
        pygame.draw.line(pantalla, AMARILLO, (x - 5, y + 1), (x + 5, y + 1), 3)


# ---------------------------------------------------------------------------
# Juego principal
# ---------------------------------------------------------------------------
class Juego:
    MAX_ALDEANOS = 6

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vampiro")
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont(None, 30)
        self.fuente_grande = pygame.font.SysFont(None, 72)
        # Estrellas fijas de fondo (posiciones aleatorias generadas una vez)
        self.estrellas = [(random.randrange(ANCHO), random.randrange(ALTO)) for _ in range(80)]
        self.mejor = 0
        self.reiniciar()

    def reiniciar(self):
        """Prepara una partida nueva."""
        self.vampiro = Vampiro()
        self.aldeanos = [Aldeano() for _ in range(self.MAX_ALDEANOS)]
        self.cazadores = []
        self.tiempo = 0.0           # segundos sobrevividos
        self.mordidas = 0
        self.t_spawn_cazador = 3.0  # cuenta regresiva para el siguiente cazador
        self.terminado = False

    @property
    def puntaje(self):
        # 1 punto por segundo + 10 por mordida
        return int(self.tiempo) + self.mordidas * 10

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                if evento.key == pygame.K_SPACE and not self.terminado:
                    self.vampiro.activar_murcielago()
                if evento.key == pygame.K_r and self.terminado:
                    self.reiniciar()
        return True

    def actualizar(self, dt):
        if self.terminado:
            return

        self.tiempo += dt
        self.vampiro.actualizar(dt, pygame.key.get_pressed())

        # Aparición de cazadores: cada vez más frecuentes y rápidos
        self.t_spawn_cazador -= dt
        if self.t_spawn_cazador <= 0:
            velocidad = min(200, 90 + self.tiempo * 1.5)
            self.cazadores.append(Cazador(velocidad))
            self.t_spawn_cazador = max(2.0, 7.0 - self.tiempo / 15)

        for aldeano in self.aldeanos:
            aldeano.actualizar(dt, self.vampiro)
        for cazador in self.cazadores:
            cazador.actualizar(dt, self.vampiro)

        # Mordidas: tocar un aldeano lo consume y devuelve sangre
        for aldeano in self.aldeanos[:]:
            if distancia(aldeano.pos, self.vampiro.pos) < aldeano.RADIO + Vampiro.RADIO:
                self.aldeanos.remove(aldeano)
                self.vampiro.sangre = min(SANGRE_MAX, self.vampiro.sangre + SANGRE_POR_MORDIDA)
                self.mordidas += 1

        # Reponer aldeanos para que nunca falten presas
        while len(self.aldeanos) < self.MAX_ALDEANOS:
            self.aldeanos.append(Aldeano())

        # Golpes de cazadores
        for cazador in self.cazadores:
            if distancia(cazador.pos, self.vampiro.pos) < cazador.RADIO + Vampiro.RADIO:
                if self.vampiro.recibir_golpe():
                    # Empujar al cazador hacia atrás para no recibir golpes seguidos
                    empuje = cazador.pos - self.vampiro.pos
                    if empuje.length_squared() > 0:
                        cazador.pos += empuje.normalize() * 60

        # Fin de la partida
        if self.vampiro.sangre <= 0:
            self.vampiro.sangre = 0
            self.terminado = True
            self.mejor = max(self.mejor, self.puntaje)

    def dibujar_hud(self):
        """Barra de sangre y textos de puntaje."""
        # Barra de sangre
        pygame.draw.rect(self.pantalla, GRIS, (20, 20, 204, 24), border_radius=4)
        ancho = int(200 * self.vampiro.sangre / SANGRE_MAX)
        pygame.draw.rect(self.pantalla, ROJO, (22, 22, ancho, 20), border_radius=4)
        self.pantalla.blit(self.fuente.render("Sangre", True, BLANCO), (232, 22))

        texto = f"Tiempo: {int(self.tiempo)}s   Mordidas: {self.mordidas}   Puntos: {self.puntaje}"
        self.pantalla.blit(self.fuente.render(texto, True, BLANCO), (20, 54))

    def dibujar_fin(self):
        """Pantalla de game over."""
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((0, 0, 0, 170))  # oscurecer el fondo
        self.pantalla.blit(capa, (0, 0))
        lineas = [
            (self.fuente_grande, "AMANECIÓ...", ROJO),
            (self.fuente, f"Puntos: {self.puntaje}    Récord: {self.mejor}", BLANCO),
            (self.fuente, "Pulsa R para volver a la noche o ESC para salir", BLANCO),
        ]
        y = ALTO // 2 - 70
        for fuente, texto, color in lineas:
            sup = fuente.render(texto, True, color)
            self.pantalla.blit(sup, sup.get_rect(center=(ANCHO // 2, y)))
            y += 60

    def dibujar(self):
        self.pantalla.fill(NEGRO)
        for estrella in self.estrellas:
            self.pantalla.set_at(estrella, BLANCO)
        pygame.draw.circle(self.pantalla, (230, 230, 200), (ANCHO - 80, 80), 40)  # luna

        for aldeano in self.aldeanos:
            aldeano.dibujar(self.pantalla)
        for cazador in self.cazadores:
            cazador.dibujar(self.pantalla)
        self.vampiro.dibujar(self.pantalla)

        self.dibujar_hud()
        if self.terminado:
            self.dibujar_fin()
        pygame.display.flip()

    def ejecutar(self, max_cuadros=None):
        """Bucle principal. max_cuadros sirve para pruebas automáticas."""
        cuadros = 0
        while self.manejar_eventos():
            dt = self.reloj.tick(FPS) / 1000  # segundos desde el último cuadro
            self.actualizar(dt)
            self.dibujar()
            cuadros += 1
            if max_cuadros and cuadros >= max_cuadros:
                break
        pygame.quit()


if __name__ == "__main__":
    Juego().ejecutar()
    sys.exit()
