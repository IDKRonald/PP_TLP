"""
Funciones gráficas básicas del motor
Requisito: dibujar_ladrillo(), dibujar_texto(), etc.
"""
import pygame
from typing import Tuple

class Graficos:
    """Maneja todas las operaciones de dibujo del motor"""
    
    # Paleta de colores estándar
    COLORES = {
        "negro": (0, 0, 0),
        "blanco": (255, 255, 255),
        "rojo": (255, 0, 0),
        "verde": (0, 255, 0),
        "azul": (0, 0, 255),
        "amarillo": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "naranja": (255, 165, 0),
        "morado": (128, 0, 128),
        "rosa": (255, 192, 203),
        "dorado": (255, 215, 0),
        "gris": (128, 128, 128),
        "gris_oscuro": (50, 50, 50)
    }
    
    def __init__(self, pantalla: pygame.Surface, tam_celda: int = 10):
        """
        Inicializa el sistema gráfico
        
        Args:
            pantalla: Superficie de pygame donde dibujar
            tam_celda: Tamaño en píxeles de cada celda del grid
        """
        self.pantalla = pantalla
        self.tam_celda = tam_celda
        self.fuente = pygame.font.Font(None, 36)
        self.fuente_pequeña = pygame.font.Font(None, 24)
    
    def obtener_color(self, nombre_color: str) -> Tuple[int, int, int]:
        """Convierte un nombre de color a tupla RGB"""
        return self.COLORES.get(nombre_color.lower(), (255, 255, 255))
    
    def dibujar_ladrillo(self, x: int, y: int, color: str, forma: str = "cuadro"):
        """
        Dibuja un ladrillo/bloque en la posición especificada
        
        Args:
            x: Coordenada x en celdas
            y: Coordenada y en celdas
            color: Nombre del color (string del DSL)
            forma: "cuadro" o "circulo"
        """
        px = x * self.tam_celda
        py = y * self.tam_celda
        rgb = self.obtener_color(color)
        
        if forma == "circulo":
            centro = (px + self.tam_celda // 2, py + self.tam_celda // 2)
            radio = self.tam_celda // 2 - 1
            pygame.draw.circle(self.pantalla, rgb, centro, radio)
            # Borde para mejor visibilidad
            pygame.draw.circle(self.pantalla, (0, 0, 0), centro, radio, 1)
        else:  # cuadro por defecto
            rect = pygame.Rect(px, py, self.tam_celda, self.tam_celda)
            pygame.draw.rect(self.pantalla, rgb, rect)
            # Borde más sutil
            borde_color = tuple(max(0, c - 40) for c in rgb)
            pygame.draw.rect(self.pantalla, borde_color, rect, 1)
    
    def dibujar_texto(self, x: int, y: int, texto: str, color: str = "blanco", pequeño: bool = False):
        """
        Dibuja texto en la pantalla
        
        Args:
            x: Coordenada x en píxeles
            y: Coordenada y en píxeles
            texto: String a mostrar
            color: Color del texto
            pequeño: Si True, usa fuente más pequeña
        """
        fuente = self.fuente_pequeña if pequeño else self.fuente
        rgb = self.obtener_color(color)
        superficie = fuente.render(str(texto), True, rgb)
        self.pantalla.blit(superficie, (x, y))
    
    def dibujar_rectangulo(self, x: int, y: int, ancho: int, alto: int, color: str, relleno: bool = True):
        """Dibuja un rectángulo (útil para bordes, UI, etc.)"""
        rgb = self.obtener_color(color)
        rect = pygame.Rect(x, y, ancho, alto)
        if relleno:
            pygame.draw.rect(self.pantalla, rgb, rect)
        else:
            pygame.draw.rect(self.pantalla, rgb, rect, 2)
    
    def limpiar_pantalla(self, color: str = "negro"):
        """Limpia toda la pantalla con un color sólido"""
        rgb = self.obtener_color(color)
        self.pantalla.fill(rgb)
    
    def dibujar_cuadricula(self, ancho_celdas: int, alto_celdas: int, color_linea: str = "gris", opacidad: float = 0.2):
        """
        Dibuja una cuadrícula de referencia con opacidad ajustable
        
        Args:
            ancho_celdas: Ancho en celdas
            alto_celdas: Alto en celdas
            color_linea: Color base de las líneas
            opacidad: Opacidad de 0.0 a 1.0 (0.2 = 20% visible)
        """
        rgb = self.obtener_color(color_linea)
        # Aplicar opacidad reduciendo cada componente RGB
        rgb_opaco = tuple(int(c * opacidad) for c in rgb)
        
        ancho_px = ancho_celdas * self.tam_celda
        alto_px = alto_celdas * self.tam_celda
        
        # Crear superficie temporal con alpha
        superficie_grid = pygame.Surface((ancho_px, alto_px), pygame.SRCALPHA)
        
        # Líneas verticales
        for x in range(0, ancho_px + 1, self.tam_celda):
            pygame.draw.line(superficie_grid, rgb_opaco, (x, 0), (x, alto_px), 1)
        
        # Líneas horizontales
        for y in range(0, alto_px + 1, self.tam_celda):
            pygame.draw.line(superficie_grid, rgb_opaco, (0, y), (ancho_px, y), 1)
        
        # Blit sobre la pantalla principal
        self.pantalla.blit(superficie_grid, (0, 0))