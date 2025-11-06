"""
Intérprete del AST - Lee arbol.ast y extrae configuraciones
Conecta el DSL .brik con el motor de juego
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

class InterpreteAST:
    """Lee y parsea el archivo arbol.ast generado por analizador.py"""
    
    def __init__(self, ruta_ast: str):
        """
        Args:
            ruta_ast: Ruta al archivo arbol.ast
        """
        self.ruta = Path(ruta_ast)
        self.ast: Dict[str, Any] = {}
        self.cargar()
    
    def cargar(self):
        """Carga el AST desde el archivo JSON"""
        if not self.ruta.exists():
            raise FileNotFoundError(f"No se encontró el archivo AST: {self.ruta}")
        
        with open(self.ruta, 'r', encoding='utf-8') as f:
            self.ast = json.load(f)
    
    def obtener(self, ruta_clave: str, default=None) -> Any:
        """
        Obtiene un valor del AST usando notación de punto
        
        Ejemplo:
            obtener("parametros_generales.cuadricula") -> [50, 50]
            obtener("reglas.vidas_iniciales") -> 3
        """
        partes = ruta_clave.split('.')
        valor = self.ast
        
        for parte in partes:
            if isinstance(valor, dict) and parte in valor:
                valor = valor[parte]
            else:
                return default
        
        return valor
    
    def obtener_bloque(self, nombre_bloque: str) -> Optional[Dict]:
        """Obtiene un bloque completo del AST"""
        return self.ast.get(nombre_bloque)
    
    def obtener_parametros_generales(self) -> Dict:
        """Extrae parámetros generales del juego"""
        params = self.obtener_bloque("parametros_generales") or {}
        return {
            "nombre_juego": params.get("mi_juego", "Juego sin nombre"),
            "version": params.get("version", "1.0.0"),
            "dimensiones": params.get("cuadricula") or params.get("tablero", [20, 20]),
            "tam_celda": params.get("celda", 10)
        }
    
    def obtener_reglas(self) -> Dict:
        """Extrae reglas del juego"""
        reglas = self.obtener_bloque("reglas") or {}
        return {
            "vidas_iniciales": reglas.get("vidas_iniciales", 1),
            "score_inicial": reglas.get("score_inicial", 0),
            "tick_base": reglas.get("tick_base", 1.0),
            "incremento_velocidad": reglas.get("incremento_velocidad", 0.1),
            "hard_drop": reglas.get("hard_drop", False),
            "ghost_piece": reglas.get("ghost_piece", False)
        }
    
    def obtener_controles(self) -> Dict:
        """Extrae el bloque de controles completo"""
        return self.obtener_bloque("controles") or {}
    
    def obtener_eventos(self) -> list:
        """
        Extrae mapeos de eventos
        
        Retorna lista de dicts: [{"from": "colision", "to": "perder_vida"}, ...]
        """
        eventos = self.obtener_bloque("eventos")
        if eventos and "_mappings" in eventos:
            return eventos["_mappings"]
        return []
    
    def obtener_config_snake(self) -> Optional[Dict]:
        """Configuración específica de Snake"""
        snake = self.obtener_bloque("snake")
        if not snake:
            return None
        
        return {
            "dimensiones": snake.get("dimensiones", [1, 3]),
            "velocidad_inicial": snake.get("velocidad_inicial", 2),
            "aumento_velocidad": snake.get("aumento_velocidad", 1),
            "color": snake.get("color", "verde")
        }
    
    def obtener_manzanas(self) -> Dict:
        """Extrae todas las configuraciones de manzanas (Snake)"""
        return self.obtener_bloque("manzanas") or {}
    
    def obtener_piezas_tetris(self) -> Dict:
        """Extrae las definiciones de piezas (Tetris)"""
        piezas = self.obtener_bloque("piezas") or {}
        # Filtra la clave especial "_mappings" si existe
        return {k: v for k, v in piezas.items() if k != "_mappings"}
    
    def obtener_puntaje_config(self) -> Dict:
        """Extrae configuración de puntaje (Tetris)"""
        puntaje = self.obtener_bloque("puntaje") or {}
        return {
            "score_por_linea": puntaje.get("score_por_linea", 100),
            "combo_bonus": puntaje.get("combo_bonus", 50),
            "tetris_bonus": puntaje.get("tetris_bonus", 800)
        }
    
    def obtener_condicion_fin(self) -> str:
        """Obtiene la condición de fin de juego"""
        fin = self.obtener_bloque("fin_de_juego") or {}
        return fin.get("condicion", "")
    
    def __repr__(self) -> str:
        return f"InterpreteAST({self.ruta})"