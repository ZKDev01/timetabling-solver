from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

from ..data_structures.timetabling import TimetablingInstance


@dataclass
class TimetablingResult:
  """Resultado del solver de Timetabling.

  Atributos:
    assignment: Diccionario {(curso, periodo): 0/1} para y_{ik}
    scheduled_by_period: Diccionario {periodo: set(cursos)} con cursos asignados por período
    period_load: Diccionario {periodo: cantidad de clases asignadas}
    unassigned_courses: Lista de cursos que no pudieron alcanzar k_i asignaciones
    ok: True si todos los cursos fueron asignados respetando restricciones
    messages: Lista de mensajes informativos/advertencias
  """
  assignment: Dict[Tuple[int, int], int]
  scheduled_by_period: Dict[int, Set[int]]
  period_load: Dict[int, int]
  unassigned_courses: List[int]
  ok: bool
  messages: List[str]


def solve_timetabling(instance: TimetablingInstance) -> TimetablingResult:
  """Resuelve la instancia de Timetabling con un enfoque greedy sencillo.

  Estrategia:
    - Valida preasignaciones y disponibilidad
    - Coloca preasignaciones primero
    - Ordena cursos por mayor k_i (más clases primero)
    - Para cada curso, intenta asignar períodos disponibles respetando:
        * capacidad por período (l_k)
        * conflictos por grupo (a lo sumo 1 por grupo en cada período)
        * matriz de conflictos (si existe), no co-ubicar cursos en conflicto
    - Garantiza que un curso no tenga más de una clase en el mismo período

  Devuelve estructura con el plan y métricas básicas.
  """
  q = instance.q
  p = instance.p

  assignment: Dict[Tuple[int, int], int] = {(i, k): 0 for i in instance.courses for k in range(1, p + 1)}
  scheduled_by_period: Dict[int, Set[int]] = {k: set() for k in range(1, p + 1)}
  period_load: Dict[int, int] = {k: 0 for k in range(1, p + 1)}
  messages: List[str] = []

  # Construir mapa curso -> grupos a los que pertenece
  course_to_groups: Dict[int, Set[int]] = {i: set() for i in instance.courses}
  for gi, group in enumerate(instance.groups):
    for c in group:
      if c in course_to_groups:
        course_to_groups[c].add(gi)

  # Validaciones básicas
  # 1) Preasignaciones no disponibles
  for (i, k), v in instance.preassignment.items():
    if v == 1 and instance.availability.get((i, k), 0) == 0:
      messages.append(f"Preasignación inválida: curso {i} en período {k} no está disponible")

  # 2) Exceso de preasignaciones para algún curso
  for i in instance.courses:
    num_pre = sum(instance.preassignment.get((i, k), 0) for k in range(1, p + 1))
    k_i = instance.k.get(i, 0)
    if num_pre > k_i:
      messages.append(f"Curso {i} tiene más preasignaciones ({num_pre}) que clases requeridas (k_i={k_i})")

  # Aplicar preasignaciones (si son factibles con capacidad)
  for i in instance.courses:
    for k in range(1, p + 1):
      if instance.preassignment.get((i, k), 0) == 1:
        if instance.availability.get((i, k), 0) == 1:
          # revisar capacidad y conflictos por grupo y matriz de conflictos
          if _can_place(instance, i, k, scheduled_by_period, period_load, course_to_groups):
            assignment[(i, k)] = 1
            scheduled_by_period[k].add(i)
            period_load[k] += 1
          else:
            messages.append(f"No se pudo colocar preasignación de curso {i} en período {k} por restricciones")

  # Ordenar cursos por mayor k_i y menor disponibilidad (más difíciles primero)
  def course_difficulty(course: int) -> Tuple[int, int]:
    k_i = instance.k.get(course, 0)
    avail_count = sum(instance.availability.get((course, kk), 0) for kk in range(1, p + 1))
    # Orden: k_i descendente, disponibilidad ascendente
    return (-k_i, avail_count)

  sorted_courses = sorted(instance.courses, key=course_difficulty)

  # Asignar greedily
  for i in sorted_courses:
    k_i = instance.k.get(i, 0)
    already = [k for k in range(1, p + 1) if assignment[(i, k)] == 1]
    needed = max(0, k_i - len(already))
    if needed == 0:
      continue

    # explorar períodos viables en orden creciente
    for k in range(1, p + 1):
      if needed == 0:
        break
      if assignment[(i, k)] == 1:
        continue  # ya está colocado aquí por preasignación
      if instance.availability.get((i, k), 0) == 0:
        continue
      if _can_place(instance, i, k, scheduled_by_period, period_load, course_to_groups):
        assignment[(i, k)] = 1
        scheduled_by_period[k].add(i)
        period_load[k] += 1
        needed -= 1

  # Evaluar cursos no asignados completamente
  unassigned: List[int] = []
  for i in instance.courses:
    assigned = sum(assignment[(i, k)] for k in range(1, p + 1))
    if assigned != instance.k.get(i, 0):
      unassigned.append(i)

  ok = len(unassigned) == 0
  if not ok:
    messages.append("Instancia no resuelta completamente; algunos cursos no alcanzaron k_i asignaciones")

  return TimetablingResult(
      assignment=assignment,
      scheduled_by_period=scheduled_by_period,
      period_load=period_load,
      unassigned_courses=unassigned,
      ok=ok,
      messages=messages,
  )


def _can_place(
    instance: TimetablingInstance,
    course: int,
    period: int,
    scheduled_by_period: Dict[int, Set[int]],
    period_load: Dict[int, int],
    course_to_groups: Dict[int, Set[int]],
) -> bool:
  """Verifica si se puede colocar el curso en el período respetando restricciones."""
  # capacidad
  cap_k = instance.l.get(period, 0)
  if period_load.get(period, 0) >= cap_k:
    return False

  # que el curso no esté ya asignado en este período (y_ik binario)
  if course in scheduled_by_period.get(period, set()):
    return False

  # conflictos por grupo: si algún curso del mismo grupo ya está en el período
  groups_course = course_to_groups.get(course, set())
  if groups_course:
    existing = scheduled_by_period.get(period, set())
    if existing:
      for other in existing:
        if not course_to_groups.get(other):
          continue
        # intersección de grupos: si comparten algún grupo, no puede colocarse
        if course_to_groups[other].intersection(groups_course):
          return False

  # matriz de conflictos (si existe)
  if instance.conflict_matrix:
    conflicts = instance.get_conflicting_courses(course)
    existing = scheduled_by_period.get(period, set())
    if conflicts.intersection(existing):
      return False

  return True
