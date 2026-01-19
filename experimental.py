import time
import random
import statistics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
import json
from datetime import datetime

# Importar las clases necesarias (asumiendo que están disponibles)
from src.data_structures.timetabling import TimetablingInstance, CourseSection, Room, Teacher, Curriculum, Preference
from src.algorithms.grasp import GRASPTimetabling, GRASPSolution
from src.algorithms.timetabling_solver import solve_timetabling_with_graph_coloring
from src.algorithms.timetabling_solver import solve_timetabling_bruteforce


@dataclass
class ExperimentResult:
  """Resultado de un experimento individual"""
  algorithm: str
  instance_name: str
  instance_size: int
  cost: float
  objective_value: float  # Valor de la función objetivo (maximización)
  is_feasible: bool
  execution_time: float
  num_violations: int
  num_sections: int
  num_rooms: int
  num_teachers: int
  num_periods: int
  success: bool
  error_message: str = ""


class InstanceGenerator:
  """Generador robusto de instancias de prueba para Timetabling"""

  def __init__(self, seed: Optional[int] = None):
    if seed is not None:
      random.seed(seed)
      np.random.seed(seed)

  def generate_random_instance(
      self,
      num_courses: int,
      num_curriculums: int,
      num_rooms: int,
      num_teachers: int,
      num_periods: int,
      room_capacity_range: Tuple[int, int] = (50, 200),
      students_per_curriculum_range: Tuple[int, int] = (50, 150),
      courses_per_curriculum_range: Tuple[int, int] = (2, 4),
      availability_ratio: float = 0.8,
      name: str = "Random Instance"
  ) -> TimetablingInstance:
    """
    Genera una instancia aleatoria con parámetros configurables.

    Args:
        num_courses: Número de cursos
        num_curriculums: Número de curriculums
        num_rooms: Número de aulas
        num_teachers: Número de profesores
        num_periods: Número de períodos
        room_capacity_range: Rango de capacidad de aulas (min, max)
        students_per_curriculum_range: Rango de estudiantes por curriculum
        courses_per_curriculum_range: Rango de cursos por curriculum
        availability_ratio: Fracción de períodos en que recursos están disponibles
        name: Nombre de la instancia
    """
    instance = TimetablingInstance(name)

    # Generar períodos
    periods = list(range(1, num_periods + 1))

    # Crear curriculums
    course_names = [f"Curso {i + 1}" for i in range(num_courses)]
    curriculum_data = []

    for i in range(num_curriculums):
      num_students = random.randint(*students_per_curriculum_range)
      num_courses_in_curr = random.randint(*courses_per_curriculum_range)
      selected_courses = random.sample(course_names, min(num_courses_in_curr, len(course_names)))
      curriculum_data.append((f"Curriculum {i + 1}", num_students, selected_courses))

    # Agregar curriculums
    for name, students, courses in curriculum_data:
      instance.add_curriculum(name, students, courses)

    # Agregar cursos
    for course_name in course_names:
      # Encontrar curriculums que contienen este curso
      curriculum_names = [cd[0] for cd in curriculum_data if course_name in cd[2]]
      instance.add_course(course_name, curriculum_names)

    # Crear aulas
    for i in range(num_rooms):
      capacity = random.randint(*room_capacity_range)
      # Disponibilidad aleatoria
      available_periods = random.sample(
          periods,
          max(1, int(len(periods) * availability_ratio))
      )
      instance.add_room(f"Aula {i + 1}", capacity, available_periods)

    # Crear profesores
    for i in range(num_teachers):
      # Cada profesor puede impartir 2-4 cursos
      num_courses_taught = random.randint(2, min(4, len(course_names)))
      taught_courses = random.sample(course_names, num_courses_taught)

      # Disponibilidad aleatoria
      available_periods = random.sample(
          periods,
          max(1, int(len(periods) * availability_ratio))
      )
      instance.add_teacher(f"Profesor {i + 1}", taught_courses, available_periods)

    # Crear secciones
    instance.create_course_sections()

    # Generar preferencias con valores flotantes
    # 1. Preferencias de período
    for course_name in course_names:
      # Generar 1-3 preferencias de período
      num_prefs = random.randint(1, 3)
      pref_periods = random.sample(periods, min(num_prefs, len(periods)))

      for p in pref_periods:
        # Valor flotante aleatorio entre 1.0 y 5.0
        val = random.uniform(1.0, 5.0)
        instance.add_preference(course_name, p, None, None, val)

    # 2. Preferencias específicas (Curso, Periodo, Aula) o (Curso, Profesor)
    for _ in range(num_courses):
      course = random.choice(course_names)
      p = random.choice(periods)

      room_name = None
      if random.random() < 0.5:
        room_name = f"Aula {random.randint(1, num_rooms)}"

      teacher_name = None
      if random.random() < 0.5:
        teacher_name = f"Profesor {random.randint(1, num_teachers)}"

      if room_name or teacher_name:
        val = random.uniform(5.0, 10.0)
        instance.add_preference(course, p, room_name, teacher_name, val)

    return instance

  def generate_easy_instance(self) -> TimetablingInstance:
    """Genera una instancia fácil: recursos abundantes"""
    return self.generate_random_instance(
        num_courses=3,
        num_curriculums=2,
        num_rooms=5,
        num_teachers=4,
        num_periods=6,
        room_capacity_range=(100, 150),
        students_per_curriculum_range=(50, 80),
        courses_per_curriculum_range=(2, 3),
        availability_ratio=0.9,
        name="Easy Instance"
    )

  def generate_medium_instance(self) -> TimetablingInstance:
    """Genera una instancia mediana: recursos moderados"""
    return self.generate_random_instance(
        num_courses=6,
        num_curriculums=4,
        num_rooms=6,
        num_teachers=6,
        num_periods=8,
        room_capacity_range=(80, 120),
        students_per_curriculum_range=(60, 100),
        courses_per_curriculum_range=(2, 4),
        availability_ratio=0.7,
        name="Medium Instance"
    )

  def generate_hard_instance(self) -> TimetablingInstance:
    """Genera una instancia difícil: recursos limitados"""
    return self.generate_random_instance(
        num_courses=10,
        num_curriculums=6,
        num_rooms=6,
        num_teachers=8,
        num_periods=10,
        room_capacity_range=(60, 100),
        students_per_curriculum_range=(70, 120),
        courses_per_curriculum_range=(3, 5),
        availability_ratio=0.6,
        name="Hard Instance"
    )

  def generate_tight_capacity_instance(self) -> TimetablingInstance:
    """Caso de prueba: capacidad de aulas muy ajustada"""
    return self.generate_random_instance(
        num_courses=5,
        num_curriculums=3,
        num_rooms=3,
        num_teachers=5,
        num_periods=8,
        room_capacity_range=(70, 90),  # Capacidad ajustada
        students_per_curriculum_range=(80, 100),  # Muchos estudiantes
        courses_per_curriculum_range=(2, 3),
        availability_ratio=0.8,
        name="Tight Capacity Instance"
    )

  def generate_limited_availability_instance(self) -> TimetablingInstance:
    """Caso de prueba: disponibilidad limitada"""
    return self.generate_random_instance(
        num_courses=5,
        num_curriculums=3,
        num_rooms=5,
        num_teachers=5,
        num_periods=6,
        room_capacity_range=(100, 150),
        students_per_curriculum_range=(60, 90),
        courses_per_curriculum_range=(2, 3),
        availability_ratio=0.4,  # Baja disponibilidad
        name="Limited Availability Instance"
    )

  def generate_high_conflict_instance(self) -> TimetablingInstance:
    """Caso de prueba: muchos conflictos de curriculum"""
    instance = TimetablingInstance("High Conflict Instance")

    # Crear 4 curriculums que comparten muchos cursos
    courses = ["Curso A", "Curso B", "Curso C", "Curso D", "Curso E"]

    # Todos los curriculums comparten la mayoría de cursos
    instance.add_curriculum("Curr 1", 100, ["Curso A", "Curso B", "Curso C"])
    instance.add_curriculum("Curr 2", 100, ["Curso B", "Curso C", "Curso D"])
    instance.add_curriculum("Curr 3", 100, ["Curso C", "Curso D", "Curso E"])
    instance.add_curriculum("Curr 4", 100, ["Curso A", "Curso D", "Curso E"])

    # Agregar cursos
    for course in courses:
      instance.add_course(course, [])

    # Aulas suficientes pero no excesivas
    for i in range(4):
      instance.add_room(f"Aula {i + 1}", 150, list(range(1, 7)))

    # Profesores
    for i, course in enumerate(courses):
      instance.add_teacher(f"Prof {i + 1}", [course], list(range(1, 7)))

    instance.create_course_sections()
    return instance

  def generate_scalability_instances(self) -> List[TimetablingInstance]:
    """Genera conjunto de instancias para pruebas de escalabilidad"""
    instances = []

    # Instancias de tamaño creciente
    sizes = [
        # (3, 2, 3, 3, 5, "Tiny"),
        # (6, 3, 4, 4, 10, "Small"),
        # (8, 4, 5, 6, 20, "Medium"),
        (10, 6, 6, 8, 30, "Large"),
        # (16, 8, 7, 10, 12, "Medium-Large"),
        # (20, 10, 8, 12, 15, "Large")
    ]

    for courses, currs, rooms, teachers, periods, size_name in sizes:
      instance = self.generate_random_instance(
          num_courses=courses,
          num_curriculums=currs,
          num_rooms=rooms,
          num_teachers=teachers,
          num_periods=periods,
          room_capacity_range=(120, 200),
          students_per_curriculum_range=(50, 100),
          availability_ratio=1.0,
          name=f"{size_name} ({courses} courses)"
      )
      instances.append(instance)

    return instances

  def generate_metaheuristic_instances(self) -> List[TimetablingInstance]:
    """Genera 5 instancias grandes para metaheurísticas con alta factibilidad"""
    instances = []
    sizes = [
        (50, 10, 30, 30, 200, "Small-100"),
        (60, 10, 30, 30, 250, "Medium-150"),
        (70, 10, 35, 35, 300, "Medium-200"),
        (80, 10, 40, 40, 400, "Large-250"),
        (100, 10, 40, 40, 500, "Large-300"),
    ]

    for courses, currs, rooms, teachers, periods, label in sizes:
      instance = self.generate_random_instance(
          num_courses=courses,
          num_curriculums=currs,
          num_rooms=rooms,
          num_teachers=teachers,
          num_periods=periods,
          room_capacity_range=(150, 250),
          students_per_curriculum_range=(50, 100),
          availability_ratio=1.0,
          name=f"{label}"
      )
      instances.append(instance)
    return instances


@dataclass
class GAIndividual:
  """Individuo para el Algoritmo Genético"""
  assignments: Dict[int, 'Assignment']
  fitness: float = 0.0
  is_feasible: bool = False
  violations: List[str] = field(default_factory=list)


class GeneticAlgorithmTimetabling:
  """
  Implementación del Algoritmo Genético para el problema de Timetabling.

  Utiliza una población de soluciones que evoluciona a través de generaciones
  mediante selección, cruce y mutación.
  """

  def __init__(self, instance, population_size: int = 50, generations: int = 100,
               mutation_rate: float = 0.1, crossover_rate: float = 0.8,
               tournament_size: int = 3, verbose: bool = True, enable_local_search: bool = True):
    """
    Args:
        instance: Instancia del problema (TimetablingInstance)
        population_size: Tamaño de la población
        generations: Número de generaciones
        mutation_rate: Probabilidad de mutación
        crossover_rate: Probabilidad de cruce
        tournament_size: Tamaño del torneo para selección
        verbose: Si True, imprime información durante la ejecución
    """
    self.instance = instance
    self.population_size = population_size
    self.generations = generations
    self.mutation_rate = mutation_rate
    self.crossover_rate = crossover_rate
    self.tournament_size = tournament_size
    self.verbose = verbose
    self.enable_local_search = enable_local_search
    self.best_individual: Optional[GAIndividual] = None

  def solve(self) -> GRASPSolution:  # Retornar compatible con GRASP
    """Ejecuta el algoritmo genético"""
    if self.verbose:
      print(f"\n{'=' * 60}")
      print(f"Ejecutando Algoritmo Genético: Población {self.population_size}, {self.generations} generaciones")
      print(f"{'=' * 60}\n")

    # Inicializar población
    population = self._initialize_population()

    # Evaluar población inicial
    for individual in population:
      self._evaluate_individual(individual)
      # Aplicar búsqueda local a la población inicial también para mejorar arranque
      if self.enable_local_search and random.random() < 0.2:
        self._local_search(individual, max_steps=10)

    # Encontrar mejor inicial
    self.best_individual = min(population, key=lambda x: x.fitness)

    no_improvement_count = 0

    for generation in range(self.generations):
      # Crear nueva población
      new_population = []

      # Elitismo: mantener el mejor
      best_copy_assignments = self.best_individual.assignments.copy()
      new_population.append(GAIndividual(best_copy_assignments))
      # Re-evaluar para asegurar consistencia
      self._evaluate_individual(new_population[0])

      while len(new_population) < self.population_size:
        # Selección
        parent1 = self._tournament_selection(population)
        parent2 = self._tournament_selection(population)

        # Cruce
        if random.random() < self.crossover_rate:
          child1_assignments, child2_assignments = self._crossover(parent1.assignments, parent2.assignments)
          child1 = GAIndividual(child1_assignments)
          child2 = GAIndividual(child2_assignments)
        else:
          child1 = GAIndividual(parent1.assignments.copy())
          child2 = GAIndividual(parent2.assignments.copy())

        # Mutación
        self._mutate(child1)
        self._mutate(child2)

        # Búsqueda Local (Memetic Algorithm)
        # Aplicar con cierta probabilidad o siempre
        if self.enable_local_search and random.random() < 0.2:
          self._local_search(child1, max_steps=10)
        if self.enable_local_search and random.random() < 0.2:
          self._local_search(child2, max_steps=10)

        # Evaluar
        # Nota: _local_search ya actualiza el fitness, pero por seguridad/claridad
        # si _local_search no lo hiciera al final, deberíamos llamar _evaluate_individual.
        # En mi implementación _local_search mantendrá el fitness actualizado.

        new_population.extend([child1, child2])

      # Truncar población si es necesario (por el elitismo y pares agregados)
      population = new_population[:self.population_size]

      # Ordenar por fitness para facilitar elitismo en siguiente ronda
      population.sort(key=lambda x: x.fitness)

      # Actualizar mejor global
      current_best = population[0]
      if current_best.fitness < self.best_individual.fitness:
        self.best_individual = current_best
        no_improvement_count = 0
        if self.verbose:
          print(f"Generación {generation + 1}: Nueva mejor solución - "
                f"Fitness: {current_best.fitness:.2f} (Factible: {current_best.is_feasible})")
      else:
        no_improvement_count += 1
        if no_improvement_count >= 10 and self.best_individual.is_feasible:
          break

      # Diversificación si estamos estancados
      if no_improvement_count > 10:
        if self.verbose:
          print(f"  Detectado estancamiento en gen {generation + 1}. Diversificando...")
        # Reemplazar la mitad peor con nuevos aleatorios
        start_idx = len(population) // 2
        for i in range(start_idx, len(population)):
          assignments = self._generate_random_solution()
          ind = GAIndividual(assignments)
          self._evaluate_individual(ind)
          population[i] = ind
        no_improvement_count = 0

    if self.verbose:
      self._print_final_results()

    repaired_assignments = self._repair_assignments(self.best_individual.assignments)
    original_assignments = self.instance.assignments.copy()
    self.instance.assignments = repaired_assignments
    is_feasible, violations = self.instance.check_hard_constraints()
    cost = self.instance.calculate_objective()
    if not is_feasible:
      cost += 1000 * len(violations)
    self.instance.assignments = original_assignments
    return GRASPSolution(
        assignments=repaired_assignments,
        cost=cost,
        is_feasible=is_feasible,
        violations=violations
    )

  def _get_conflicting_section_ids(self, assignments: Dict) -> List[int]:
    """Identifica los IDs de secciones que causan conflictos"""
    conflicting_sections = set()

    # Mapeos para detectar solapamientos
    teacher_periods = {}  # (teacher_id, period) -> [section_ids]
    curriculum_periods = {}  # (curriculum_id, period) -> [section_ids]
    room_periods = {}  # (room_id, period) -> [section_ids]

    for section_id, assignment in assignments.items():
        # Verificar capacidad, disponibilidad y cualificación individualmente
      section = self.instance.course_sections[section_id]
      teacher = self.instance.teachers[assignment.teacher_id]
      room = self.instance.rooms[assignment.room_id]
      period = assignment.period

      # Cualificación
      if section.course_name not in teacher.course_names:
        conflicting_sections.add(section_id)

      # Disponibilidad Profesor
      if period not in teacher.availability:
        conflicting_sections.add(section_id)

      # Disponibilidad Aula
      if period not in room.availability:
        conflicting_sections.add(section_id)

      # Capacidad
      if room.capacity < section.total_students:
        conflicting_sections.add(section_id)

      # Preparar detección de solapamientos
      # Profesor
      tp_key = (assignment.teacher_id, period)
      if tp_key not in teacher_periods:
        teacher_periods[tp_key] = []
      teacher_periods[tp_key].append(section_id)

      # Aula
      rp_key = (assignment.room_id, period)
      if rp_key not in room_periods:
        room_periods[rp_key] = []
      room_periods[rp_key].append(section_id)

      # Curriculum
      for curr_id in section.curriculum_ids:
        cp_key = (curr_id, period)
        if cp_key not in curriculum_periods:
          curriculum_periods[cp_key] = []
        curriculum_periods[cp_key].append(section_id)

    # Procesar solapamientos
    for sids in teacher_periods.values():
      if len(sids) > 1:
        conflicting_sections.update(sids)

    for sids in room_periods.values():
      if len(sids) > 1:
        conflicting_sections.update(sids)

    for sids in curriculum_periods.values():
      if len(sids) > 1:
        conflicting_sections.update(sids)

    return list(conflicting_sections)

  def _is_candidate_feasible(self, section_id: int, period: int, room_id: int, teacher_id: int, current_assignments: Dict) -> bool:
    section = self.instance.course_sections[section_id]
    room = self.instance.rooms[room_id]
    teacher = self.instance.teachers[teacher_id]
    if section.course_name not in teacher.course_names:
      return False
    if room.capacity < section.total_students:
      return False
    if period not in room.availability:
      return False
    if period not in teacher.availability:
      return False
    for assigned_section_id, assignment in current_assignments.items():
      if assignment.period == period:
        if assignment.teacher_id == teacher_id:
          return False
        if assignment.room_id == room_id:
          return False
        assigned_section = self.instance.course_sections[assigned_section_id]
        if section.curriculum_ids & assigned_section.curriculum_ids:
          return False
    return True

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

  def _local_search(self, individual: GAIndividual, max_steps: int = 20):
    """
    Mejora iterativa (Hill Climbing) para arreglar conflictos o mejorar costo.
    Estrategia:
    1. Identificar secciones en conflicto.
    2. Si hay conflictos, intentar mover una sección conflictiva a una mejor posición.
    3. Si es factible, intentar mejorar la función objetivo (preferencias).
    """
    if not individual.assignments:
      return

    # Evaluar estado inicial si no está evaluado
    if individual.fitness == 0.0 and not individual.assignments:
      # Caso borde, no debería pasar si se llama bien
      pass
    else:
      # Asegurar que tenemos fitness actual
      self._evaluate_individual(individual)

    current_fitness = individual.fitness

    # Trabajar sobre los assignments del individuo
    # Nota: Modificamos el objeto Assignment existente o lo reemplazamos

    # Guardar estado global de la instancia para no corromperlo si algo falla,
    # aunque aquí modificamos el individual directamente.
    # Usaremos self.instance para validar, inyectando los assignments del individuo.
    original_instance_assignments = self.instance.assignments
    self.instance.assignments = individual.assignments

    for step in range(max_steps):
      # 1. Identificar candidatos
      conflicts = self._get_conflicting_section_ids(individual.assignments)

      is_feasible = len(conflicts) == 0

      if not is_feasible:
        # Prioridad: Resolver conflictos
        section_id = random.choice(conflicts)
      else:
        # Si es factible, intentar optimizar costo (soft constraints)
        # Elegir una sección aleatoria que no esté en su periodo preferido
        candidates = []
        for sid, assign in individual.assignments.items():
          section = self.instance.course_sections[sid]
          pref = self.instance.preferred_periods.get(section.course_name, set())
          if pref and assign.period not in pref:
            candidates.append(sid)

        if candidates:
          section_id = random.choice(candidates)
        else:
          # Si todos están perfectos o no hay preferencias, aleatorio total
          section_id = random.choice(list(individual.assignments.keys()))

      # 2. Generar vecino (movimiento)
      # Intentar encontrar un mejor lugar para esta sección
      assignment = individual.assignments[section_id]
      original_assignment_data = (assignment.period, assignment.room_id, assignment.teacher_id)

      best_move_fitness = current_fitness
      best_move_data = original_assignment_data
      found_improvement = False

      # Estrategia de vecindario: Probar X cambios aleatorios
      # Probar cambios de periodo (más común para resolver choques de tiempo)
      attempts = 5
      for _ in range(attempts):
        # Generar movimiento aleatorio
        move_type = random.choice(['period', 'room', 'teacher'])

        new_period = assignment.period
        new_room = assignment.room_id
        new_teacher = assignment.teacher_id

        if move_type == 'period':
          new_period = random.choice(list(self.instance.periods))
        elif move_type == 'room':
          new_room = random.choice(list(self.instance.rooms.keys()))
        elif move_type == 'teacher':
          # Solo profesores cualificados
          section = self.instance.course_sections[section_id]
          qualified = [t.id for t in self.instance.teachers.values() if section.course_name in t.course_names]
          if qualified:
            new_teacher = random.choice(qualified)

        # Aplicar cambio
        assignment.period = new_period
        assignment.room_id = new_room
        assignment.teacher_id = new_teacher

        # Evaluar delta
        # Nota: _evaluate_individual recalcula todo, es costoso pero seguro.
        # Para optimizar se podría calcular delta, pero por ahora usamos fuerza bruta en LS.

        # Hack: necesitamos actualizar fitness en el objeto individual
        # _evaluate_individual usa self.instance.assignments, que apunta a individual.assignments
        # así que solo llamamos a check constraints/objective

        is_valid_move, violations_move = self.instance.check_hard_constraints()
        cost_move = -self.instance.calculate_objective()
        if not is_valid_move:
          cost_move += 1000 * len(violations_move)

        if cost_move < best_move_fitness:
          best_move_fitness = cost_move
          best_move_data = (new_period, new_room, new_teacher)
          found_improvement = True
          # First improvement strategy (más rápido)
          break

      # 3. Aplicar o revertir
      if found_improvement:
        # Aplicar mejor encontrado (ya está aplicado si fue el último, pero aseguramos)
        assignment.period = best_move_data[0]
        assignment.room_id = best_move_data[1]
        assignment.teacher_id = best_move_data[2]
        current_fitness = best_move_fitness
        individual.fitness = current_fitness
        individual.is_feasible = (best_move_fitness < 1000)  # Asumiendo peso 1000 por violación
        individual.violations = []  # Se actualizaría en evaluación completa si fuera necesario
      else:
        # Revertir a original
        assignment.period = original_assignment_data[0]
        assignment.room_id = original_assignment_data[1]
        assignment.teacher_id = original_assignment_data[2]

    # Restaurar asignaciones de instancia original
    self.instance.assignments = original_instance_assignments

    # Evaluación final para dejar el individuo consistente (violations list, etc)
    self._evaluate_individual(individual)

  def _initialize_population(self) -> List[GAIndividual]:
    """Inicializa la población con soluciones aleatorias"""
    population = []
    for _ in range(self.population_size):
      assignments = self._generate_random_solution()
      individual = GAIndividual(assignments)
      population.append(individual)
    return population

  def _generate_random_solution(self) -> Dict[int, 'Assignment']:
    assignments = {}
    for section_id in self.instance.course_sections.keys():
      section = self.instance.course_sections[section_id]
      qualified_teachers = [
          tid for tid, teacher in self.instance.teachers.items()
          if section.course_name in teacher.course_names
      ]
      if not qualified_teachers:
        qualified_teachers = list(self.instance.teachers.keys())

      periods = list(self.instance.periods)
      rooms = list(self.instance.rooms.keys())
      random.shuffle(periods)
      random.shuffle(rooms)
      random.shuffle(qualified_teachers)

      chosen = None
      for period in periods:
        for room_id in rooms:
          room = self.instance.rooms[room_id]
          if room.capacity < section.total_students:
            continue
          if period not in room.availability:
            continue
          for teacher_id in qualified_teachers:
            teacher = self.instance.teachers[teacher_id]
            if period not in teacher.availability:
              continue
            conflict = False
            for sid, a in assignments.items():
              if a.period == period:
                if a.room_id == room_id or a.teacher_id == teacher_id:
                  conflict = True
                  break
                other_section = self.instance.course_sections[sid]
                if section.curriculum_ids & other_section.curriculum_ids:
                  conflict = True
                  break
            if not conflict:
              chosen = (period, room_id, teacher_id)
              break
          if chosen:
            break
        if chosen:
          break

      if not chosen:
        period = random.choice(list(self.instance.periods))
        room_id = random.choice(list(self.instance.rooms.keys()))
        teacher_id = random.choice(qualified_teachers)
      else:
        period, room_id, teacher_id = chosen

      @dataclass
      class Assignment:
        section_id: int
        period: int
        room_id: int
        teacher_id: int

      assignments[section_id] = Assignment(section_id, period, room_id, teacher_id)
    return assignments

  def _evaluate_individual(self, individual: GAIndividual):
    """Evalúa el fitness de un individuo"""
    # Aplicar asignaciones temporalmente
    original_assignments = self.instance.assignments.copy()
    self.instance.assignments = individual.assignments

    # Verificar restricciones
    is_feasible, violations = self.instance.check_hard_constraints()
    cost = -self.instance.calculate_objective()

    # Penalizar no factibles
    if not is_feasible:
      cost += 1000 * len(violations)

    individual.fitness = cost
    individual.is_feasible = is_feasible
    individual.violations = violations

    # Restaurar
    self.instance.assignments = original_assignments

  def _tournament_selection(self, population: List[GAIndividual]) -> GAIndividual:
    """Selección por torneo"""
    tournament = random.sample(population, self.tournament_size)
    return min(tournament, key=lambda x: x.fitness)

  def _crossover(self, parent1_assignments: Dict, parent2_assignments: Dict) -> Tuple[Dict, Dict]:
    """Cruce de un punto"""
    section_ids = list(parent1_assignments.keys())
    if len(section_ids) < 2:
      return parent1_assignments.copy(), parent2_assignments.copy()

    crossover_point = random.randint(1, len(section_ids) - 1)

    child1_assignments = {}
    child2_assignments = {}

    for i, section_id in enumerate(section_ids):
      if i < crossover_point:
        child1_assignments[section_id] = parent1_assignments[section_id]
        child2_assignments[section_id] = parent2_assignments[section_id]
      else:
        child1_assignments[section_id] = parent2_assignments[section_id]
        child2_assignments[section_id] = parent1_assignments[section_id]

    return child1_assignments, child2_assignments

  def _mutate(self, individual: GAIndividual):
    """Mutación: cambiar aleatoriamente una asignación"""
    if random.random() < self.mutation_rate:
      section_ids = list(individual.assignments.keys())
      if section_ids:
        section_id = random.choice(section_ids)
        assignment = individual.assignments[section_id]

        # Mutar uno de los atributos aleatoriamente
        mutation_type = random.choice(['period', 'room', 'teacher'])

        if mutation_type == 'period':
          assignment.period = random.choice(list(self.instance.periods))
        elif mutation_type == 'room':
          assignment.room_id = random.choice(list(self.instance.rooms.keys()))
        elif mutation_type == 'teacher':
          section = self.instance.course_sections[section_id]
          qualified_teachers = [
              tid for tid, teacher in self.instance.teachers.items()
              if section.course_name in teacher.course_names
          ]
          if qualified_teachers:
            assignment.teacher_id = random.choice(qualified_teachers)

  def _print_final_results(self):
    """Imprime los resultados finales"""
    print(f"\n{'=' * 60}")
    print("RESULTADOS FINALES - ALGORITMO GENÉTICO")
    print(f"{'=' * 60}")

    if self.best_individual:
      print(f"\nMejor solución encontrada:")
      print(f"  Fitness: {self.best_individual.fitness:.2f}")
      print(f"  Factible: {'Sí' if self.best_individual.is_feasible else 'No'}")

      if not self.best_individual.is_feasible:
        print(f"\n  Violaciones ({len(self.best_individual.violations)}):")
        for violation in self.best_individual.violations[:10]:
          print(f"    - {violation}")
        if len(self.best_individual.violations) > 10:
          print(f"    ... y {len(self.best_individual.violations) - 10} más")

      # Aplicar mejor solución
      self.instance.assignments = self.best_individual.assignments

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


class ExperimentRunner:
  """Ejecutor de experimentos comparativos"""

  def __init__(self, timeout: float = 300.0):
    """
    Args:
        timeout: Tiempo máximo de ejecución por algoritmo en segundos
    """
    self.timeout = timeout
    self.results: List[ExperimentResult] = []

  def run_genetic_algorithm(self, instance: TimetablingInstance) -> ExperimentResult:
    """Ejecuta el algoritmo Genético en una instancia"""
    start_time = time.time()

    try:
      sections = len(instance.course_sections)
      population = 22 if sections >= 140 else max(24, min(64, int(sections * 0.22)))
      generations = 15 if sections >= 140 else max(22, min(60, int(16 + sections * 0.1)))
      mutation = 0.06 if sections >= 150 else 0.08
      crossover = 0.85
      tour = 4
      ga = GeneticAlgorithmTimetabling(
          instance,
          population_size=population,
          generations=generations,
          mutation_rate=mutation,
          crossover_rate=crossover,
          tournament_size=tour,
          verbose=False
      )

      solution = ga.solve()

      execution_time = time.time() - start_time

      return ExperimentResult(
          algorithm="Genetic Algorithm",
          instance_name=instance.name,
          instance_size=len(instance.course_sections),
          cost=solution.cost if solution else float('inf'),
          objective_value=-solution.cost if solution and solution.cost != float('inf') else 0.0,
          is_feasible=solution.is_feasible if solution else False,
          execution_time=execution_time,
          num_violations=len(solution.violations) if solution else 0,
          num_sections=len(instance.course_sections),
          num_rooms=len(instance.rooms),
          num_teachers=len(instance.teachers),
          num_periods=len(instance.periods),
          success=True
      )
    except Exception as e:
      return ExperimentResult(
          algorithm="Genetic Algorithm",
          instance_name=instance.name,
          instance_size=len(instance.course_sections),
          cost=float('inf'),
          objective_value=0.0,
          is_feasible=False,
          execution_time=time.time() - start_time,
          num_violations=0,
          num_sections=len(instance.course_sections),
          num_rooms=len(instance.rooms),
          num_teachers=len(instance.teachers),
          num_periods=len(instance.periods),
          success=False,
          error_message=str(e)
      )

  def run_genetic_algorithm_custom(
      self,
      instance: TimetablingInstance,
      population: int,
      generations: int,
      mutation: float,
      crossover: float,
      tour: int
  ) -> ExperimentResult:
    start_time = time.time()
    try:
      ga = GeneticAlgorithmTimetabling(
          instance,
          population_size=population,
          generations=generations,
          mutation_rate=mutation,
          crossover_rate=crossover,
          tournament_size=tour,
          verbose=False
      )
      solution = ga.solve()
      execution_time = time.time() - start_time
      return ExperimentResult(
          algorithm="Genetic Algorithm",
          instance_name=instance.name,
          instance_size=len(instance.course_sections),
          cost=solution.cost if solution else float('inf'),
          objective_value=-solution.cost if solution and solution.cost != float('inf') else 0.0,
          is_feasible=solution.is_feasible if solution else False,
          execution_time=execution_time,
          num_violations=len(solution.violations) if solution else 0,
          num_sections=len(instance.course_sections),
          num_rooms=len(instance.rooms),
          num_teachers=len(instance.teachers),
          num_periods=len(instance.periods),
          success=True
      )
    except Exception as e:
      return ExperimentResult(
          algorithm="Genetic Algorithm",
          instance_name=instance.name,
          instance_size=len(instance.course_sections),
          cost=float('inf'),
          objective_value=0.0,
          is_feasible=False,
          execution_time=time.time() - start_time,
          num_violations=0,
          num_sections=len(instance.course_sections),
          num_rooms=len(instance.rooms),
          num_teachers=len(instance.teachers),
          num_periods=len(instance.periods),
          success=False,
          error_message=str(e)
      )

  def run_grasp(
      self,
      instance: TimetablingInstance,
      alpha: float = 0.3,
      max_iterations: int = 100
  ) -> ExperimentResult:
    """Ejecuta GRASP en una instancia"""
    start_time = time.time()

    try:
      sections = len(instance.course_sections)
      iters = max_iterations
      a = alpha
      ls_iters = 10 if sections >= 140 else 30
      grasp = GRASPTimetabling(
          instance,
          alpha=a,
          max_iterations=iters,
          max_local_search_iterations=ls_iters,
          verbose=False
      )

      solution = grasp.solve()

      execution_time = time.time() - start_time

      return ExperimentResult(
          algorithm="GRASP",
          instance_name=instance.name,
          instance_size=len(instance.course_sections),
          cost=solution.cost if solution else float('inf'),
          objective_value=-solution.cost if solution and solution.cost != float('inf') else 0.0,
          is_feasible=solution.is_feasible if solution else False,
          execution_time=execution_time,
          num_violations=len(solution.violations) if solution else 0,
          num_sections=len(instance.course_sections),
          num_rooms=len(instance.rooms),
          num_teachers=len(instance.teachers),
          num_periods=len(instance.periods),
          success=True
      )
    except Exception as e:
      return ExperimentResult(
          algorithm="GRASP",
          instance_name=instance.name,
          instance_size=len(instance.course_sections),
          cost=float('inf'),
          objective_value=0.0,
          is_feasible=False,
          execution_time=time.time() - start_time,
          num_violations=0,
          num_sections=len(instance.course_sections),
          num_rooms=len(instance.rooms),
          num_teachers=len(instance.teachers),
          num_periods=len(instance.periods),
          success=False,
          error_message=str(e)
      )

  def run_graph_coloring_heuristic(
      self,
      instance: TimetablingInstance,
      heuristic: str = 'dsatur'
  ) -> ExperimentResult:
    """Ejecuta algoritmo basado en coloración de grafos"""
    start_time = time.time()

    try:
      # Hacer copia para no modificar la original
      import copy
      instance_copy = copy.deepcopy(instance)

      solve_timetabling_with_graph_coloring(instance_copy, heuristic=heuristic)

      execution_time = time.time() - start_time

      # Verificar solución
      is_feasible, violations = instance_copy.check_hard_constraints()
      cost = instance_copy.calculate_objective()

      return ExperimentResult(
          algorithm=f"GraphColoring-{heuristic.upper()}",
          instance_name=instance.name,
          instance_size=len(instance.course_sections),
          cost=cost,
          objective_value=(-cost if is_feasible else 0.0),
          is_feasible=is_feasible,
          execution_time=execution_time,
          num_violations=len(violations),
          num_sections=len(instance.course_sections),
          num_rooms=len(instance.rooms),
          num_teachers=len(instance.teachers),
          num_periods=len(instance.periods),
          success=True
      )
    except Exception as e:
      return ExperimentResult(
          algorithm=f"GraphColoring-{heuristic.upper()}",
          instance_name=instance.name,
          instance_size=len(instance.course_sections),
          cost=float('inf'),
          objective_value=0.0,
          is_feasible=False,
          execution_time=time.time() - start_time,
          num_violations=0,
          num_sections=len(instance.course_sections),
          num_rooms=len(instance.rooms),
          num_teachers=len(instance.teachers),
          num_periods=len(instance.periods),
          success=False,
          error_message=str(e)
      )

  def run_experiment_suite(
      self,
      instances: List[TimetablingInstance],
      algorithms: List[str] = ['GRASP', 'DSatur', 'RLF', 'Genetic'],
      repetitions: int = 5
  ) -> pd.DataFrame:
    """
    Ejecuta suite completa de experimentos

    Args:
        instances: Lista de instancias a probar
        algorithms: Lista de algoritmos a ejecutar
        repetitions: Número de repeticiones por instancia
    """
    self.results = []

    total_experiments = len(instances) * len(algorithms) * repetitions
    current = 0

    print(f"Ejecutando {total_experiments} experimentos...")

    for instance in instances:
      print(f"\n{'=' * 60}")
      print(f"Instancia: {instance.name}")
      print(f"  Secciones: {len(instance.course_sections)}")
      print(f"  Aulas: {len(instance.rooms)}")
      print(f"  Profesores: {len(instance.teachers)}")
      print(f"  Períodos: {len(instance.periods)}")
      print(f"{'=' * 60}")

      for algo in algorithms:
        print(f"\nAlgoritmo: {algo}")

        for rep in range(repetitions):
          current += 1
          progress = (current / total_experiments) * 100
          print(f"  Repetición {rep + 1}/{repetitions} ({progress:.1f}% total)", end='')

          match algo:
            case "RLF":
              result = self.run_graph_coloring_heuristic(instance, 'rlf')
            case "DSatur":
              result = self.run_graph_coloring_heuristic(instance, 'dsatur')
            case "GRASP":
              result = self.run_grasp(instance)
            case "Genetic":
              result = self.run_genetic_algorithm(instance)

          self.results.append(result)

          status = "✓" if result.is_feasible else "✗"
          display_value = (-result.cost if result.is_feasible else result.cost)
          print(f" - {status} Tiempo: {result.execution_time:.3f}s, Puntaje: {display_value:.2f}")

    return self.get_results_dataframe()

  def get_results_dataframe(self) -> pd.DataFrame:
    """Convierte resultados a DataFrame de pandas"""
    data = []
    for result in self.results:
      data.append({
          'Algorithm': result.algorithm,
          'Instance': result.instance_name,
          'Size': result.instance_size,
          'Cost': result.cost,
          'Score': -result.cost,
          'Feasible': result.is_feasible,
          'Time': result.execution_time,
          'Violations': result.num_violations,
          'Sections': result.num_sections,
          'Rooms': result.num_rooms,
          'Teachers': result.num_teachers,
          'Periods': result.num_periods,
          'Success': result.success
      })

    return pd.DataFrame(data)

  def generate_summary_statistics(self) -> pd.DataFrame:
    """Genera estadísticas resumidas por algoritmo e instancia"""
    df = self.get_results_dataframe()

    summary = df.groupby(['Algorithm', 'Instance']).agg({
        'Score': ['mean', 'std', 'min'],
        'Time': ['mean', 'std', 'min', 'max'],
        'Feasible': 'sum',
        'Success': 'sum',
        'Size': 'first'
    }).round(4)

    return summary

  def plot_results(self, save_path: Optional[str] = None):
    """Genera visualizaciones de los resultados"""
    df = self.get_results_dataframe()

    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    samples_by_algo = df.groupby('Algorithm').size()

    # 1. Tiempo de ejecución por tamaño
    ax1 = axes[0, 0]
    for algo in df['Algorithm'].unique():
      algo_data = df[df['Algorithm'] == algo]
      grouped = algo_data.groupby('Size')['Time'].mean()
      ax1.plot(grouped.index, grouped.values, marker='o', label=algo)
    ax1.set_xlabel('Tamaño de Instancia (# secciones)')
    ax1.set_ylabel('Tiempo de Ejecución (s)')
    ax1.set_title('Escalabilidad: Tiempo vs Tamaño')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Calidad de solución (costo)
    ax2 = axes[0, 1]
    feasible_df = df[df['Feasible'] == True]
    if not feasible_df.empty:
      feasible_df.boxplot(column='Score', by='Algorithm', ax=ax2)
      ax2.set_xlabel('Algoritmo')
      ax2.set_ylabel('Puntaje de Solución')
      ax2.set_title(f'Calidad de Solución (solo factibles, mayor es mejor)\nMuestras por algoritmo: {samples_by_algo.to_dict()}')
      plt.sca(ax2)
      plt.xticks(rotation=45)

    # 3. Tasa de éxito
    ax3 = axes[1, 0]
    success_rates = df.groupby('Algorithm')['Feasible'].mean() * 100
    success_rates.plot(kind='bar', ax=ax3, color='skyblue')
    ax3.set_ylabel('Tasa de Éxito (%)')
    ax3.set_title(f'Tasa de Soluciones Factibles\nMuestras por algoritmo: {samples_by_algo.to_dict()}')
    ax3.set_xlabel('Algoritmo')
    plt.sca(ax3)
    plt.xticks(rotation=45)
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. Tiempo vs Costo (trade-off)
    ax4 = axes[1, 1]
    for algo in df['Algorithm'].unique():
      algo_data = df[(df['Algorithm'] == algo) & (df['Feasible'] == True)]
      if not algo_data.empty:
        ax4.scatter(algo_data['Time'], algo_data['Score'],
                    label=algo, alpha=0.6, s=50)
    ax4.set_xlabel('Tiempo de Ejecución (s)')
    ax4.set_ylabel('Puntaje de Solución')
    ax4.set_title('Trade-off: Tiempo vs Calidad')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
      plt.savefig(save_path, dpi=300, bbox_inches='tight')
      print(f"\nGráficas guardadas en: {save_path}")

    plt.show()


def experimental_result() -> None:
  "Función Principal para ejecutar experimentos completos"
  generator = InstanceGenerator(seed=42)
  runner = ExperimentRunner(timeout=600)

  print("Generando instancias para metaheurísticas ...")
  instances = generator.generate_metaheuristic_instances()

  print("Ejecutando experimentos (metaheurísticas) ...")
  algorithms = ['GRASP', 'Genetic']
  repetitions = 20

  df_results = runner.run_experiment_suite(
      instances=instances,
      algorithms=algorithms,
      repetitions=repetitions
  )

  # Generar estadísticas
  print("Generando estadísticas...")
  summary = runner.generate_summary_statistics()
  print(summary)

  # Guardar resultados
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  df_results.to_csv(f'results_{timestamp}.csv', index=False)
  summary.to_csv(f'summary_{timestamp}.csv')

  # Generar visualizaciones
  print("Generando visualizaciones...")
  runner.plot_results(save_path=f'plots_{timestamp}.png')


def bruteforce_benchmark() -> None:
  generator = InstanceGenerator(seed=42)
  print("Benchmark brute force (graph-based DFS) ...")
  sizes = [
      (3, 2, 3, 3, 6, "Tiny"),
      (4, 2, 3, 3, 6, "Small-4"),
      (5, 3, 4, 4, 8, "Small-5"),
      (6, 3, 4, 4, 10, "Small-6"),
      (8, 4, 5, 5, 12, "Medium-8"),
      (10, 4, 5, 6, 12, "Medium-10"),
      (15, 5, 6, 8, 20, "Large-15"),
      (20, 8, 8, 10, 35, "Large-20"),
      (40, 15, 15, 15, 60, "Large-40"),
      (80, 30, 30, 30, 100, "Large-80"),
      (100, 50, 50, 50, 150, "Large-100"),
      # (150, 75, 75, 75, 250, "Large-150"),
      # (200, 100, 100, 100, 300, "Large-200"),
      # (250, 125, 125, 125, 400, "Large-250"),
      # A partir de aquí fuerza bruta se rompe
      # (300, 150, 150, 150, 400, "Large-300"),
      # (400, 200, 200, 200, 800, "Large-400-1"),
      # (400, 250, 250, 250, 800, "Large-400-2"),

  ]
  for courses, currs, rooms, teachers, periods, label in sizes:
    instance = generator.generate_random_instance(
        num_courses=courses,
        num_curriculums=currs,
        num_rooms=rooms,
        num_teachers=teachers,
        num_periods=periods,
        room_capacity_range=(120, 200),
        students_per_curriculum_range=(50, 100),
        availability_ratio=1.0,
        name=f"{label}"
    )
    ok, assignments, elapsed = solve_timetabling_bruteforce(instance, time_limit_sec=160.0)
    print(f"{label} -> Factible: {'Sí' if ok else 'No/Timeout'} | Secciones: {len(instance.course_sections)} | Tiempo: {elapsed:.3f}s")


def _compute_candidates_stats(instance: TimetablingInstance) -> Dict[str, float]:
  section_candidates = {}
  for sid, section in instance.course_sections.items():
    candidates = 0
    qualified = [tid for tid, t in instance.teachers.items() if section.course_name in t.course_names] or list(instance.teachers.keys())
    for period in instance.periods:
      for rid, room in instance.rooms.items():
        if room.capacity < section.total_students:
          continue
        if period not in room.availability:
          continue
        for tid in qualified:
          teacher = instance.teachers[tid]
          if period not in teacher.availability:
            continue
          candidates += 1
    section_candidates[sid] = candidates
  counts = list(section_candidates.values())
  total_vertices = float(sum(counts))
  min_c = float(min(counts)) if counts else 0.0
  max_c = float(max(counts)) if counts else 0.0
  mean_c = float(np.mean(counts)) if counts else 0.0
  median_c = float(np.median(counts)) if counts else 0.0
  sum_log = float(sum(np.log(c) for c in counts if c > 0))
  approx_combinations = float(np.exp(sum_log)) if sum_log > 0 else 0.0
  return {
      "total_vertices": total_vertices,
      "min_candidates": min_c,
      "max_candidates": max_c,
      "mean_candidates": mean_c,
      "median_candidates": median_c,
      "sum_log_candidates": sum_log,
      "approx_combinations": approx_combinations,
  }


def _generate_instances_for_sizes(sizes: List[Tuple[int, int, int, int, int, str]]) -> List[TimetablingInstance]:
  gen = InstanceGenerator(seed=42)
  instances = []
  for courses, currs, rooms, teachers, periods, label in sizes:
    inst = gen.generate_random_instance(
        num_courses=courses,
        num_curriculums=currs,
        num_rooms=rooms,
        num_teachers=teachers,
        num_periods=periods,
        room_capacity_range=(120, 200),
        students_per_curriculum_range=(50, 100),
        availability_ratio=1.0,
        name=label
    )
    instances.append(inst)
  return instances


def analysis_bruteforce_section() -> pd.DataFrame:
  sizes = [
      (3, 2, 3, 3, 6, "Tiny"),
      (4, 2, 3, 3, 6, "Small-4"),
      (5, 3, 4, 4, 8, "Small-5"),
      (6, 3, 4, 4, 10, "Small-6"),
      (8, 4, 5, 5, 12, "Medium-8"),
      (10, 4, 5, 6, 12, "Medium-10"),
      (15, 5, 6, 8, 20, "Large-15"),
      (20, 8, 8, 10, 35, "Large-20"),
      (40, 15, 15, 15, 60, "Large-40"),
      (80, 30, 30, 30, 100, "Large-80"),
      (100, 50, 50, 50, 150, "Large-100"),
      (150, 75, 75, 75, 250, "Large-150"),
      (200, 100, 100, 100, 300, "Large-200"),
      (250, 125, 125, 125, 400, "Large-250"),
  ]
  instances = _generate_instances_for_sizes(sizes)
  rows = []
  for inst in instances:
    stats = _compute_candidates_stats(inst)
    ok, _, elapsed = solve_timetabling_bruteforce(inst, time_limit_sec=3.0)
    rows.append({
        "section": "BruteForce",
        "instance": inst.name,
        "num_sections": len(inst.course_sections),
        "num_rooms": len(inst.rooms),
        "num_teachers": len(inst.teachers),
        "num_periods": len(inst.periods),
        "total_vertices": stats["total_vertices"],
        "min_candidates": stats["min_candidates"],
        "max_candidates": stats["max_candidates"],
        "mean_candidates": stats["mean_candidates"],
        "median_candidates": stats["median_candidates"],
        "sum_log_candidates": stats["sum_log_candidates"],
        "approx_combinations": stats["approx_combinations"],
        "feasible": ok,
        "time_sec": elapsed,
    })
    print(f"{inst.name}: V={int(stats['total_vertices'])}, meanC={stats['mean_candidates']:.1f}, "
          f"comb≈e^{stats['sum_log_candidates']:.1f}, tiempo={elapsed:.3f}s, factible={'Sí' if ok else 'No'}")
  return pd.DataFrame(rows)


def analysis_heuristics_section() -> pd.DataFrame:
  sizes = [
      (150, 75, 75, 75, 250, "Large-150"),
      (200, 100, 100, 100, 300, "Large-200"),
      (250, 125, 125, 125, 400, "Large-250"),
      (300, 150, 150, 150, 400, "Large-300"),
      # (400, 200, 200, 200, 800, "Large-400-1"),
      # (400, 250, 250, 250, 800, "Large-400-2"),
  ]
  instances = _generate_instances_for_sizes(sizes)
  runner = ExperimentRunner(timeout=600)
  df = runner.run_experiment_suite(instances=instances, algorithms=["DSatur", "RLF"], repetitions=3)
  summary = df.groupby(["algorithm", "instance_name"]).agg(
      mean_objective=("objective_value", "mean"),
      std_objective=("objective_value", "std"),
      mean_time=("execution_time", "mean"),
  ).reset_index()
  for _, row in summary.iterrows():
    print(f"{row['instance_name']} [{row['algorithm']}]: score_media={row['mean_objective']:.2f}±{row['std_objective']:.2f}, "
          f"tiempo_medio={row['mean_time']:.3f}s")
  return df


def analysis_metaheuristics_section() -> pd.DataFrame:
  generator = InstanceGenerator(seed=42)
  print("generando instancias")
  instances = generator.generate_metaheuristic_instances()
  print("instancias generadas")
  runner = ExperimentRunner(timeout=600)
  results = []
  repetitions = 2
  for inst in instances:
    for rep in range(repetitions):
      # GRASP con 2 iteraciones
      res_grasp = runner.run_grasp(inst, alpha=0.3, max_iterations=2)
      results.append(res_grasp)
      # GA con 2 generaciones
      res_ga = runner.run_genetic_algorithm_custom(inst, population=40, generations=2, mutation=0.1, crossover=0.8, tour=3)
      results.append(res_ga)
  runner.results = results
  df = runner.get_results_dataframe()
  summary = df.groupby(["Algorithm", "Instance"]).agg(
      mean_score=("Score", "mean"),
      std_score=("Score", "std"),
      mean_time=("Time", "mean"),
      samples=("Algorithm", "count")
  ).reset_index()
  for _, row in summary.iterrows():
    print(f"{row['Instance']} [{row['Algorithm']}]: score_media={row['mean_score']:.2f}±{row['std_score']:.2f}, "
          f"tiempo_medio={row['mean_time']:.3f}s, muestras={int(row['samples'])}")
  # Visualizar
  runner.plot_results()
  return df


def run_three_section_analysis() -> None:
  # print("Sección 1: Fuerza bruta")
  # df_bf = analysis_bruteforce_section()
  # print("Sección 2: Heurísticas")
  # df_h = analysis_heuristics_section()
  print("Sección 3: Metaheurísticas")
  df_mh = analysis_metaheuristics_section()
  combined = pd.concat([df_mh], ignore_index=True)
  try:
    combined.to_csv("summary/analysis_results.csv", index=False)
    print("CSV guardado en summary/analysis_results.csv")
  except Exception:
    combined.to_csv("analysis_results.csv", index=False)
    print("CSV guardado en analysis_results.csv")


if __name__ == "__main__":
  run_three_section_analysis()
