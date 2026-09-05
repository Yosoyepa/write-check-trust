# SPEC-G1b-1 — BLOQUEADO: pertenencia, completitud y causa

Estado: **no autorizado**. Este archivo existe para que no queden dos
instrucciones vivas para el coder: la única spec implementable hoy es
SPEC-G1a-1. Se desbloquea solo cuando TODOS estos gates se cumplen:

1. G1a fusionada (con su bless propio; el de #36 no se recicla).
2. ADR-G1-02 y ADR-G1-04 aprobados por el humano.
3. Gherkin de G1b (borrador en GHERKIN-G1.md §G1b) aprobado por el humano.
4. RG12 ejecutado: presupuesto emparejado (≥3 repeticiones, mediana/rango,
   mismo entorno/scope/tests/versiones; suite/coverage/redteam/gate por
   separado) y aprobado por el humano.
5. RG13 demostrado: la repetición literal no deja vía a evidencia anterior
   (incluidos stats/asociaciones), sobre fixtures etiquetados.

## Contenido futuro (resumen; el detalle se escribe al desbloquear)

- Política única de frescura por repetición pública literal del alcance
  (ADR-G1-02) aplicada por gate y CLI al medir; sin `fresh=False`.
- Lector versionado del `.meta` (assert de esquema; divergencia → ERROR)
  para: exit 3 separado de exit 1 (RG05), inventario esperado-vs-recibido
  y pérdida parcial (RG06), versión soportada 3.7.0 exacta (RG10).
- Aislamiento/rechazo visible ante concurrencia; sin symlinks fuera de la
  raíz (RG11).
- Pruebas RG05/06/10/11/12/13 en fixtures nuevos etiquetados; nada de esto
  está implementado ni medido a la fecha de este dossier.

## Guardas

- No confundir con H0 (mapeo función→mutante, invalidación amplia, scope
  tools): G1b repite TODO el alcance actual; H0 selecciona.
- No marcar F01/F02 "cerrados" al terminar G1b: selección/scope/delta de
  tests siguen abiertos (H0/H1) — el claim se acota a lo implementado.
