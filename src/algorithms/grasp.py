import random
import copy
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from ..data_structures.timetabling import create_simple_example, TimetablingInstance


@dataclass
class GRASPSolution:
  """Representa una solución del problema de timetabling"""
  assignments: Dict[int, 'Assignment']
  cost: float
  is_feasible: bool
  violations: List[str]

  def __lt__(self, other):
    # Para ordenar soluciones: primero factibles, luego por costo
    if self.is_feasible != other.is_feasible:
      return self.is_feasible > other.is_feasible
    return self.cost < other.cost


class GRASPTimetabling:
  """
  Implementación del algoritmo GRASP para el problema de Timetabling.

  GRASP consta de dos fases:
  1. Fase constructiva: Construye una solución de forma greedy randomizada
  2. Fase de búsqueda local: Mejora la solución mediante movimientos locales
  """

  def __init__(self, instance, alpha: float = 0.3, max_iterations: int = 100,
               max_local_search_iterations: int = 50, verbose: bool = True):
    """
    Args:
        instance: Instancia del problema (TimetablingInstance)
        alpha: Parámetro de aleatorización (0 = greedy puro, 1 = aleatorio puro)
        max_iterations: Número máximo de iteraciones GRASP
        max_local_search_iterations: Iteraciones máximas de búsqueda local
        verbose: Si True, imprime información durante la ejecución
    """
    self.instance = instance
    self.alpha = alpha
    self.max_iterations = max_iterations
    self.max_local_search_iterations = max_local_search_iterations
    self.verbose = verbose
    self.best_solution: Optional[GRASPSolution] = None

  def solve(self) -> GRASPSolution:
    """Ejecuta el algoritmo GRASP"""
    if self.verbose:
      print(f"\n{'=' * 60}")
      print(f"Ejecutando GRASP con α={self.alpha}, {self.max_iterations} iteraciones")
      print(f"{'=' * 60}\n")

    self.best_solution = None

    for iteration in range(self.max_iterations):
      # Fase 1: Construcción greedy randomizada
      solution = self._construct_solution()

      # Fase 2: Búsqueda local
      if solution.is_feasible:
        solution = self._local_search(solution)

      # Actualizar mejor solución
      if self.best_solution is None or solution < self.best_solution:
        self.best_solution = copy.deepcopy(solution)
        if self.verbose:
          status = "FACTIBLE" if solution.is_feasible else "NO FACTIBLE"
          print(f"Iteración {iteration + 1}: Nueva mejor solución - "
                f"Costo: {solution.cost:.2f} ({status})")

    if self.verbose:
      self._print_final_results()

    return self.best_solution

  def _construct_solution(self) -> GRASPSolution:
    """
    Construye una solución de forma greedy randomizada.

    Para cada sección sin asignar:
    1. Evalúa todas las asignaciones posibles (período, aula, profesor)
    2. Crea una lista restringida de candidatos (RCL) con las mejores opciones
    3. Selecciona aleatoriamente una opción de la RCL
    """
    # Crear una copia temporal de la instancia
    temp_assignments = {}
    sections = list(self.instance.course_sections.keys())
    random.shuffle(sections)

    for section_id in sections:
      # Generar candidatos para esta sección
      candidates = self._generate_candidates(section_id, temp_assignments)

      if not candidates:
        candidate = self._get_random_assignment(section_id, temp_assignments)
      else:
        # Seleccionar de la RCL
        candidate = self._select_from_rcl(candidates)

      # Agregar la asignación
      temp_assignments[section_id] = candidate

    # Evaluar la solución construida
    return self._evaluate_solution(temp_assignments)

  def _generate_candidates(self, section_id: int,
                           current_assignments: Dict) -> List[Tuple[int, int, int, float]]:
    """
    Genera lista de candidatos factibles para una sección.

    Returns:
        Lista de tuplas (period, room_id, teacher_id, cost)
    """
    section = self.instance.course_sections[section_id]
    candidates = []

    # Obtener profesores calificados
    qualified_teachers = [
        tid for tid, teacher in self.instance.teachers.items()
        if section.course_name in teacher.course_names
    ]

    # Evaluar todas las combinaciones
    for period in self.instance.periods:
      for room_id, room in self.instance.rooms.items():
        for teacher_id in qualified_teachers:
          # Verificar factibilidad básica
          if self._is_candidate_feasible(
              section_id, period, room_id, teacher_id, current_assignments
          ):
            cost = self._evaluate_candidate(
                section_id, period, room_id, teacher_id
            )
            candidates.append((period, room_id, teacher_id, cost))

    return candidates

  def _is_candidate_feasible(self, section_id: int, period: int,
                             room_id: int, teacher_id: int,
                             current_assignments: Dict) -> bool:
    """Verifica si una asignación candidata es factible"""
    section = self.instance.course_sections[section_id]
    room = self.instance.rooms[room_id]
    teacher = self.instance.teachers[teacher_id]

    # 1. Verificar capacidad del aula
    if room.capacity < section.total_students:
      return False

    # 2. Verificar disponibilidad del aula
    if period not in room.availability:
      return False

    # 3. Verificar disponibilidad del profesor
    if period not in teacher.availability:
      return False

    # 4. Verificar conflictos con asignaciones actuales
    for assigned_section_id, assignment in current_assignments.items():
      if assignment.period == period:
        # Conflicto de profesor
        if assignment.teacher_id == teacher_id:
          return False

        # Conflicto de aula
        if assignment.room_id == room_id:
          return False

        # Conflicto de curriculum
        assigned_section = self.instance.course_sections[assigned_section_id]
        if section.curriculum_ids & assigned_section.curriculum_ids:
          return False

    return True

  def _evaluate_candidate(self, section_id: int, period: int,
                          room_id: int, teacher_id: int) -> float:
    """
    Evalúa el costo de una asignación candidata.

    Considera:
    - Penalización si el período no es preferido
    - Penalización por espacio desperdiciado en el aula
    - Bonificación por usar preferencias
    """
    section = self.instance.course_sections[section_id]
    room = self.instance.rooms[room_id]
    cost = 0.0

    # Penalización por período no preferido
    preferred_periods = self.instance.preferred_periods.get(section.course_name, set())
    if preferred_periods and period not in preferred_periods:
      cost += 1.0

    # Penalización por espacio desperdiciado (normalizado)
    wasted_space = (room.capacity - section.total_students) / room.capacity
    cost += wasted_space * 0.5

    # Verificar preferencias con valores
    # Iteramos sobre todas las preferencias para ver cuáles se cumplen
    for pref in self.instance.preferences:
      if pref.course_name != section.course_name:
        continue

      match = True

      # 1. Periodo
      if pref.period is not None and pref.period != period:
        match = False

      # 2. Aula
      if match and pref.room_name is not None:
        # Buscar ID del aula preferida
        pref_room_id = self.instance._find_room_by_name(pref.room_name)
        if pref_room_id != room_id:
          match = False

      # 3. Profesor
      if match and pref.teacher_name is not None:
        pref_teacher_id = self.instance._find_teacher_by_name(pref.teacher_name)
        if pref_teacher_id != teacher_id:
          match = False

      if match:
        cost -= pref.value  # Bonificación (restar costo)

    return cost

  def _select_from_rcl(self, candidates: List[Tuple[int, int, int, float]]) -> 'Assignment':
    """
    Selecciona un candidato de la Lista Restringida de Candidatos (RCL).

    La RCL contiene los candidatos con costo entre [min_cost, min_cost + alpha * (max_cost - min_cost)]
    """
    # Ordenar por costo
    candidates.sort(key=lambda x: x[3])

    # Calcular umbrales
    min_cost = candidates[0][3]
    max_cost = candidates[-1][3]
    threshold = min_cost + self.alpha * (max_cost - min_cost)

    # Construir RCL
    rcl = [c for c in candidates if c[3] <= threshold]

    # Seleccionar aleatoriamente de la RCL
    selected = random.choice(rcl)

    from dataclasses import dataclass

    @dataclass
    class Assignment:
      section_id: int
      period: int
      room_id: int
      teacher_id: int

    return Assignment(
        section_id=0,  # Se asignará después
        period=selected[0],
        room_id=selected[1],
        teacher_id=selected[2]
    )

  def _get_random_assignment(self, section_id: int, current_assignments: Dict) -> 'Assignment':
    section = self.instance.course_sections[section_id]

    qualified_teachers = [
        tid for tid, teacher in self.instance.teachers.items()
        if section.course_name in teacher.course_names
    ]

    if not qualified_teachers:
      qualified_teachers = list(self.instance.teachers.keys())

    from dataclasses import dataclass

    @dataclass
    class Assignment:
      section_id: int
      period: int
      room_id: int
      teacher_id: int

    periods = list(self.instance.periods)
    rooms = list(self.instance.rooms.keys())
    random.shuffle(periods)
    random.shuffle(rooms)
    random.shuffle(qualified_teachers)

    for period in periods:
      for room_id in rooms:
        for teacher_id in qualified_teachers:
          if self._is_candidate_feasible(section_id, period, room_id, teacher_id, current_assignments):
            return Assignment(
                section_id=section_id,
                period=period,
                room_id=room_id,
                teacher_id=teacher_id
            )

    return Assignment(
        section_id=section_id,
        period=random.choice(list(self.instance.periods)),
        room_id=random.choice(list(self.instance.rooms.keys())),
        teacher_id=random.choice(qualified_teachers)
    )

  def _local_search(self, solution: GRASPSolution) -> GRASPSolution:
    """
    Búsqueda local para mejorar la solución.

    Utiliza los siguientes movimientos:
    1. Cambio de período
    2. Cambio de aula
    3. Cambio de profesor
    4. Intercambio de asignaciones entre dos secciones
    """
    current_solution = solution
    improved = True
    iteration = 0

    while improved and iteration < self.max_local_search_iterations:
      improved = False
      iteration += 1

      # Probar diferentes tipos de movimientos
      neighbors = []

      # Movimiento 1: Cambiar período, aula o profesor de una sección
      neighbors.extend(self._generate_swap_neighbors(current_solution))

      # Movimiento 2: Intercambiar asignaciones entre dos secciones
      neighbors.extend(self._generate_exchange_neighbors(current_solution))

      # Evaluar vecinos
      for neighbor_assignments in neighbors:
        neighbor = self._evaluate_solution(neighbor_assignments)

        # Aceptar si es mejor
        if neighbor < current_solution:
          current_solution = neighbor
          improved = True
          break

    return current_solution

  def _generate_swap_neighbors(self, solution: GRASPSolution) -> List[Dict]:
    """Genera vecinos cambiando un atributo de una asignación"""
    neighbors = []

    for section_id, assignment in solution.assignments.items():
      section = self.instance.course_sections[section_id]

      # Cambiar período
      for new_period in self.instance.periods:
        if new_period != assignment.period:
          new_assignments = copy.deepcopy(solution.assignments)
          new_assignments[section_id].period = new_period
          neighbors.append(new_assignments)

      # Cambiar aula
      for new_room_id in self.instance.rooms.keys():
        if new_room_id != assignment.room_id:
          new_assignments = copy.deepcopy(solution.assignments)
          new_assignments[section_id].room_id = new_room_id
          neighbors.append(new_assignments)

      # Cambiar profesor (solo calificados)
      qualified_teachers = [
          tid for tid, teacher in self.instance.teachers.items()
          if section.course_name in teacher.course_names
      ]
      for new_teacher_id in qualified_teachers:
        if new_teacher_id != assignment.teacher_id:
          new_assignments = copy.deepcopy(solution.assignments)
          new_assignments[section_id].teacher_id = new_teacher_id
          neighbors.append(new_assignments)

    return neighbors

  def _generate_exchange_neighbors(self, solution: GRASPSolution) -> List[Dict]:
    """Genera vecinos intercambiando asignaciones entre dos secciones"""
    neighbors = []
    section_ids = list(solution.assignments.keys())

    # Limitar el número de intercambios para eficiencia
    sample_size = min(20, len(section_ids))
    sampled_ids = random.sample(section_ids, sample_size)

    for i in range(len(sampled_ids)):
      for j in range(i + 1, len(sampled_ids)):
        sid1, sid2 = sampled_ids[i], sampled_ids[j]

        new_assignments = copy.deepcopy(solution.assignments)

        # Intercambiar períodos
        new_assignments[sid1].period, new_assignments[sid2].period = \
            new_assignments[sid2].period, new_assignments[sid1].period
        neighbors.append(copy.deepcopy(new_assignments))

        # Restaurar y intercambiar aulas
        new_assignments = copy.deepcopy(solution.assignments)
        new_assignments[sid1].room_id, new_assignments[sid2].room_id = \
            new_assignments[sid2].room_id, new_assignments[sid1].room_id
        neighbors.append(copy.deepcopy(new_assignments))

    return neighbors

  def _evaluate_solution(self, assignments: Dict) -> GRASPSolution:
    """Evalúa una solución completa"""
    # Aplicar asignaciones temporalmente a la instancia
    original_assignments = self.instance.assignments.copy()
    self.instance.assignments = assignments

    # Verificar restricciones
    is_feasible, violations = self.instance.check_hard_constraints()

    # Calcular costo
    cost = self.instance.calculate_objective()

    if not is_feasible:
      repaired = self._repair_assignments(assignments)
      self.instance.assignments = repaired
      is_feasible, violations = self.instance.check_hard_constraints()
      cost = self.instance.calculate_objective()
      if not is_feasible:
        cost += 1000 * len(violations)

    # Restaurar asignaciones originales
    self.instance.assignments = original_assignments

    return GRASPSolution(
        assignments=copy.deepcopy(assignments),
        cost=cost,
        is_feasible=is_feasible,
        violations=violations
    )

  def _repair_assignments(self, assignments: Dict) -> Dict:
    changed = True
    while changed:
      changed = False
      for sid, a in list(assignments.items()):
        others = {k: v for k, v in assignments.items() if k != sid}
        if not self._is_candidate_feasible(sid, a.period, a.room_id, a.teacher_id, others):
          section = self.instance.course_sections[sid]
          qualified_teachers = [
              tid for tid, teacher in self.instance.teachers.items()
              if section.course_name in teacher.course_names
          ]
          periods = list(self.instance.periods)
          rooms = list(self.instance.rooms.keys())
          random.shuffle(periods)
          random.shuffle(rooms)
          random.shuffle(qualified_teachers)
          found = False
          for period in periods:
            for room_id in rooms:
              for teacher_id in qualified_teachers:
                if self._is_candidate_feasible(sid, period, room_id, teacher_id, others):
                  a.period = period
                  a.room_id = room_id
                  a.teacher_id = teacher_id
                  found = True
                  changed = True
                  break
              if found:
                break
            if found:
              break
    return assignments

  def _print_final_results(self):
    """Imprime los resultados finales"""
    print(f"\n{'=' * 60}")
    print("RESULTADOS FINALES")
    print(f"{'=' * 60}")

    if self.best_solution:
      print(f"\nMejor solución encontrada:")
      print(f"  Costo: {self.best_solution.cost:.2f}")
      print(f"  Factible: {'Sí' if self.best_solution.is_feasible else 'No'}")

      if not self.best_solution.is_feasible:
        print(f"\n  Violaciones ({len(self.best_solution.violations)}):")
        for violation in self.best_solution.violations[:10]:
          print(f"    - {violation}")
        if len(self.best_solution.violations) > 10:
          print(f"    ... y {len(self.best_solution.violations) - 10} más")

      # Aplicar mejor solución
      self.instance.assignments = self.best_solution.assignments

      print(f"\n  Asignaciones:")
      assignments = self.instance.get_assignment_details()
      for i, assignment in enumerate(assignments[:15], 1):
        print(f"    {i}. {assignment['sección']}: Período {assignment['periodo']}, "
              f"{assignment['aula']} con {assignment['profesor']}")
      if len(assignments) > 15:
        print(f"    ... y {len(assignments) - 15} asignaciones más")
    else:
      print("No se encontró ninguna solución")

    print(f"\n{'=' * 60}\n")


# Ejemplo de uso
if __name__ == "__main__":
  # Crear instancia del problema
  instance = create_simple_example()

  # Configurar y ejecutar GRASP
  grasp = GRASPTimetabling(
      instance,
      alpha=0.3,              # Balance greedy-aleatorio
      max_iterations=100,     # Iteraciones GRASP
      verbose=True
  )

  # Resolver
  solution = grasp.solve()

  # Ver resultados
  instance.print_summary()
