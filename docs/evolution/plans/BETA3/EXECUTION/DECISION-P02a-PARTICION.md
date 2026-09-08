# P02a — revisión de frontera previa a nuevos archivos

El arquitecto autoriza esta partición después del challenge separado de
`verifier`. Medición del borrador por coder y arquitecto: `input_git.py` tiene
86 sitios estimados antes de completar streaming, preflight y proyección.
Se conservan los límites; no esperar al exceso para esconder complejidad.

## Siete rutas adicionales exactas

| Ruta | Responsabilidad |
|---|---|
| `tools/wct/evidence/input_git_protocol.py` | Framing binario y parsers Git |
| `tools/wct/evidence/input_git_process.py` | Proceso acotado, argv/entorno cerrado, terminación y recolección |
| `tools/wct/evidence/input_git_scope.py` | Proyección tipada de índice/HEAD/status a inputs |
| `tools/wct/evidence/input_git_preflight.py` | Consultas ordenadas y rechazo previo a status |
| `tools/wct/evidence/input_file_read.py` | Lectura no-follow, hash, límites y estabilidad |
| `tools/wct/evidence/input_file_root.py` | Validación/apertura de raíz y componentes |
| `tools/wct/evidence/input_selection.py` | Clasificación pura y única de exclusiones e intersecciones required |

Se suman al allowlist de §10 del contrato congelado: **17 archivos** en total,
12 módulos, cuatro archivos de tests y una feature. El handoff adicional
conserva su ruta exacta. No se autoriza ningún otro archivo de producto.

`input_files` mantiene la orquestación del recorrido; `input_git` la composición
de la observación Git. Dependencias acíclicas: composición → adaptadores y
helpers puros → tipos. La clasificación de exclusiones por path/tipo tendrá
una sola fuente pura, reutilizada por filesystem y proyección Git; no copiar
tablas ni esconder lecturas en ese helper. No crear módulos vacíos ni fachadas
sin responsabilidad real. Las funciones nuevas siguen la búsqueda de reuso.

## Identidad y verificación

API pública, comportamiento, catálogo de errores, matriz/Gherkin, límites y
umbrales permanecen intactos. El contrato original conserva SHA-256
`3e70dc048779ede4a73510de7a0ded493596e4661a3ba809aee5c52b45c13fa3`.
Esta acta es un componente adicional versionado del paquete, no una edición
retroactiva de ese archivo. El recibo del coder debe registrar ambos hashes.

La identidad final del candidato incluirá las 17 rutas en orden lexicográfico
de bytes UTF-8 con la serialización ENTREGA-v2. Cobertura, sitios, CRAP y
mutación focal incluyen los doce módulos, no solo la fachada. Conservar el
borrador/medición y la intervención arquitectónica; no contar esta partición
como reparación de un primer candidato completo que aún no se ha entregado.

Motivo: fronteras distintas de efectos/protocolo merecen módulos cohesionados;
no se relaja el contrato para encajar un archivo grande. El reviewer favoreció
la partición condicionada a esta autorización previa y al reuso de exclusiones.
Antes de comunicar la decisión, el coder precisó que la selección compartida
suma 32 sitios medidos y el módulo de manifest ya tiene 70. El arquitecto añade
`input_selection` como séptima ruta pura para materializar esa fuente única
sin importar un adaptador desde otro ni exceder el límite del serializador.
El challenge independiente cubrió las seis fronteras y exigió precisamente
esa fuente única; la ubicación pura séptima es decisión explícita del arquitecto.
El coder puede crear ahora esas siete rutas; bless sigue siendo humano.
