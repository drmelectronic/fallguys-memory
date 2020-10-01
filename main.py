import os
import random

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import pygame

FPS = 15
# DISPLAY = pygame.display.set_mode((1900, 1080), pygame.FULLSCREEN)
DISPLAY = pygame.display.set_mode((1900, 1060))
FRUTAS = [
    'manzana',
    'cereza',
    'platano',
    'naranja',
    'sandia',
    'uva'
]
LEVELS = [2, 3, 4, 5, 6]
MARGIN = 20
WIDTH_CARD = 300
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
PLAY = True


class Game:

    def __init__(self, x, y):
        pygame.init()
        self.X = x
        self.Y = y
        logo = pygame.image.load(os.path.join('images/logo.png'))
        pygame.display.set_icon(logo)
        pygame.display.set_caption("Fall Guys Memory")
        self.mostrando = False
        self.buscar = None
        self.cards = []
        self.opciones = []
        self.time_oculto = 4
        self.time_mostrado = 14
        self.cronometro = Cronometro(1350 + 150, 250, 200, 100, '0', (249, 206, 60), 120)
        self.cronometro.inicializar_cards = self.inicializar_cards
        self.cronometro.termino_tiempo = self.termino_tiempo
        self.cronometro.liberar_cards = self.liberar_cards

        self.level1_button = Button(1150 + 150, 800, 120, 80, '1', color=(255, 255, 100), size=50)
        self.level2_button = Button(1270 + 150, 800, 120, 80, '2', color=(100, 255, 255), size=50)
        self.level3_button = Button(1390 + 150, 800, 120, 80, '3', color=(255, 100, 255), size=50)
        self.level4_button = Button(1510 + 150, 800, 120, 80, '4', color=(100, 255, 255), size=50)
        self.level5_button = Button(1630 + 150, 800, 120, 80, '5', color=(255, 255, 100), size=50)
        self.level1_button.set_callback(self.set_nivel, 0)
        self.level2_button.set_callback(self.set_nivel, 1)
        self.level3_button.set_callback(self.set_nivel, 2)
        self.level4_button.set_callback(self.set_nivel, 3)
        self.level5_button.set_callback(self.set_nivel, 4)
        self.start_button = Button(1150 + 150, 930, 300, 80, 'START', color=(100, 255, 100), size=35)
        self.start_button.set_callback(self.cronometro.init)
        self.finish_button = Button(1450 + 150, 930, 300, 80, 'FINISH', color=(255, 100, 100), size=35)
        self.finish_button.set_callback(self.close)
        self.nivel = Button(1150 + 150, 70, 600, 120, 'NIVEL', color=(5, 180, 252), size=80)
        self.nivel.set_color_font((255, 39, 144))
        self.set_nivel(0)

    def close(self):
        reactor.stop()
        pygame.quit()

    def set_nivel(self, nivel):
        self.nivel.set_text(f'NIVEL {nivel + 1}')
        level = LEVELS[nivel]
        frutas = list(FRUTAS)
        self.opciones = []
        self.cards = []

        for r in range(level):
            choice = random.choice(frutas)
            index = frutas.index(choice)
            frutas.pop(index)
            self.opciones.append(choice)

        ganador = random.choice(self.opciones)
        self.buscar = Card(4.5, 1, ganador, True)

        escogidos = []
        minimo = int(12 / len(self.opciones))
        for o in self.opciones:
            for g in range(minimo):
                escogidos.append(o)

        self.opciones.remove(ganador)
        for c in range(12 - len(escogidos)):
            choice = random.choice(self.opciones)
            escogidos.append(choice)

        random.shuffle(escogidos)
        for i in range(self.X):
            for j in range(self.Y):
                choice = escogidos.pop()
                self.cards.append(Card(i, j, choice, choice == ganador))

    def display(self):
        self.process_events()
        DISPLAY.fill((248, 142, 190))
        for c in self.cards:
            c.display()
        self.cronometro.display()
        self.start_button.display()
        self.finish_button.display()
        self.buscar.display()
        self.level1_button.display()
        self.level2_button.display()
        self.level3_button.display()
        self.level4_button.display()
        self.level5_button.display()
        self.nivel.display()

        pygame.display.flip()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                self.start_button.check_click(pos)
                self.finish_button.check_click(pos)
                self.level1_button.check_click(pos)
                self.level2_button.check_click(pos)
                self.level3_button.check_click(pos)
                self.level4_button.check_click(pos)
                self.level5_button.check_click(pos)

    def ocultar_todos(self):
        self.mostrando = False
        for c in self.cards:
            c.mostrar(False)

    def inicializar_cards(self):
        self.ocultar_todos()
        self.buscar.mostrar(False)

    def termino_tiempo(self):
        self.ocultar_todos()
        self.buscar.mostrar(True)

    def liberar_cards(self):
        for c in self.cards:
            c.check_correcto()

    def mostrar_ocultar(self):
        if self.cronometro.status == 'INICIO':
            if self.mostrando:
                self.ocultar_todos()
            else:
                self.mostrando = True
                for c in self.cards:
                    c.mostrar(random.choice([True, False]))
            self.cronometro.clock()
        elif self.cronometro.status == 'FIN':
            self.cronometro.clock()


class TextField:

    def __init__(self, x, y, texto, size, color):
        self.font = pygame.font.SysFont("Arial", size)
        self.x = x
        self.y = y
        self.color = color
        self.set_text(texto)

    def set_text(self, texto):
        self.texto = self.font.render(texto, True, BLACK)

    def display(self):
        DISPLAY.blit(self.texto, (self.x, self.y))

    def check_click(self, pos):
        if self.rectangulo.collidepoint(pos):
            self.clicked()


class Button:

    def __init__(self, x, y, w, h, texto, color, size):
        self.text = ''
        self.X = 0
        self.Y = 0
        self.args = []
        self.color_font = BLACK
        self.font = pygame.font.SysFont("Arial", size)
        self.is_clicked = False
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.texto = texto
        self.render()
        self.rectangulo = pygame.Rect(x, y, w, h)

    def set_callback(self, callback, *args):
        self.callback = callback
        self.args = args

    def clicked(self):
        self.callback(*self.args)

    def callback(self, *args):
        return

    def set_color_font(self, color):
        self.color_font = color
        self.render()

    def set_text(self, texto):
        self.texto = texto
        self.render()

    def render(self):
        self.text = self.font.render(self.texto, True, self.color_font)
        width = self.text.get_width()
        height = self.text.get_height()
        self.X = self.x - width / 2 + self.w / 2
        self.Y = self.y - height / 2 + self.h / 2

    def display(self):
        pygame.draw.rect(DISPLAY, self.color, self.rectangulo)
        DISPLAY.blit(self.text, (self.X, self.Y))

    def check_click(self, pos):
        if self.rectangulo.collidepoint(pos):
            self.clicked()


class Cronometro(Button):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_color_font(WHITE)
        self.tiempo = 0
        self.status = 'QUIET'
        self.font = pygame.font.SysFont("Arial", 60)

    def inicializar_cards(self):
        pass

    def termino_tiempo(self):
        pass

    def liberar_cards(self):
        pass

    def init(self):
        if self.status == 'QUIET':
            self.status = 'INICIO'
            self.inicializar_cards()
            self.set(14)

    def set(self, tiempo):
        self.tiempo = tiempo
        self.set_text(str(tiempo))
        self.display()

    def clock(self):
        if self.status == 'INICIO':
            if self.tiempo == 0:
                self.status = 'FIN'
                self.set(5)
                self.termino_tiempo()
            else:
                self.set(self.tiempo - 1)
        elif self.status == 'FIN':
            if self.tiempo == 0:
                self.status = 'QUIET'
                self.liberar_cards()
            else:
                self.set(self.tiempo - 1)


class Card:

    def __init__(self, x, y, fruta, correcto):
        self.x = x
        self.y = y
        self.fruta = fruta
        self.image = pygame.image.load(f'images/{fruta}.png')
        self.tile = pygame.image.load(f'images/tile.png')
        self.error_img = pygame.image.load(f'images/error.png')
        self.mostrado = False
        self.correcto = correcto
        self.show_error = False
        self.rectangulo = pygame.Rect(self.get_x_pos(), self.get_y_pos() + 50, WIDTH_CARD, WIDTH_CARD)

    def get_x_pos(self):
        return MARGIN + (self.x * (WIDTH_CARD + MARGIN))

    def get_y_pos(self):
        return MARGIN + (self.y * (WIDTH_CARD + MARGIN))

    def mostrar(self, valor):
        self.mostrado = valor

    def check_correcto(self):
        if not self.correcto:
            self.show_error = True
        else:
            self.mostrado = True

    def display(self):
        if self.show_error:
            return
        if self.mostrado:
            pygame.draw.rect(DISPLAY, WHITE, self.rectangulo)
            DISPLAY.blit(self.image, (self.get_x_pos(), self.get_y_pos() + 50))
        else:
            pygame.draw.rect(DISPLAY, GRAY, self.rectangulo)
            DISPLAY.blit(self.tile, (self.get_x_pos(), self.get_y_pos() + 50))


if __name__ == '__main__':
    game = Game(4, 3)
    clock = LoopingCall(game.display)
    clock.start(1 / FPS)
    switch = LoopingCall(game.mostrar_ocultar)
    switch.start(1)

    reactor.run()
