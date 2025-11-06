#!/usr/bin/env python3
"""
Ejecutable para Tetris usando el motor .brik
Demuestra la Entrega 2: Motor Gráfico y de Juego

Uso:
    cd PP_TLP
    python tetris/ejecutar_tetris.py
"""
import sys
from pathlib import Path
import random

# Agregar el directorio raíz al path para importar el motor
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor import Motor


class Pieza:
    """Representa una pieza de Tetris con su forma y rotación"""
    
    def __init__(self, tipo: str, color: str, matriz: list):
        self.tipo = tipo
        self.color = color
        self.matriz_base = matriz
        self.rotacion = 0
        self.x = 0
        self.y = 0
    
    def obtener_matriz(self) -> list:
        """Retorna la matriz en la rotación actual"""
        matriz = self.matriz_base
        for _ in range(self.rotacion):
            matriz = self._rotar_matriz_horario(matriz)
        return matriz
    
    def _rotar_matriz_horario(self, matriz: list) -> list:
        """Rota una matriz 90° en sentido horario"""
        filas = len(matriz)
        cols = len(matriz[0])
        nueva = [[0] * filas for _ in range(cols)]
        
        for i in range(filas):
            for j in range(cols):
                nueva[j][filas - 1 - i] = matriz[i][j]
        
        return nueva
    
    def rotar_horario(self):
        """Rota la pieza 90° en sentido horario"""
        self.rotacion = (self.rotacion + 1) % 4
    
    def rotar_antihorario(self):
        """Rota la pieza 90° en sentido antihorario"""
        self.rotacion = (self.rotacion - 1) % 4
    
    def obtener_bloques(self) -> list:
        """Retorna lista de coordenadas (x, y) de los bloques activos"""
        bloques = []
        matriz = self.obtener_matriz()
        
        for i, fila in enumerate(matriz):
            for j, celda in enumerate(fila):
                if celda == 1:
                    bloques.append((self.x + j, self.y + i))
        
        return bloques


class JuegoTetris:
    """Lógica específica del juego Tetris"""
    
    def __init__(self, motor: Motor):
        self.motor = motor
        self.ast = motor.interprete
        
        # Estado del juego
        self.score = 0
        self.lineas_completadas = 0
        self.nivel = 1
        self.pieza_actual = None
        self.pieza_siguiente = None
        self.tablero = []
        self.juego_terminado = False
        
        # Control de velocidad
        self.velocidad = 0
        self.tiempo_acumulado = 0
        self.tiempo_drop_rapido = 0.05  # Segundos cuando se presiona bajar
        
        # Dimensiones del tablero
        params = self.ast.obtener_parametros_generales()
        self.ancho_tablero, self.alto_tablero = params["dimensiones"]
        
        # Configuraciones
        self.config_puntaje = self.ast.obtener_puntaje_config()
        self.reglas = self.ast.obtener_reglas()
        self.piezas_disponibles = self.ast.obtener_piezas_tetris()
    
    def inicializar(self):
        """Inicializa el estado del juego desde el AST"""
        # Limpiar tablero
        self.tablero = [[None for _ in range(self.ancho_tablero)] 
                        for _ in range(self.alto_tablero)]
        
        # Configurar velocidad inicial
        self.velocidad = self.reglas.get("tick_base", 1.0)
        
        # Reset de estadísticas
        self.score = 0
        self.lineas_completadas = 0
        self.nivel = 1
        self.juego_terminado = False
        
        # Generar primera pieza
        self.pieza_siguiente = self.generar_pieza_aleatoria()
        self.nueva_pieza()
        
        # Registrar controles
        controles = self.ast.obtener_controles()
        
        # Movimiento
        self.motor.entrada.registrar_accion("izquierda", self.mover_izquierda)
        self.motor.entrada.registrar_accion("derecha", self.mover_derecha)
        self.motor.entrada.registrar_accion("bajar", self.bajar_rapido)
        
        # Rotación
        self.motor.entrada.registrar_accion("horario", self.rotar_horario)
        self.motor.entrada.registrar_accion("antihorario", self.rotar_antihorario)
        
        # Acciones
        self.motor.entrada.registrar_accion("soltar", self.hard_drop)
        self.motor.entrada.registrar_accion("reiniciar", self.reiniciar)
        
        print(f"Tetris iniciado - Nivel: {self.nivel}, Velocidad: {self.velocidad:.2f}s")
    
    def generar_pieza_aleatoria(self) -> Pieza:
        """Genera una pieza aleatoria de las disponibles"""
        tipo = random.choice(list(self.piezas_disponibles.keys()))
        config = self.piezas_disponibles[tipo]
        
        return Pieza(tipo, config["color"], config["matriz"])
    
    def nueva_pieza(self):
        """Coloca la siguiente pieza en el tablero"""
        self.pieza_actual = self.pieza_siguiente
        self.pieza_siguiente = self.generar_pieza_aleatoria()
        
        # Posición inicial (centro superior)
        self.pieza_actual.x = self.ancho_tablero // 2 - len(self.pieza_actual.obtener_matriz()[0]) // 2
        self.pieza_actual.y = 0
        
        # Verificar game over
        if not self.es_posicion_valida(self.pieza_actual):
            self.game_over()
    
    def es_posicion_valida(self, pieza: Pieza) -> bool:
        """Verifica si la pieza puede estar en su posición actual"""
        for x, y in pieza.obtener_bloques():
            # Fuera del tablero
            if x < 0 or x >= self.ancho_tablero or y >= self.alto_tablero:
                return False
            
            # Colisión con bloques existentes
            if y >= 0 and self.tablero[y][x] is not None:
                return False
        
        return True
    
    def mover_izquierda(self):
        """Mueve la pieza a la izquierda"""
        if self.juego_terminado:
            return
        
        self.pieza_actual.x -= 1
        if not self.es_posicion_valida(self.pieza_actual):
            self.pieza_actual.x += 1
    
    def mover_derecha(self):
        """Mueve la pieza a la derecha"""
        if self.juego_terminado:
            return
        
        self.pieza_actual.x += 1
        if not self.es_posicion_valida(self.pieza_actual):
            self.pieza_actual.x -= 1
    
    def bajar_rapido(self):
        """Acelera la caída de la pieza"""
        if self.juego_terminado:
            return
        
        # Mientras mantenga presionada la tecla, caerá más rápido
        # (implementado en actualizar())
        pass
    
    def rotar_horario(self):
        """Rota la pieza en sentido horario"""
        if self.juego_terminado:
            return
        
        self.pieza_actual.rotar_horario()
        if not self.es_posicion_valida(self.pieza_actual):
            # Intento de wall kick básico
            for offset in [1, -1, 2, -2]:
                self.pieza_actual.x += offset
                if self.es_posicion_valida(self.pieza_actual):
                    return
                self.pieza_actual.x -= offset
            
            # Si no hay espacio, deshacer rotación
            self.pieza_actual.rotar_antihorario()
    
    def rotar_antihorario(self):
        """Rota la pieza en sentido antihorario"""
        if self.juego_terminado:
            return
        
        self.pieza_actual.rotar_antihorario()
        if not self.es_posicion_valida(self.pieza_actual):
            # Intento de wall kick básico
            for offset in [1, -1, 2, -2]:
                self.pieza_actual.x += offset
                if self.es_posicion_valida(self.pieza_actual):
                    return
                self.pieza_actual.x -= offset
            
            # Si no hay espacio, deshacer rotación
            self.pieza_actual.rotar_horario()
    
    def hard_drop(self):
        """Suelta la pieza instantáneamente"""
        if self.juego_terminado or not self.reglas.get("hard_drop", True):
            return
        
        while True:
            self.pieza_actual.y += 1
            if not self.es_posicion_valida(self.pieza_actual):
                self.pieza_actual.y -= 1
                break
        
        self.fijar_pieza()
    
    def actualizar(self, dt: float):
        """Actualización lógica del juego"""
        if self.juego_terminado:
            return
        
        # Control de velocidad (caída automática)
        self.tiempo_acumulado += dt
        
        # Velocidad ajustada si se está bajando rápido
        velocidad_actual = self.velocidad
        if self.motor.entrada.esta_presionada("S"):
            velocidad_actual = self.tiempo_drop_rapido
        
        tiempo_por_tick = velocidad_actual
        
        if self.tiempo_acumulado >= tiempo_por_tick:
            self.tiempo_acumulado = 0
            self.bajar_pieza()
    
    def bajar_pieza(self):
        """Baja la pieza un nivel"""
        self.pieza_actual.y += 1
        
        if not self.es_posicion_valida(self.pieza_actual):
            self.pieza_actual.y -= 1
            self.fijar_pieza()
    
    def fijar_pieza(self):
        """Fija la pieza actual en el tablero"""
        for x, y in self.pieza_actual.obtener_bloques():
            if 0 <= y < self.alto_tablero:
                self.tablero[y][x] = self.pieza_actual.color
        
        # Verificar líneas completas
        lineas_eliminadas = self.verificar_lineas_completas()
        
        if lineas_eliminadas > 0:
            self.procesar_lineas_eliminadas(lineas_eliminadas)
        
        # Nueva pieza
        self.nueva_pieza()
    
    def verificar_lineas_completas(self) -> int:
        """Verifica y elimina líneas completas. Retorna cantidad eliminada"""
        lineas_completas = []
        
        for y in range(self.alto_tablero):
            if all(celda is not None for celda in self.tablero[y]):
                lineas_completas.append(y)
        
        # Eliminar líneas completas
        for y in reversed(lineas_completas):
            del self.tablero[y]
            self.tablero.insert(0, [None] * self.ancho_tablero)
        
        return len(lineas_completas)
    
    def procesar_lineas_eliminadas(self, cantidad: int):
        """Procesa el puntaje y nivel por líneas eliminadas"""
        # Puntaje base
        puntos = self.config_puntaje["score_por_linea"] * cantidad
        
        # Bonus por Tetris (4 líneas)
        if cantidad == 4:
            puntos += self.config_puntaje["tetris_bonus"]
            print("¡TETRIS! +800 puntos")
        
        self.score += puntos
        self.lineas_completadas += cantidad
        
        # Aumentar nivel y velocidad
        lineas_por_nivel = self.reglas.get("lineas_por_nivel", 10)
        nuevo_nivel = (self.lineas_completadas // lineas_por_nivel) + 1
        
        if nuevo_nivel > self.nivel:
            self.nivel = nuevo_nivel
            incremento = self.reglas.get("incremento_velocidad", 0.1)
            self.velocidad = max(0.1, self.velocidad - incremento)
            print(f"¡Nivel {self.nivel}! Velocidad: {self.velocidad:.2f}s")
        
        print(f"{cantidad} línea(s) - Score: {self.score}")
    
    def calcular_posicion_ghost(self) -> int:
        """Calcula la posición Y donde caería la pieza (ghost piece)"""
        if not self.reglas.get("ghost_piece", True):
            return None
        
        y_original = self.pieza_actual.y
        
        while True:
            self.pieza_actual.y += 1
            if not self.es_posicion_valida(self.pieza_actual):
                self.pieza_actual.y -= 1
                break
        
        y_ghost = self.pieza_actual.y
        self.pieza_actual.y = y_original
        
        return y_ghost if y_ghost != y_original else None
    
    def game_over(self):
        """Termina el juego"""
        self.juego_terminado = True
        print(f"GAME OVER - Score final: {self.score}, Líneas: {self.lineas_completadas}")
    
    def reiniciar(self):
        """Reinicia el juego"""
        self.inicializar()
        print("Juego reiniciado")
    
    def renderizar(self):
        """Dibuja el juego en pantalla"""
        # Dibujar cuadrícula de fondo
        self.motor.graficos.dibujar_cuadricula(
            self.ancho_tablero,
            self.alto_tablero,
            "gris"
        )
        
        # Dibujar bloques fijos en el tablero
        for y in range(self.alto_tablero):
            for x in range(self.ancho_tablero):
                if self.tablero[y][x] is not None:
                    self.motor.graficos.dibujar_ladrillo(x, y, self.tablero[y][x])
        
        # Dibujar ghost piece (pieza fantasma)
        if not self.juego_terminado:
            y_ghost = self.calcular_posicion_ghost()
            if y_ghost is not None:
                y_original = self.pieza_actual.y
                self.pieza_actual.y = y_ghost
                
                for x, y in self.pieza_actual.obtener_bloques():
                    if 0 <= y < self.alto_tablero:
                        # Dibujar con color más transparente/oscuro
                        self.motor.graficos.dibujar_rectangulo(
                            x * self.motor.graficos.tam_celda,
                            y * self.motor.graficos.tam_celda,
                            self.motor.graficos.tam_celda,
                            self.motor.graficos.tam_celda,
                            "gris",
                            relleno=False
                        )
                
                self.pieza_actual.y = y_original
        
        # Dibujar pieza actual
        if self.pieza_actual and not self.juego_terminado:
            for x, y in self.pieza_actual.obtener_bloques():
                if y >= 0:  # No dibujar bloques por encima del tablero
                    self.motor.graficos.dibujar_ladrillo(x, y, self.pieza_actual.color)
        
        # UI - Panel derecho
        ui_x = self.ancho_tablero * self.motor.graficos.tam_celda + 20
        
        # Estadísticas
        self.motor.graficos.dibujar_texto(ui_x, 20, f"Score: {self.score}", "blanco", pequeño=True)
        self.motor.graficos.dibujar_texto(ui_x, 50, f"Líneas: {self.lineas_completadas}", "blanco", pequeño=True)
        self.motor.graficos.dibujar_texto(ui_x, 80, f"Nivel: {self.nivel}", "blanco", pequeño=True)
        
        # Vista previa de siguiente pieza
        if self.reglas.get("vista_previa", 1) > 0 and self.pieza_siguiente:
            self.motor.graficos.dibujar_texto(ui_x, 120, "Siguiente:", "blanco", pequeño=True)
            
            matriz_preview = self.pieza_siguiente.obtener_matriz()
            offset_x = ui_x // self.motor.graficos.tam_celda
            offset_y = 150 // self.motor.graficos.tam_celda
            
            for i, fila in enumerate(matriz_preview):
                for j, celda in enumerate(fila):
                    if celda == 1:
                        self.motor.graficos.dibujar_ladrillo(
                            offset_x + j,
                            offset_y + i,
                            self.pieza_siguiente.color
                        )
        
        # Mensaje de game over
        if self.juego_terminado:
            self.motor.graficos.dibujar_texto(80, 200, "GAME OVER", "rojo")
            self.motor.graficos.dibujar_texto(60, 240, "Presiona R para reiniciar", "blanco", pequeño=True)


def main():
    """Punto de entrada del juego Tetris"""
    # Crear motor
    motor = Motor(titulo="Tetris .brik", fps=60)
    
    # Cargar configuración desde AST
    ruta_ast = Path(__file__).parent / "arbol.ast"
    
    # Obtener tamaño de celda del AST
    import json
    with open(ruta_ast, 'r', encoding='utf-8') as f:
        ast_data = json.load(f)
    tam_celda = ast_data.get("parametros_generales", {}).get("celda", 16)
    
    motor.cargar_ast(str(ruta_ast), tam_celda=tam_celda)
    
    # Crear juego
    juego = JuegoTetris(motor)
    
    # Conectar callbacks
    motor.callback_inicializar = juego.inicializar
    motor.callback_actualizar = juego.actualizar
    motor.callback_renderizar = juego.renderizar
    
    # Iniciar motor
    print("=" * 50)
    print("TETRIS - Motor .brik")
    print("=" * 50)
    print("Controles:")
    print("  A/D - Izquierda/Derecha")
    print("  S - Bajar rápido")
    print("  J/K - Rotar antihorario/horario")
    print("  Espacio - Hard drop")
    print("  P - Pausar")
    print("  R - Reiniciar")
    print("=" * 50)
    
    motor.iniciar()


if __name__ == "__main__":
    main()