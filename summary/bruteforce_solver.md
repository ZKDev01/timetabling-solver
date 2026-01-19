# Solver por Fuerza Bruta Basado en Grafo de Conflicto (UCTP)

## Objetivo
- Resolver instancias del UCTP garantizando factibilidad (todas las restricciones duras satisfechas) usando una búsqueda exhaustiva sobre asignaciones factibles por sección.
- Estimar el tamaño máximo de instancia resoluble en tiempo razonable.

## Idea General
- Se transforma el problema a un grafo de conflicto implícito:
  - Vértices: asignaciones factibles (período, aula, profesor) para cada sección
  - Aristas: pares de asignaciones que no pueden coexistir (comparten aula/profesor en el mismo período o comparten currículum en el mismo período)
- Se elige exactamente una asignación por sección formando un conjunto independiente en el grafo.

## Construcción de Candidatos
- Por cada sección, se generan todas las combinaciones factibles (period, room_id, teacher_id) respetando:
  - Capacidad del aula suficiente y disponibilidad del aula
  - Profesor calificado para el curso y con disponibilidad en el período

## Verificación de Conflictos
- Unicidad de aula por período: no se permite (room_id, period) repetido
- Unicidad de profesor por período: no se permite (teacher_id, period) repetido
- No superposición por currículum: no se permite (curriculum_id, period) repetido

## Búsqueda (DFS) y Poda
- Orden “fail-first”: secciones ordenadas por menor número de candidatos
- DFS con backtracking:
  - Intenta colocar una asignación para la sección actual
  - Si no hay conflictos, avanza a la siguiente sección
  - Si hay conflictos, retrocede y prueba otra asignación
- Límite de tiempo para garantizar “tiempo razonable”; se detiene en la primera solución encontrada

## Salida del Solver
- Devuelve (es_factible, asignaciones, tiempo_segundos)
- Asignaciones como diccionario de Assignment por sección

## Benchmark y Tamaño Resoluble
- Parámetros del benchmark:
  - Límite de tiempo por instancia: 3.0 segundos
  - Disponibilidad completa y aulas con capacidad suficiente
  - Instancias aleatorias con cursos, currículos, aulas y profesores moderados
- Resultados observados:

  ```
  Tiny -> Factible: Sí | Secciones: 3 | Tiempo: 0.001s
  Small-4 -> Factible: Sí | Secciones: 4 | Tiempo: 0.000s
  Small-5 -> Factible: Sí | Secciones: 5 | Tiempo: 0.000s
  Small-6 -> Factible: Sí | Secciones: 5 | Tiempo: 0.001s
  Medium-8 -> Factible: Sí | Secciones: 9 | Tiempo: 0.000s
  Medium-10 -> Factible: Sí | Secciones: 7 | Tiempo: 0.000s
  ```

- Conclusión:
  - Bajo estas condiciones, el solver de fuerza bruta resuelve en ≤ 3s instancias con ~8–10 secciones de curso.
  - El tamaño resoluble depende de la densidad de conflictos y disponibilidad; instancias más restringidas reducen candidatos y pueden requerir más tiempo.
