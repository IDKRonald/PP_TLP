#!/usr/bin/env python3
"""
Ejecutable para Snake usando el motor .brik
Demuestra la Entrega 2: Motor Gráfico y de Juego

Uso:
    cd PP_TLP
    python snake/ejecutar_snake.py
"""
import sys
from pathlib import Path
import random
import time

# Agregar el directorio raíz al path para importar el motor
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor import Motor

class Manzana:
    """Representa una manzana con tipo"""
    def __init__(self, pos, tipo, config):
        self.pos = pos
        self.tipo = tipo
        self.config = config

class Efecto:
    """Representa un efecto temporal activo"""
    def __init__(self, nombre, duracion):
        self.nombre = nombre
        self.tiempo_inicio = time.time()
        self.duracion = duracion
    
    def esta_activo(self):
        return time.time() - self.tiempo_inicio < self.duracion
    
    def tiempo_restante(self):
        return max(0, self.duracion - (time.time() - self.tiempo_inicio))

class JuegoSnake:
    """Lógica específica del juego Snake"""
    
    def __init__(self, motor: Motor):
        self.motor = motor
        self.ast = motor.interprete
        
        # Estado del juego
        self.vidas = 0
        self.vidas_maximas = 0
        self.score = 0
        self.snake_pos = []
        self.snake_dir = (1, 0)  # (dx, dy)
        self.manzana_actual = None
        self.velocidad_base = 0
        self.velocidad = 0
        self.tiempo_acumulado = 0
        self.juego_terminado = False
        
        # Efectos activos
        self.efectos = []
        
        # Dimensiones del tablero
        params = self.ast.obtener_parametros_generales()
        self.ancho_grid, self.alto_grid = params["dimensiones"]
        
        # Configuraciones de manzanas
        self.configs_manzanas = self.ast.obtener_manzanas()
        
        # Pesos para selección aleatoria de manzanas
        self.tipos_manzanas = []
        self.calcular_probabilidades()
    
    def calcular_probabilidades(self):
        """Calcula la tabla de probabilidades para manzanas"""
        self.tipos_manzanas = []
        total_prob_especiales = 0
        
        # Calcular probabilidad total de manzanas especiales
        if "manzana_dorada" in self.configs_manzanas:
            total_prob_especiales += self.configs_manzanas["manzana_dorada"].get("probabilidad", 0.1)
        
        if "manzana_envenenada" in self.configs_manzanas:
            total_prob_especiales += self.configs_manzanas["manzana_envenenada"].get("probabilidad", 0.2)

        if "manzana_de_vida" in self.configs_manzanas:
            total_prob_especiales += self.configs_manzanas["manzana_de_vida"].get("probabilidad", 0.005)
        
        # Manzana normal toma el resto de probabilidad
        if "manzana" in self.configs_manzanas:
            self.tipos_manzanas.append(("manzana", 1.0 - total_prob_especiales))
        
        # Manzanas especiales
        if "manzana_dorada" in self.configs_manzanas:
            prob = self.configs_manzanas["manzana_dorada"].get("probabilidad", 0.1)
            self.tipos_manzanas.append(("manzana_dorada", prob))
        
        if "manzana_envenenada" in self.configs_manzanas:
            prob = self.configs_manzanas["manzana_envenenada"].get("probabilidad", 0.2)
            self.tipos_manzanas.append(("manzana_envenenada", prob))
        
        if "manzana_de_vida" in self.configs_manzanas:
            prob = self.configs_manzanas["manzana_de_vida"].get("probabilidad", 0.005)
            self.tipos_manzanas.append(("manzana_de_vida", prob))
    
    def inicializar(self):
        """Inicializa el estado del juego desde el AST"""
        # Reglas iniciales (solo la primera vez)
        if self.vidas == 0:
            reglas = self.ast.obtener_reglas()
            self.vidas = reglas["vidas_iniciales"]
            self.vidas_maximas = reglas["vidas_iniciales"]
            self.score = reglas["score_inicial"]
        
        # Configuración de snake
        config_snake = self.ast.obtener_config_snake()
        self.velocidad_base = config_snake["velocidad_inicial"]
        self.velocidad = self.velocidad_base
        
        # Posición inicial de la snake (centro del tablero)
        largo_inicial = config_snake["dimensiones"][1]
        centro_x = self.ancho_grid // 2
        centro_y = self.alto_grid // 2
        self.snake_pos = [(centro_x - i, centro_y) for i in range(largo_inicial)]
        self.snake_dir = (1, 0)  # Siempre inicia hacia la derecha
        
        # Limpiar efectos
        self.efectos = []
        
        # Generar primera manzana
        self.generar_manzana()
        
        # Registrar controles (solo la primera vez)
        if not hasattr(self, '_controles_registrados'):
            self.motor.entrada.registrar_accion("derecha", lambda: self.cambiar_direccion(1, 0))
            self.motor.entrada.registrar_accion("izquierda", lambda: self.cambiar_direccion(-1, 0))
            self.motor.entrada.registrar_accion("arriba", lambda: self.cambiar_direccion(0, -1))
            self.motor.entrada.registrar_accion("bajar", lambda: self.cambiar_direccion(0, 1))
            self.motor.entrada.registrar_accion("reiniciar", self.reiniciar)
            self._controles_registrados = True
        
        print(f"🐍 Snake reiniciado - Vidas: {self.vidas}/{self.vidas_maximas}, Velocidad: {self.velocidad}")
    
    def cambiar_direccion(self, dx: int, dy: int):
        """Cambia la dirección del snake (evita reversa)"""
        # No permitir reversa (moverse 180° al instante)
        if (dx, dy) != (-self.snake_dir[0], -self.snake_dir[1]):
            self.snake_dir = (dx, dy)
    
    def seleccionar_tipo_manzana(self):
        """Selecciona un tipo de manzana según probabilidades"""
        rand = random.random()
        acumulado = 0
        
        for tipo, prob in self.tipos_manzanas:
            acumulado += prob
            if rand <= acumulado:
                return tipo
        
        # Fallback a manzana normal
        return "manzana"
    
    def generar_manzana(self):
        """Genera una manzana en posición aleatoria con tipo aleatorio"""
        # Seleccionar tipo de manzana
        tipo = self.seleccionar_tipo_manzana()
        config = self.configs_manzanas.get(tipo, self.configs_manzanas.get("manzana", {}))
        
        # Buscar posición libre
        intentos = 0
        while intentos < 100:
            x = random.randint(0, self.ancho_grid - 1)
            y = random.randint(0, self.alto_grid - 1)
            if (x, y) not in self.snake_pos:
                self.manzana_actual = Manzana((x, y), tipo, config)
                emoji = {"manzana": "🍎", "manzana_dorada": "⭐", "manzana_envenenada": "☠️", "manzana_de_vida": "💖"}
                print(f"{emoji.get(tipo, '🍎')} Nueva manzana: {tipo} en ({x}, {y})")
                break
            intentos += 1
    
    def actualizar(self, dt: float):
        """Actualización lógica del juego"""
        if self.juego_terminado:
            return
        
        # Actualizar efectos activos
        self.efectos = [e for e in self.efectos if e.esta_activo()]
        
        # Calcular velocidad con efectos
        velocidad_efectiva = self.velocidad
        for efecto in self.efectos:
            if efecto.nombre == "velocidad_x2":
                velocidad_efectiva *= 2
        
        # Control de velocidad (movimiento basado en tiempo)
        self.tiempo_acumulado += dt
        tiempo_por_movimiento = 1.0 / velocidad_efectiva
        
        if self.tiempo_acumulado >= tiempo_por_movimiento:
            self.tiempo_acumulado = 0
            self.mover_snake()
    
    def mover_snake(self):
        """Mueve la snake un paso"""
        # Nueva posición de la cabeza
        cabeza = self.snake_pos[0]
        nueva_cabeza = (cabeza[0] + self.snake_dir[0], cabeza[1] + self.snake_dir[1])
        
        # Verificar colisiones
        if self.verificar_colision(nueva_cabeza):
            self.perder_vida()
            return
        
        # Mover snake
        self.snake_pos.insert(0, nueva_cabeza)
        
        # Verificar si comió manzana
        if self.manzana_actual and nueva_cabeza == self.manzana_actual.pos:
            self.comer_manzana()
        else:
            # Eliminar cola si no comió
            self.snake_pos.pop()
    
    def verificar_colision(self, pos) -> bool:
        """Verifica si hay colisión en una posición"""
        x, y = pos
        
        # Fuera del tablero
        if x < 0 or x >= self.ancho_grid or y < 0 or y >= self.alto_grid:
            return True
        
        # Colisión con el cuerpo (excluye la cola que desaparecerá)
        if pos in self.snake_pos[:-1]:
            return True
        
        return False
    
    def comer_manzana(self):
        """Procesa el evento de comer una manzana"""
        if not self.manzana_actual:
            return
        
        tipo = self.manzana_actual.tipo
        config = self.manzana_actual.config
        
        # Procesar según tipo de manzana
        if tipo == "manzana":
            # Manzana normal
            score = config.get("score", 15)
            self.score += score
            self.aumentar_velocidad()
            print(f"🍎 Manzana comida! +{score} puntos")
        
        elif tipo == "manzana_dorada":
            # Manzana dorada: score doble
            score = config.get("score", 30)
            self.score += score
            duracion = config.get("duracion", 5)
            self.efectos.append(Efecto("score_x2", duracion))
            self.aumentar_velocidad()
            print(f"⭐ Manzana dorada! +{score} puntos, Score x2 por {duracion}s")
        
        elif tipo == "manzana_envenenada":
            # Manzana envenenada: score negativo, velocidad x2
            score = config.get("score", -30)
            self.score = max(0, self.score + score)  # No bajar de 0
            duracion = config.get("duracion", 5)
            self.efectos.append(Efecto("velocidad_x2", duracion))
            print(f"☠️ Manzana envenenada! {score} puntos, Velocidad x2 por {duracion}s")
        
        elif tipo == "manzana_de_vida":
            # Manzana de vida: aumenta vidas
            valor = config.get("valor", 1)
            self.vidas = min(self.vidas_maximas, self.vidas + valor)
            print(f"💖 Manzana de vida! +{valor} vida")
        
        # Aplicar multiplicador de score si está activo
        for efecto in self.efectos:
            if efecto.nombre == "score_x2" and tipo == "manzana":
                self.score += config.get("score", 15)  # Doble puntos
                print(f"   ✨ Score x2 activo! +{config.get('score', 15)} extra")
        
        # Generar nueva manzana
        self.generar_manzana()
        
        print(f"   📊 Score actual: {self.score}")
    
    def aumentar_velocidad(self):
        """Aumenta la velocidad base del snake"""
        config_snake = self.ast.obtener_config_snake()
        self.velocidad += config_snake["aumento_velocidad"]
    
    def perder_vida(self):
        """Maneja la pérdida de una vida"""
        self.vidas -= 1
        print(f"💔 Vida perdida! Vidas restantes: {self.vidas}/{self.vidas_maximas}")
        
        if self.vidas <= 0:
            self.game_over()
        else:
            # Reiniciar posición de la snake sin resetear score
            score_temporal = self.score
            self.inicializar()
            self.score = score_temporal  # Mantener el score
    
    def game_over(self):
        """Termina el juego"""
        self.juego_terminado = True
        print(f"💀 GAME OVER - Score final: {self.score}")
    
    def reiniciar(self):
        """Reinicia el juego completamente"""
        self.juego_terminado = False
        self.vidas = 0  # Forzar reinicio completo
        self.score = 0
        self.inicializar()
        print("🔄 Juego reiniciado completamente")
    
    def renderizar(self):
        """Dibuja el juego en pantalla"""
        # Dibujar cuadrícula con baja opacidad
        self.motor.graficos.dibujar_cuadricula(self.ancho_grid, self.alto_grid, "gris", opacidad=0.15)
        
        # Dibujar snake
        config_snake = self.ast.obtener_config_snake()
        color_snake = config_snake["color"]
        
        for i, (x, y) in enumerate(self.snake_pos):
            # Cabeza más clara
            color = "amarillo" if i == 0 else color_snake
            self.motor.graficos.dibujar_ladrillo(x, y, color)
        
        # Dibujar manzana
        if self.manzana_actual:
            config = self.manzana_actual.config
            color_manzana = config.get("color", "rojo")
            forma_manzana = config.get("forma", "cuadro")
            
            self.motor.graficos.dibujar_ladrillo(
                self.manzana_actual.pos[0],
                self.manzana_actual.pos[1],
                color_manzana,
                forma_manzana
            )
        
        # UI - Score y vidas (fuera del área de juego)
        ui_x = self.ancho_grid * self.motor.graficos.tam_celda + 20
        self.motor.graficos.dibujar_texto(ui_x, 20, f"Score: {self.score}", "blanco", pequeño=True)
        self.motor.graficos.dibujar_texto(ui_x, 50, f"Vidas: {self.vidas}/{self.vidas_maximas}", "blanco", pequeño=True)
        self.motor.graficos.dibujar_texto(ui_x, 80, f"Vel: {self.velocidad:.1f}", "blanco", pequeño=True)
        
        # Mostrar efectos activos
        y_offset = 110
        for efecto in self.efectos:
            tiempo = efecto.tiempo_restante()
            if efecto.nombre == "score_x2":
                self.motor.graficos.dibujar_texto(ui_x, y_offset, f"⭐ x2: {tiempo:.1f}s", "amarillo", pequeño=True)
            elif efecto.nombre == "velocidad_x2":
                self.motor.graficos.dibujar_texto(ui_x, y_offset, f"☠️ Fast: {tiempo:.1f}s", "rojo", pequeño=True)
            y_offset += 25
        
        # Mensaje de game over
        if self.juego_terminado:
            self.motor.graficos.dibujar_texto(150, 200, "GAME OVER", "rojo")
            self.motor.graficos.dibujar_texto(120, 240, "Presiona Q para reiniciar", "blanco", pequeño=True)


def main():
    """Punto de entrada del juego Snake"""
    # Crear motor
    motor = Motor(titulo="Snake .brik", fps=60)
    
    # Cargar configuración desde AST
    ruta_ast = Path(__file__).parent / "arbol.ast"
    motor.cargar_ast(str(ruta_ast), tam_celda=10)
    
    # Crear juego
    juego = JuegoSnake(motor)
    
    # Conectar callbacks
    motor.callback_inicializar = juego.inicializar
    motor.callback_actualizar = juego.actualizar
    motor.callback_renderizar = juego.renderizar
    
    # Iniciar motor
    print("=" * 50)
    print("🎮 SNAKE - Motor .brik")
    print("=" * 50)
    print("Controles:")
    print("  W - Arriba")
    print("  A - Izquierda")
    print("  D - Derecha")
    print("  S - Abajo")
    print("  P - Pausar")
    print("  Q - Reiniciar")
    print("  ESC - Salir")
    print("=" * 50)
    print("\n🍎 Manzanas:")
    print("  🍎 Normal: +15 puntos")
    print("  ⭐ Dorada: +30 puntos, Score x2 por 5s")
    print("  ☠️ Envenenada: -30 puntos, Velocidad x2 por 5s")
    print("  💖 Vida: +1 vida extra")
    print("=" * 50)
    
    motor.iniciar()


if __name__ == "__main__":
    main()