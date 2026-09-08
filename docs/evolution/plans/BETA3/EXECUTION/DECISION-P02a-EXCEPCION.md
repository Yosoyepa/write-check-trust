# P02a — excepción Python y valores inmutables

El arquitecto precisa §3 del contrato congelado antes de la entrega. La frase
«tipos siguientes serán dataclasses inmutables» no debe aplicarse a
InputCaptureError: la tabla la identifica como excepción, pero su introducción
era ambigua. El coder lo consultó; no se adjudica como defecto oculto de R0.

**Decisión:** los ocho tipos de datos conservan dataclass frozen y tuplas.
InputCaptureError es una excepción Python normal con code, path y errno
observables según el catálogo aprobado. No se exige dataclass ni congelación
de la excepción, ni se impide al runtime asignar traceback/context/cause.
No introducir un framework de excepciones o mutabilidad en los snapshots.

Motivo reproducido por el arquitecto con Python 3.13.14: propagar una excepción
dataclass frozen a través de contextlib.contextmanager provoca
`FrozenInstanceError: cannot assign to field '__traceback__'`, enmascarando la
causa contratada. La compatibilidad de excepciones requiere esos metadatos
operativos mutables. No se presume que frozen signifique autenticación.

El contrato base conserva su hash histórico
`3e70dc048779ede4a73510de7a0ded493596e4661a3ba809aee5c52b45c13fa3`;
esta precisión forma parte adicional del paquete. Allowlist, Gherkin, códigos,
precedencia y límites no cambian. El coder debe probar preservación del error
al atravesar sus fronteras reales y registrar esta asistencia de contrato.

Corrección documental antes de integrar: el arquitecto escribió inicialmente
«nueve tipos de datos». El coder detectó el error de conteo: son ocho tipos de
datos más la excepción, nueve tipos en total. Esta corrección no cambia sus
campos ni crea un tipo adicional.
