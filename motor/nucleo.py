"""
Núcleo del Motor - Game Loop Principal
Requisitos de la Entrega 2:
- Ventana 640x480
- Game loop: eventos → actualización → renderizado
"""
import pygame
from typing import Optional, Callable
from .graficos import Graficos
from .entrada import ControladorEntrada
from .interprete import InterpreteAST

class Motor:
    """Motor de juego base - corazón del sistema"""
    
    ANCHO_VENTANA = 640
    ALTO_VENTANA = 520
    
    def __init__(self, titulo: str = "Motor .brik", fps: int = 60):
        """
        Inicializa el motor gráfico
        
        Args:
            titulo: Título de la ventana
            fps: Frames por segundo objetivo
        """
        pygame.init()
        
        # Configuración de ventana
        self.pantalla = pygame.display.set_mode((self.ANCHO_VENTANA, self.ALTO_VENTANA))
        pygame.display.set_caption(titulo)
        
        # Reloj para controlar FPS
        self.reloj = pygame.time.Clock()
        self.fps = fps
        
        # Subsistemas
        self.graficos: Optional[Graficos] = None
        self.entrada = ControladorEntrada()
        self.interprete: Optional[InterpreteAST] = None
        
        # Control del loop
        self.ejecutando = False
        self.pausado = False
        
        # Callbacks del juego (deben ser asignados por el juego específico)
        self.callback_actualizar: Optional[Callable] = None
        self.callback_renderizar: Optional[Callable] = None
        self.callback_inicializar: Optional[Callable] = None
    
    def cargar_ast(self, ruta_ast: str, tam_celda: int = 10):
        """
        Carga un archivo AST y configura el motor
        
        Args:
            ruta_ast: Ruta al arbol.ast
            tam_celda: Tamaño de celda para gráficos
        """
        self.interprete = InterpreteAST(ruta_ast)
        self.graficos = Graficos(self.pantalla, tam_celda)
        
        # Configurar controles desde AST
        controles = self.interprete.obtener_controles()
        self.entrada.configurar_desde_ast(controles)
        
        # Registrar acciones básicas del motor
        self.entrada.registrar_accion("pausar", self.pausar)
        
        # Actualizar título con nombre del juego
        params = self.interprete.obtener_parametros_generales()
        pygame.display.set_caption(params["nombre_juego"])
    
    def pausar(self):
        """Pausa/despausa el juego"""
        self.pausado = not self.pausado
    
    def detener(self):
        """Detiene el motor"""
        self.ejecutando = False
    
    def iniciar(self):
        """
        Inicia el game loop principal
        
        El loop sigue el patrón:
        1. Gestión de eventos (entrada del usuario)
        2. Actualización lógica (física, IA, colisiones)
        3. Renderizado (dibujado en pantalla)
        """
        if self.graficos is None:
            raise RuntimeError("Debe cargar un AST antes de iniciar (usar cargar_ast())")
        
        # Inicialización del juego específico
        if self.callback_inicializar:
            self.callback_inicializar()
        
        self.ejecutando = True
        
        # ===== GAME LOOP PRINCIPAL =====
        while self.ejecutando:
            dt = self.reloj.tick(self.fps) / 1000.0  # Delta time en segundos
            
            # ----- 1. GESTIÓN DE EVENTOS -----
            eventos = pygame.event.get()
            for evento in eventos:
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                # Salir con ESC
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
            
            # Actualizar estado de entradas
            self.entrada.actualizar(eventos)
            self.entrada.ejecutar_acciones(tipo="recien_presionada")
            
            # ----- 2. ACTUALIZACIÓN LÓGICA -----
            if not self.pausado and self.callback_actualizar:
                self.callback_actualizar(dt)
            
            # ----- 3. RENDERIZADO -----
            self.graficos.limpiar_pantalla("negro")
            
            if self.callback_renderizar:
                self.callback_renderizar()
            
            # Indicador de pausa
            if self.pausado:
                self.graficos.dibujar_texto(
                    self.ANCHO_VENTANA // 2 - 60,
                    self.ALTO_VENTANA // 2,
                    "PAUSADO",
                    "amarillo"
                )
            
            pygame.display.flip()
        
        # Limpieza
        pygame.quit()
    
    def obtener_parametro(self, ruta: str, default=None):
        """Helper para obtener parámetros del AST"""
        if self.interprete:
            return self.interprete.obtener(ruta, default)
        return default