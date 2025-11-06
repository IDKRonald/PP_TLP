"""
Sistema de control de entradas del motor
Gestiona teclado y mapea teclas desde el AST
"""
import pygame
from typing import Dict, Set, Callable

class ControladorEntrada:
    """Maneja las entradas del usuario y mapea acciones del DSL"""
    
    # Mapeo de nombres de teclas del DSL a códigos pygame
    MAPA_TECLAS = {
        "A": pygame.K_a, "a": pygame.K_a,
        "B": pygame.K_b, "b": pygame.K_b,
        "C": pygame.K_c, "c": pygame.K_c,
        "D": pygame.K_d, "d": pygame.K_d,
        "E": pygame.K_e, "e": pygame.K_e,
        "F": pygame.K_f, "f": pygame.K_f,
        "G": pygame.K_g, "g": pygame.K_g,
        "H": pygame.K_h, "h": pygame.K_h,
        "I": pygame.K_i, "i": pygame.K_i,
        "J": pygame.K_j, "j": pygame.K_j,
        "K": pygame.K_k, "k": pygame.K_k,
        "L": pygame.K_l, "l": pygame.K_l,
        "M": pygame.K_m, "m": pygame.K_m,
        "N": pygame.K_n, "n": pygame.K_n,
        "O": pygame.K_o, "o": pygame.K_o,
        "P": pygame.K_p, "p": pygame.K_p,
        "Q": pygame.K_q, "q": pygame.K_q,
        "R": pygame.K_r, "r": pygame.K_r,
        "S": pygame.K_s, "s": pygame.K_s,
        "T": pygame.K_t, "t": pygame.K_t,
        "U": pygame.K_u, "u": pygame.K_u,
        "V": pygame.K_v, "v": pygame.K_v,
        "W": pygame.K_w, "w": pygame.K_w,
        "X": pygame.K_x, "x": pygame.K_x,
        "Y": pygame.K_y, "y": pygame.K_y,
        "Z": pygame.K_z, "z": pygame.K_z,
        "Espacio": pygame.K_SPACE,
        "Arriba": pygame.K_UP,
        "Abajo": pygame.K_DOWN,
        "Izquierda": pygame.K_LEFT,
        "Derecha": pygame.K_RIGHT,
        "Enter": pygame.K_RETURN,
        "Escape": pygame.K_ESCAPE,
        "ESC": pygame.K_ESCAPE
    }
    
    def __init__(self):
        self.teclas_presionadas: Set[int] = set()
        self.teclas_recien_presionadas: Set[int] = set()
        self.acciones: Dict[str, Callable] = {}
        self.mapa_accion_tecla: Dict[int, str] = {}
    
    def configurar_desde_ast(self, controles_ast: Dict):
        """
        Configura los controles desde el bloque 'controles' del AST
        
        Ejemplo de controles_ast:
        {
            "movimiento": {"derecha": "D", "izquierda": "A"},
            "interfaz": {"pausar": "S"}
        }
        """
        for categoria, mapeo in controles_ast.items():
            if isinstance(mapeo, dict):
                for accion, tecla_str in mapeo.items():
                    if tecla_str in self.MAPA_TECLAS:
                        codigo_tecla = self.MAPA_TECLAS[tecla_str]
                        self.mapa_accion_tecla[codigo_tecla] = accion
    
    def registrar_accion(self, nombre_accion: str, callback: Callable):
        """Registra una función callback para una acción"""
        self.acciones[nombre_accion] = callback
    
    def actualizar(self, eventos: list):
        """
        Procesa eventos de pygame y actualiza estado de teclas
        Debe llamarse una vez por frame antes de ejecutar_acciones()
        """
        self.teclas_recien_presionadas.clear()
        
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                self.teclas_presionadas.add(evento.key)
                self.teclas_recien_presionadas.add(evento.key)
            elif evento.type == pygame.KEYUP:
                self.teclas_presionadas.discard(evento.key)
    
    def ejecutar_acciones(self, tipo: str = "presionada"):
        """
        Ejecuta callbacks de acciones según teclas activas
        
        Args:
            tipo: "presionada" (mantener) o "recien_presionada" (una vez)
        """
        teclas = self.teclas_presionadas if tipo == "presionada" else self.teclas_recien_presionadas
        
        for codigo_tecla in teclas:
            if codigo_tecla in self.mapa_accion_tecla:
                accion = self.mapa_accion_tecla[codigo_tecla]
                if accion in self.acciones:
                    self.acciones[accion]()
    
    def esta_presionada(self, nombre_tecla: str) -> bool:
        """Verifica si una tecla está presionada actualmente"""
        if nombre_tecla in self.MAPA_TECLAS:
            return self.MAPA_TECLAS[nombre_tecla] in self.teclas_presionadas
        return False
    
    def fue_presionada(self, nombre_tecla: str) -> bool:
        """Verifica si una tecla fue presionada este frame"""
        if nombre_tecla in self.MAPA_TECLAS:
            return self.MAPA_TECLAS[nombre_tecla] in self.teclas_recien_presionadas
        return False