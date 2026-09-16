# Reparación CRAP y recalificación — AC1 / PR #53 (2026-09-16)

## Estado del registro

Este expediente cierra el encargo acotado de reparar los tres incumplimientos
CRAP identificados en la calificación previa. El código medido está en el
commit `aed2acf0ca39f39268601fe439efbe6d1226678a`, basado en
`a529adb0bf66d3bfa67ebf2f7dbee9a2facadab5`, con `origin/main` en
`932c835ac0eeb75010ec7a1071315b1c51f78eb6`. El commit contiene únicamente
los tres archivos de producto/test de la reparación; este informe y la
actualización de la matriz se publican en un commit documental posterior.

El fichero ajeno
`PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` sigue sin seguimiento,
fuera del stage y sin cambios. SHA-256 conservado:
`dedda9f3f057e9a02bd40740404c2c25773ed21b502798360ec5146a0fd1d430`.
No se modificaron gobernanza, umbrales, baselines, manifests, lock, versión,
features ni el contrato AC1. No se ejecutan aquí `full`, bless/update-manifest,
merge, bump, tag ni release.

## 1. Alcance y cambios

Se mantuvo el alcance solicitado: `semgrep_scope._python_files`,
`semgrep_scope._build_dirs` y `accept.process._execute`, con pruebas en
`tests/unit/test_accept_campaign.py` (el archivo `test_sast_targets.py` ya
contenía sus pruebas en la base y no necesitó una modificación adicional).

- `semgrep_scope.py`: se extrajeron `_is_under_build` y `_python_file` para
  separar el filtro de candidatos de la iteración; `_build_values` y
  `_resolve_build` separan validación y resolución de `paths.build`. Se
  conservaron mensajes, excepciones, orden y resultados; el verifier comparó
  casos de string/lista, rutas vacías, `build`, padres, cachés y rutas fuera
  de raíz contra la implementación base.
- `process.py`: se extrajo `_close_streams`, conservando la limpieza en
  `finally` después de observar/recolectar el hijo. Se añadió una prueba con
  streams ausentes que también comprueba `stdin=DEVNULL`, `stdout/stderr=PIPE`
  y el `wait(timeout=1)` observable.
- No se añadieron supresiones, dependencias ni configuraciones de gobierno.

SHA-256 de los archivos del commit de código:

```text
a7a41d3597e95067893df86ec8de138ef09a9d4ce00e1a939ce3ff0cda6c283c  tools/wct/gate/semgrep_scope.py
0a218827bb55219569fde1c4c9149894d6bc45173680e4f562b811314c0083e4  tools/wct/accept/process.py
442a9875a7715196fd51675b3206b4c3feba891898939ace94c8079436b40989  tests/unit/test_accept_campaign.py
b1367f104ff614028356a8de8587efe2f6afae5f1136cc2954db81ddbdfed499  tests/unit/test_sast_targets.py
```

## 2. CRAP antes y después

La misma LCOV fresca se pasó a `crap4py`, con el umbral vigente 6.0.

| Función | Antes | Después | Cambio observable |
|---|---:|---:|---|
| `semgrep_scope._python_files` | CC 7, cobertura 90%, CRAP **7.0** | CC 3, cobertura 100%, CRAP **3.0** | iteración delegada a filtro aislado |
| `semgrep_scope._build_dirs` | CC 7, cobertura 100%, CRAP **7.0** | CC 2, cobertura 100%, CRAP **2.0** | validación/resolución delegadas |
| `process._execute` | CC 6, cobertura 87.5%, CRAP **6.1** | CC 4, cobertura 100%, CRAP **4.0** | cleanup extraído y rama de streams ausentes cubierta |

Los ayudantes introducidos también cumplen: `_is_under_build` 2.0,
`_python_file` 5.0, `_build_values` 5.0, `_resolve_build` 2.0 y
`_close_streams` 3.0. La medición focal de cada archivo terminó sin funciones
sobre 6.0.

La comprobación suplementaria completa `crap4py tools/wct --max-crap 6`
sigue devolviendo exit 1 por 66 funciones fuera del foco. La clasificación
contra `origin/main` las identifica como deuda preexistente o cuerpos
mecánicamente trasladados; ninguna es un cuerpo modificado por esta reparación.
No se corrigió deuda ajena ni se subió el umbral. Por eso el resultado es
**CRAP focal conforme; CRAP global suplementario aún rojo**.

## 3. Cobertura y pruebas

Runtime acreditado: Python 3.13.14, pytest 9.1.1, pytest-cov 7.1.0,
coverage 7.15.4, diff-cover 10.5.1, crap4py 0.1.1 y mutmut 3.7.0, usando el
entorno completo del worktree de integración.

| Comprobación | Resultado |
|---|---|
| Pruebas focales | **110 passed**, 10.74 s |
| Colección después de tocar tests | **691/692 collected**, 1 property deselected, exit 0 |
| Suite completa (`-m 'not property'`) | **691 passed, 1 deselected**, 161.53 s, exit 0 |
| Cobertura total coverage.py | 3476/3951 líneas = 87.9777% de statements; 1074/1292 ramas = 83.1269% |
| Cobertura diferencial `diff-cover` | **91%**, 1163 líneas, 97 ausentes, exit 0 |
| Ramas de líneas Python añadidas | **315/350 = 90.00%**; 47 archivos fuente, 350 arcos LCOV considerados |
| `semgrep_scope.py` | 38/40 ramas = 95%; las ramas nuevas de `_python_files` quedan 4/4 |
| `process.py` | 24/24 ramas = 100%; `_execute` queda 6/6 |

LCOV fresco: `build/coverage-final/lcov.info`, SHA-256
`7b40893d328d47772c56d4aa1c8560c2508698a28d4cd518c9585e041c1ac692` en la
copia aislada. La métrica diferencial de 91% es de líneas; la métrica de
ramas añadidas se derivó directamente de `BRDA` y de los hunks `-U0`, por lo
que no se presenta la salida line-only de diff-cover como branch coverage.

## 4. Mutación acotada y Q-ACCMUT

Se ejecutó una campaña privada y aislada de mutmut sobre los dos módulos
focales, con las pruebas focales y sin tocar el worktree de integración. El
alcance generado fue:

- `process._close_streams`: 1/1 killed.
- `process._execute`: 32/32 killed.
- `semgrep_scope._is_under_build`: 2/2 killed.
- `semgrep_scope._python_file`: 12/12 killed.
- `semgrep_scope._python_files`: 14/14 killed.
- `semgrep_scope._build_values`: 7/7 killed.
- `semgrep_scope._resolve_build`: 5/5 killed.
- `semgrep_scope._build_dirs`: 14/14 killed.

Total del alcance objetivo: **87/87 killed, 0 survived, 0 errors y 0 no-run**.
Las funciones no focales quedaron fuera de la campaña y no reciben veredicto.
Esto es una mutación bounded de la reparación, no un PASS de G-MUT global.

El Q-ACCMUT histórico del expediente anterior permanece separado: 47/47
casos de aceptación clasificados, sin recampaña en este encargo. No se
reutiliza ese resultado como mutación de los nuevos helpers.

## 5. Dry, gate y verificación independiente

- La interfaz solicitada `wct dry --against ...` fue probada y el CLI la
  rechazó con exit 2 por argumento no reconocido. La forma real autorizada,
  `uv run wct dry tools/wct/gate/semgrep_scope.py tools/wct/accept/process.py --json`,
  terminó con `candidates=[]`, `errors=[]`, `units=16`, exit 0.
- El `fast` gate terminó **7/7 PASS**: G-META-2, G-RULES-DRIFT,
  G-SUPPRESS, G-DEBT, G-LINT, G-FMT y G-TYPE.
- El tier `commit` terminó **20 PASS / 1 FAIL**: todos los gates salvo
  G-META-1 pasaron; G-META-1 falla por el drift protegido preexistente de
  37 rutas (7 modificadas + 30 nuevas). G-TEST pasó con la batería normativa.
- El verifier independiente, sin escritura, revisó el diff, ejecutó las
  pruebas focales y la colección, confirmó mypy/ruff, recalculó CRAP focal,
  comparó comportamiento de `semgrep_scope` con la base y revisó la
  sensibilidad de `_close_streams`; no encontró un defecto bloqueante.
- El orden PROC-004 se detiene después de CRAP global suplementario: el dry
  focal anterior no sustituye la pasada DRY completa. **DRY completo no se
  ejecuta** mientras las 66 funciones ajenas sigan rojas; no se inventa un
  PASS global.

## 6. Drift, CI, presupuestos y siguiente acción

`uv run wct integrity check` continúa en exit 1 con el drift preexistente de
**37 rutas protegidas = 7 modificadas + 30 nuevas**. No se ejecutó bless. La
última corrida conocida de CI de la PR #53 (`35141138013`) falló en
`wct integrity check` por ese G-META-1; los pasos posteriores no corrieron.
Tras el push del commit documental se debe observar la nueva corrida, sin
interpretar el rojo de integridad como fallo de esta reparación.

Presupuesto consumido relevante: focal 10.74 s; colección 0.54 s; suite
completa 161.53 s; `fast` 3.3 s; mutación bounded ≈3.2 s de ejecución de
mutantes, además del arranque de la herramienta. No se gastó presupuesto DRY
completo ni de tier full.

Próxima acción mínima: revisión humana del residuo CRAP suplementario
preexistente/trasladado y autorización separada para DRY completo; después
seguir la cadena pre-bless ya definida. Este expediente no autoriza merge,
bless, manifest, tag, release ni cierre de AC1/beta.3.
