# 🧩 Proyecto PP_TLP — DSL `.brik` + Motor de Juego

## 📚 Integrantes
- **María José Laverde Mahecha**
- **José David Melo Contreras**
- **Ronald Sneyder Hernández Gómez**

---

## 🧱 Descripción General
Este proyecto corresponde a la **Entrega 2** del trabajo práctico de la asignatura *Teoría de Lenguajes de Programación*.  
Amplía la Entrega 1, donde se desarrolló el **analizador léxico y sintáctico** para el lenguaje **DSL `.brik`**, incorporando ahora un **motor de ejecución completo** para juegos definidos con dicho DSL, utilizando **Python 3 y Pygame**.

El sistema permite definir configuraciones de juegos (como *Snake* y *Tetris*) mediante archivos `.brik`, analizarlos para generar su **árbol sintáctico abstracto (`arbol.ast`)**, e interpretarlos dinámicamente con el motor gráfico y de control.

---

## 📁 Estructura del Proyecto
```
PP_TLP/
├─ analizador.py
├─ script_init.txt
├─ motor/
│  ├─ __init__.py
│  ├─ entrada.py
│  ├─ graficos.py
│  ├─ interprete.py
│  └─ nucleo.py
├─ snake/
│  ├─ snake.brik
│  ├─ arbol.ast
│  └─ ejecutar_snake.py
└─ tetris/
   ├─ tetris.brik
   ├─ arbol.ast
   └─ ejecutar_tetris.py
```
> La carpeta `.venv/` no se incluye en la entrega (solo para entorno local).

---

## ⚙️ Requisitos
- **Python 3.8 o superior**
- **Pygame**
  ```bash
  pip install pygame
  ```

---

## 🚀 Instrucciones de Uso

### 1️⃣ Generar los AST
```bash
cd PP_TLP
python analizador.py snake/snake.brik --pretty
python analizador.py tetris/tetris.brik --pretty
```

### 2️⃣ Ejecutar los Juegos

#### 🐍 Snake
```bash
python snake/ejecutar_snake.py
```

#### 🧱 Tetris
```bash
python tetris/ejecutar_tetris.py
```

---

## 🧠 Arquitectura del Sistema

### 🔸 1. `analizador.py` — Lexer + Parser
Genera un **AST en formato JSON** desde un archivo `.brik`.  
Características principales:
- Reconocimiento de tokens (`STRING`, `NUMBER`, `BOOL`, `IDENT`, `LIST`, `BLOCK`, `ARROW`)
- Soporte para **comentarios de línea y bloque**
- Manejo de **errores con línea y columna**
- Generación automática del archivo `arbol.ast` junto al `.brik`
- Argumento `--pretty` para impresión legible

---

### 🔸 2. `motor/` — Motor de Ejecución

#### 🧩 `nucleo.py`
Implementa el **game loop principal** (`Motor`):
- Ventana 640×520
- Ciclo: **eventos → actualización → renderizado**
- Control de FPS y pausa
- Callbacks personalizables por juego (`inicializar`, `actualizar`, `renderizar`)

#### 🧠 `interprete.py`
Traduce el contenido del `arbol.ast` al motor:
- Acceso simplificado a bloques del DSL (`parametros_generales`, `reglas`, `controles`, `piezas`, `manzanas`, etc.)
- Métodos específicos para cada juego (`obtener_config_snake()`, `obtener_piezas_tetris()`, `obtener_puntaje_config()`)

#### 🎮 `entrada.py`
Gestiona entradas del jugador mediante Pygame:
- Mapeo de teclas a acciones del DSL
- Detección de teclas presionadas y recién presionadas
- Sistema de callbacks (`registrar_accion`, `ejecutar_acciones`)

#### 🖼️ `graficos.py`
Contiene todas las funciones gráficas:
- `dibujar_ladrillo()`, `dibujar_texto()`, `dibujar_cuadricula()`
- Paleta de colores estándar (rojo, verde, dorado, gris, etc.)
- Renderizado con opacidad, figuras y texto con fuentes escaladas

#### 🧾 `__init__.py`
Integra los módulos del motor bajo un único espacio de nombres.

---

### 🔸 3. `snake/` — Implementación del Juego *Snake*
Archivo: `ejecutar_snake.py`

**Características:**
- Lógica completa del juego (movimiento, colisiones, efectos, vidas)
- Sistema de **manzanas múltiples**:
  - 🍎 Normal  
  - ⭐ Dorada (Score × 2 temporal)  
  - ☠️ Envenenada (pérdida de score, velocidad × 2)  
  - 💖 De vida (recupera vidas)
- Efectos temporales gestionados por clase `Efecto`
- Dibujo dinámico del tablero, UI y mensajes de Game Over
- Controles mapeados desde el DSL (`WASD`, `P`, `Q`, `ESC`)

---

### 🔸 4. `tetris/` — Implementación del Juego *Tetris*
Archivo: `ejecutar_tetris.py`

**Características:**
- Lógica del tablero, piezas, rotaciones, colisiones y líneas completas
- Sistema de puntaje configurable desde el AST:
  - Score por línea  
  - Bonus por Tetris (4 líneas)  
  - Incremento de nivel y velocidad
- Soporte de **pieza fantasma (ghost piece)** y **vista previa**
- Mapeo de controles (`A/D/S/J/K/Espacio/R`)
- Interfaz lateral con estadísticas y próxima pieza

---

## 🧩 Relación con la Entrega 1

| Componente | Entrega 1 | Entrega 2 |
|-------------|------------|-----------|
| Lexer + Parser (`analizador.py`) | ✔️ Completo | ✔️ Optimizado y documentado |
| AST (`arbol.ast`) | ✔️ Generado | ✔️ Utilizado por motor |
| Motor de juego (`motor/*`) | — | ✔️ Implementado |
| Interprete de AST | — | ✔️ Implementado |
| Ejemplos `.brik` (Snake, Tetris) | ✔️ | ✔️ Extendidos y funcionales |
| Renderizado y controles | — | ✔️ Integrados con Pygame |

---

## 🧾 Checklist Final
- [x] Lexer y parser funcionales (`analizador.py`)
- [x] AST JSON generado correctamente (`arbol.ast`)
- [x] Motor de juego (`motor/`) completo y modular
- [x] Juegos **Snake** y **Tetris** ejecutables
- [x] Manejo de entrada y gráficos con Pygame
- [x] Integración del DSL con motor mediante AST
- [x] Documentación actualizada (`README.md`)
