from typing import Set, List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class TimetablingInstance:
  """
  Representación de una instancia de Course Timetabling Problem

  Parámetros:
    q: Número de Cursos
    courses: Lista de índices de cursos (típicamente 1 a q)
    k: Diccionario que mapea curso i al número de clases k_i
    r: Número de grupos
    groups: Lista de grupos, donde cada grupo es un conjunto de cursos que comparten estudiantes
    p: Número de períodos de tiempo disponibles
    l: Diccionario que mapea período k al número de aulas disponibles l_k
    preassignment: Diccionario (curso, período) -> 1 si preasignado, de lo contrario 0
    availability: Diccionario (curso, período) -> 1 si disponible, de lo contrario 0
  """
  q: int
  courses: List[int] = field(default_factory=list)
  k: Dict[int, int] = field(default_factory=dict)
  r: int = 0
  groups: List[Set[int]] = field(default_factory=list)
  p: int = 0
  l: Dict[int, int] = field(default_factory=dict)
  preassignment: Dict[Tuple[int, int], int] = field(default_factory=dict)
  availability: Dict[Tuple[int, int], int] = field(default_factory=dict)
  conflict_matrix: Optional[Dict[Tuple[int, int], int]] = field(default_factory=dict)

  def __post_init__(self):
    "Inicializa la lista de cursos si no se proporciona."
    if not self.courses and self.q > 0:
      self.courses = list(range(1, self.q + 1))

    # Inicializa disponibilidad y preasignación por defecto si no se proporcionan
    if not self.availability and self.q > 0 and self.p > 0:
      for i in self.courses:
        for k in range(1, self.p + 1):
          self.availability[(i, k)] = 1

    if not self.preassignment and self.q > 0 and self.p > 0:
      for i in self.courses:
        for k in range(1, self.p + 1):
          self.preassignment[(i, k)] = 0

  def set_classroom_capacity(self, period: int, capacity: int) -> None:
    "Establece el número de aulas disponibles para un período."
    self.l[period] = capacity

  def set_course_classes(self, course: int, num_classes: int) -> None:
    "Establece el número de clases para un curso."
    self.k[course] = num_classes

  def set_preassignment(self, course: int, period: int, assigned: bool) -> None:
    "Establece o elimina una preasignación para un curso en un período."
    self.preassignment[(course, period)] = 1 if assigned else 0

  def set_availability(self, course: int, period: int, available: bool) -> None:
    "Establece o elimina la disponibilidad de un curso para un período."
    self.availability[(course, period)] = 1 if available else 0

  def set_conflict(self, course1: int, course2: int, conflict: bool) -> None:
    "Establece o elimina un conflicto entre dos cursos."
    key = (min(course1, course2), max(course1, course2))
    if self.conflict_matrix is None:
      self.conflict_matrix = {}
    self.conflict_matrix[key] = 1 if conflict else 0

  def add_group(self, courses_in_group: Set[int]) -> None:
    "Agrega un grupo de cursos que comparten estudiantes."
    self.groups.append(courses_in_group)
    self.r = len(self.groups)

  def get_conflicting_courses(self, course: int) -> Set[int]:
    "Obtiene el conjunto de cursos que tienen conflicto con el curso dado."
    if not self.conflict_matrix:
      # Construir la matriz de conflictos a partir de los grupos si no está definida
      self.conflict_matrix = {}
      for group in self.groups:
        for c1 in group:
          for c2 in group:
            if c1 < c2:
              self.conflict_matrix[(c1, c2)] = 1

    conflicts = set()
    for c in self.courses:
      if c != course:
        key = (min(course, c), max(course, c))
        if self.conflict_matrix.get(key, 0) == 1:
          conflicts.add(c)
    return conflicts

  def get_total_classes(self) -> int:
    "Obtiene el número total de clases en todos los cursos."
    return sum(self.k.get(course, 0) for course in self.courses)

  def get_total_classroom_slots(self) -> int:
    "Obtiene el número total de espacios de aula disponibles en todos los períodos."
    return sum(self.l.get(period, 0) for period in range(1, self.p + 1))

  def is_feasible(self) -> bool:
    "Verifica si la instancia es factible (total de clases menor-igual total de espacios de aula)."
    total_classes = self.get_total_classes()
    total_slots = self.get_total_classroom_slots()
    return total_classes <= total_slots
