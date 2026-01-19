from .coloring import dsatur_coloring, rlf_coloring
from .reduction import timetabling_to_graph
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

from ..data_structures.timetabling import TimetablingInstance
from ..data_structures.timetabling import Assignment
import time


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


# Funciones para el modelo dataclasses TimetablingInstance


def solve_timetabling_with_graph_coloring(instance: TimetablingInstance, heuristic: str = 'dsatur') -> None:
  """
  Resuelve el problema de Timetabling transformándolo a Graph Coloring,
  aplicando una heurística y reconstruyendo la asignación.
  Modifica la instancia in-place.
  """
  # Transformar Timetabling a Graph
  graph = timetabling_to_graph(instance)

  # Aplicar heurística de coloración
  if heuristic == 'dsatur':
    coloring = dsatur_coloring(graph)
  elif heuristic == 'rlf':
    coloring = rlf_coloring(graph)
  else:
    raise ValueError(f"Heurística desconocida: {heuristic}")

  # Extraer asignaciones de períodos para secciones
  section_periods = {}
  for vertex, color in coloring.items():
    if graph.node_types.get(vertex) == 'Section':
      section_id = vertex - 40000  # assuming offset
      period = color  # El color representa el período
      section_periods[section_id] = period

  # Asignar aulas y profesores basándose en las restricciones
  used_capacity = {p: {rid: 0 for rid in instance.rooms} for p in instance.periods}
  used_teachers = {p: set() for p in instance.periods}

  for section_id, section in instance.course_sections.items():
    course_name = section.course_name
    period = section_periods.get(section_id, 1)  # Usar período asignado, default 1

    # Encontrar aula disponible con capacidad suficiente y no usada en este período
    available_rooms = [
        rid for rid, room in instance.rooms.items()
        if period in room.availability and used_capacity[period][rid] + section.total_students <= room.capacity
    ]
    if not available_rooms:
      print(f"No hay aula disponible para {section.get_name()} en período {period}")
      continue
    room_id = available_rooms[0]  # Elegir la primera disponible
    used_capacity[period][room_id] += section.total_students

    # Encontrar profesor disponible que pueda impartir el curso y no usado en este período
    available_teachers = [
        tid for tid, teacher in instance.teachers.items()
        if course_name in teacher.course_names and period in teacher.availability and tid not in used_teachers[period]
    ]
    if not available_teachers:
      print(f"No hay profesor disponible para {section.get_name()} en período {period}")
      continue
    teacher_id = available_teachers[0]  # Elegir el primero disponible
    used_teachers[period].add(teacher_id)

    # Asignar la sección
    instance.assign_section(section_id, period, room_id, teacher_id)


def solve_timetabling_bruteforce(instance: TimetablingInstance, time_limit_sec: float = 5.0) -> Tuple[bool, Dict[int, Assignment], float]:
  """
  Fuerza bruta con transformación a vértices factibles y chequeo de conflictos (modelo de grafo).
  Selecciona exactamente una asignación por sección y verifica independencia (sin conflictos).
  Devuelve (es_factible, asignaciones, tiempo_segundos). Detiene cuando encuentra la primera solución.
  """
  start = time.time()

  # Construir candidatos por sección (vértices)
  section_candidates: Dict[int, List[Tuple[int, int, int]]] = {}
  for sid, section in instance.course_sections.items():
    candidates = []
    # profesores calificados
    qualified = [tid for tid, t in instance.teachers.items() if section.course_name in t.course_names]
    if not qualified:
      qualified = list(instance.teachers.keys())
    periods = list(instance.periods)
    rooms = list(instance.rooms.keys())
    for period in periods:
      for room_id in rooms:
        room = instance.rooms[room_id]
        if room.capacity < section.total_students:
          continue
        if period not in room.availability:
          continue
        for tid in qualified:
          teacher = instance.teachers[tid]
          if period not in teacher.availability:
            continue
          candidates.append((period, room_id, tid))
    section_candidates[sid] = candidates

  # Ordenar secciones por menor número de candidatos (fail-first)
  ordered_sections = sorted(instance.course_sections.keys(), key=lambda s: len(section_candidates[s]))

  used_room_period: Set[Tuple[int, int]] = set()
  used_teacher_period: Set[Tuple[int, int]] = set()
  used_curr_period: Set[Tuple[int, int]] = set()
  result_assignments: Dict[int, Assignment] = {}

  def conflicts(section_id: int, period: int, room_id: int, teacher_id: int) -> bool:
    # room-period y teacher-period únicos
    if (room_id, period) in used_room_period:
      return True
    if (teacher_id, period) in used_teacher_period:
      return True
    # conflictos por curriculum
    section = instance.course_sections[section_id]
    for curr_id in section.curriculum_ids:
      if (curr_id, period) in used_curr_period:
        return True
    return False

  def place(section_id: int, period: int, room_id: int, teacher_id: int) -> None:
    used_room_period.add((room_id, period))
    used_teacher_period.add((teacher_id, period))
    sec = instance.course_sections[section_id]
    for curr_id in sec.curriculum_ids:
      used_curr_period.add((curr_id, period))
    result_assignments[section_id] = Assignment(section_id=section_id, period=period, room_id=room_id, teacher_id=teacher_id)

  def unplace(section_id: int, period: int, room_id: int, teacher_id: int) -> None:
    used_room_period.discard((room_id, period))
    used_teacher_period.discard((teacher_id, period))
    sec = instance.course_sections[section_id]
    for curr_id in sec.curriculum_ids:
      used_curr_period.discard((curr_id, period))
    result_assignments.pop(section_id, None)

  found = False

  def dfs(idx: int) -> bool:
    nonlocal found
    if time.time() - start > time_limit_sec:
      return False
    if idx == len(ordered_sections):
      found = True
      return True
    sid = ordered_sections[idx]
    for (period, room_id, teacher_id) in section_candidates[sid]:
      if conflicts(sid, period, room_id, teacher_id):
        continue
      place(sid, period, room_id, teacher_id)
      if dfs(idx + 1):
        return True
      unplace(sid, period, room_id, teacher_id)
    return False

  dfs(0)
  elapsed = time.time() - start
  return found, (result_assignments if found else {}), elapsed
