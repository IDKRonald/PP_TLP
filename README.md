# Proyecto — DSL `.brik` + Analizador (Lexer/Parser)

## Integrantes:
- Maria José Laverde Mahecha
- José David Melo Contreras
- Ronald Sneyder Hernández Gómez

## Entregables (según el classroom)
- `snake/snake.brik`  
- `tetris/tetris.brik`  
- **Un solo archivo** de analizador: `analizador.py` (Python)  
- El analizador debe **tokenizar** y **generar el árbol sintáctico** y guardarlo como **`arbol.ast`** (JSON)

---

## Estructura recomendada
```
PP_TLP/
├─ analizador.py
├─ snake/
│  └─ snake.brik
└─ tetris/
   └─ tetris.brik
```
> Así cada `arbol.ast` se genera **junto** a su `.brik` y no se sobreescriben entre sí.

---

## Requisitos
- Python 3.8+  
- `analizador.py` en la raíz del proyecto (como en el árbol anterior)

---

## Cómo generar el AST (`arbol.ast`) [MUY IMPORTANTE]
#### Las instrucciones de ejecución para generar el AST son importantes en este caso, ya que quedaron algo diferentes respecto al archivo de ejemplo del profe


### Snake
**Windows (PowerShell)**
```powershell
cd PP_TLP
py .\analizador.py .\snake\snake.brik --pretty
```

**macOS / Linux**
```bash
cd PP_TLP
python3 analizador.py ./snake/snake.brik --pretty
```

➡️ Se crea **`snake/arbol.ast`** (JSON).  
`--pretty` es opcional (solo afecta la impresión en pantalla, el archivo siempre se escribe indentado).

### Tetris
**Windows (PowerShell)**
```powershell
cd PP_TLP
py .\analizador.py .\tetris\tetris.brik --pretty
```

**macOS / Linux**
```bash
cd PP_TLP
python3 analizador.py ./tetris/tetris.brik --pretty
```

➡️ Se crea **`tetris/arbol.ast`**.

> Si ejecutas varias veces sobre el mismo `.brik`, **se sobrescribe** su `arbol.ast` (comportamiento esperado).

---

## Especificación breve del DSL `.brik`

### Comentarios
- Línea: `// comentario`
- Bloque: `/* comentario ... */`

### Parámetros
- **Simples:** `nombre = valor`
- **Compuestos (bloque):**
  ```brik
  nombre {
      atributo1 = valor1,
      atributo2 = valor2
      // subbloques y mapeos permitidos
  }
  ```
- **Listas:** `lista = [x1, x2, x3]` (admite listas anidadas)

### Tipos soportados
- `STRING`: `"texto"` (con escapes `\" \\ \n`)
- `NUMBER`: `123`, `3.14`, **`-30`** (negativos admitidos)
- `BOOL`: `true`, `false`
- `LIST`: `[ ... ]`
- `BLOCK`: `{ ... }`

### Mapeos de eventos
- Sintaxis: `evento -> accion`
- Se guardan en el AST bajo la clave `"_mappings"` del bloque:
  ```json
  "_mappings": [
    { "from": "colision", "to": "perder_vida" }
  ]
  ```

### Separadores dentro de bloques
- **Coma opcional** entre entradas.
- También se admite **separador implícito** por nueva línea (otra entrada `IDENT` sin coma).

---

## Qué hace el analizador (`analizador.py`)

### Lexer (Tokenizador)
- Reconoce: `{ } [ ] , = ->`
- Ignora comentarios `//` y `/* ... */`
- Tokeniza: strings, números (incluye negativos), booleanos, identificadores

### Parser (Árbol sintáctico)
- Top-level: `ident = valor` **o** `ident { ... }`
- Dentro de bloques:
  - Asignación: `ident = valor`
  - **Sub-bloques:** `ident { ... }`
  - **Mapeos:** `ident -> ident | "string"`
- Salida: **JSON**  
  - El AST se guarda **siempre** como `arbol.ast` en la **misma carpeta** del `.brik` analizado.

### Errores (ejemplos)
- Mensajes con **línea y columna** para depurar rápido:
  - Comillas sin cerrar
  - Llaves o corchetes desbalanceados
  - Token inesperado dentro de un bloque

---

## Notas por juego

### `snake.brik`
- Secciones típicas: `parametros_generales`, `reglas`, `snake`, `manzanas`, `eventos`, `fin_de_juego`, `controles`
- Ítems de `manzanas` como **sub-bloques** dentro de `manzanas { ... }`
- `eventos` usa mapeos: `colision -> perder_vida`

### `tetris.brik`
- `piezas` definidas con **matrices 0/1** (solo forma base; las **rotaciones** las hace el motor)
- Secciones análogas: `parametros_generales`, `reglas`, `puntaje`, `piezas`, `eventos`, `fin_de_juego`, `controles`

---

## Checklist (para entrega)
- [ ] `snake/snake.brik` (válido con el DSL)
- [ ] `tetris/tetris.brik` (válido con el DSL)
- [ ] `analizador.py` (un solo archivo — lexer + parser)
- [ ] `snake/arbol.ast` generado (La idea es que ambos árboles sintácticos sean generados por el profe/monitor a cargo de la revisión del trabajo, ya que justamente es el sentido de la entrega, que funcione)
- [ ] `tetris/arbol.ast` generado

---

## Tips
- Usa identificadores en minúsculas con guion_bajo.
- Evita coma **final** cuando no la necesites (el analizador la tolera, pero mejor limpio).
- Si ves un error, revisa **justo** la línea y columna que señala el analizador.
