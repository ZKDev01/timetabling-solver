from typing import Any, Set, List, Dict, Tuple, Optional
from dataclasses import dataclass, field


# region: Data Structures
@dataclass
class TimetablingInstance:
  """Representación de una instancia de Course Timetabling Problem

  Parámetros:
    n_courses: número de cursos
    courses: lista de índices de cursos (típicamente 1 a q)
    classes_per_course: diccionario que mapea curso i al número de clases k_i
    n_groups: número de grupos
    groups: lista de grupos, donde cada grupo es un conjunto de cursos que comparten estudiantes
    n_timeslot: número de períodos de tiempo disponibles
    classroom_capacity: diccionario que mapea período k al número de aulas disponibles l_k
    preassignment: diccionario (curso, período) -> 1 si preasignado, de lo contrario 0
    availability: diccionario (curso, período) -> 1 si disponible, de lo contrario 0
  """
  n_courses: int
  courses: List[int] = field(default_factory=list)
  classes_per_course: Dict[int, int] = field(default_factory=dict)
  n_groups: int = 0
  groups: List[Set[int]] = field(default_factory=list)
  n_timeslot: int = 0
  classroom_capacity: Dict[int, int] = field(default_factory=dict)
  preassignment: Dict[Tuple[int, int], int] = field(default_factory=dict)
  availability: Dict[Tuple[int, int], int] = field(default_factory=dict)
  conflict_matrix: Optional[Dict[Tuple[int, int], int]] = field(default_factory=dict)

  def __post_init__(self):
    "Inicializa la lista de cursos si no se proporciona."
    if not self.courses and self.n_courses > 0:
      self.courses = list(range(1, self.n_courses + 1))

    # Inicializa disponibilidad y preasignación por defecto si no se proporcionan
    if not self.availability and self.n_courses > 0 and self.n_timeslot > 0:
      for i in self.courses:
        for k in range(1, self.n_timeslot + 1):
          self.availability[(i, k)] = 1

    if not self.preassignment and self.n_courses > 0 and self.n_timeslot > 0:
      for i in self.courses:
        for k in range(1, self.n_timeslot + 1):
          self.preassignment[(i, k)] = 0

  def set_classroom_capacity(self, period: int, capacity: int) -> None:
    "Establece el número de aulas disponibles para un período."
    self.classroom_capacity[period] = capacity

  def set_course_classes(self, course: int, num_classes: int) -> None:
    "Establece el número de clases para un curso."
    self.classes_per_course[course] = num_classes

  def set_preassignment(self, course: int, period: int, assigned: bool) -> None:
    "Establece o elimina una preasignación para un curso en un período."
    is_available = self.availability.get((course, period), 0) == 1
    self.preassignment[(course, period)] = 1 if (assigned and is_available) else 0

  def set_availability(self, course: int, period: int, available: bool) -> None:
    "Establece o elimina la disponibilidad de un curso para un período."
    self.availability[(course, period)] = 1 if available else 0
    if not available:
      self.preassignment[(course, period)] = 0

  def set_conflict(self, course1: int, course2: int, conflict: bool) -> None:
    "Establece o elimina un conflicto entre dos cursos."
    key = (min(course1, course2), max(course1, course2))
    if self.conflict_matrix is None:
      self.conflict_matrix = {}
    self.conflict_matrix[key] = 1 if conflict else 0

  def add_group(self, courses_in_group: Set[int]) -> None:
    "Agrega un grupo de cursos que comparten estudiantes."
    self.groups.append(courses_in_group)
    self.n_groups = len(self.groups)

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
    return sum(self.classes_per_course.get(course, 0) for course in self.courses)

  def get_total_classroom_slots(self) -> int:
    "Obtiene el número total de espacios de aula disponibles en todos los períodos."
    return sum(self.classroom_capacity.get(period, 0) for period in range(1, self.n_timeslot + 1))

  def is_feasible(self) -> bool:
    "Verifica factibilidad con restricciones de disponibilidad, preasignación y capacidad."
    total_classes = self.get_total_classes()
    total_slots = self.get_total_classroom_slots()
    if total_classes > total_slots:
      return False
    for course in self.courses:
      available_periods = sum(
          1 for k in range(1, self.n_timeslot + 1)
          if self.availability.get((course, k), 0) == 1
      )
      if available_periods < self.classes_per_course.get(course, 0):
        return False
    for (course, period), assigned in self.preassignment.items():
      if assigned == 1 and self.availability.get((course, period), 0) != 1:
        return False
    return True

  def to_graph_instance(self) -> 'GraphInstance':
    vertices: Set[int] = set()
    edges: Set[Tuple[int, int]] = set()
    labels: Dict[int, Tuple[int, int]] = {}
    course_classes: Dict[int, List[int]] = {}
    next_id = 1
    for course in self.courses:
      num = self.classes_per_course.get(course, 0)
      if num > 0:
        class_vertices: List[int] = []
        for idx in range(1, num + 1):
          v_id = next_id
          next_id += 1
          vertices.add(v_id)
          labels[v_id] = (course, idx)
          class_vertices.append(v_id)
        course_classes[course] = class_vertices
        for i in range(len(class_vertices)):
          for j in range(i + 1, len(class_vertices)):
            u = class_vertices[i]
            w = class_vertices[j]
            edges.add((min(u, w), max(u, w)))
    for course in course_classes.keys():
      conflicts = self.get_conflicting_courses(course)
      for other in conflicts:
        if other in course_classes:
          for u in course_classes[course]:
            for w in course_classes[other]:
              edges.add((min(u, w), max(u, w)))
    graph = GraphInstance(vertices=vertices, edges=edges)
    graph.labels = labels
    return graph


@dataclass
class GraphInstance:
  """Representación de instancia de un grafo G = (V, E) usado para el Problema de Coloración de Grafos

  Atributos:
    vertices: Conjunto de identificadores de vértices (típicamente enteros o cadenas)
    edges: Conjunto de aristas representadas como tuplas (u, v) donde u < v
    adjacency_list: Diccionario que mapea cada vértice a su conjunto de vértices adyacentes
  """
  vertices: Set[int]
  edges: Set[Tuple[int, int]] = field(default_factory=set)
  adjacency_list: Dict[int, Set[int]] = field(default_factory=dict)
  labels: Dict[int, Tuple[int, int]] = field(default_factory=dict)

  def __post_init__(self):
    "Inicializa la lista de adyacencia si se proporcionan vértices sin aristas."
    if not self.adjacency_list and self.vertices:
      self.adjacency_list = {v: set() for v in self.vertices}

    for u, v in self.edges:
      if u not in self.adjacency_list:
        self.adjacency_list[u] = set()
      if v not in self.adjacency_list:
        self.adjacency_list[v] = set()

      self.adjacency_list[u].add(v)
      self.adjacency_list[v].add(u)

  def add_vertex(self, vertex: int) -> None:
    "Agrega un vértice al grafo."
    if vertex not in self.vertices:
      self.vertices.add(vertex)
      self.adjacency_list[vertex] = set()

  def add_edge(self, u: int, v: int) -> None:
    "Agrega una arista entre los vértices u y v."
    if u not in self.vertices:
      self.add_vertex(u)
    if v not in self.vertices:
      self.add_vertex(v)

    # Almacena la arista con u < v para consistencia
    edge = (min(u, v), max(u, v))
    self.edges.add(edge)
    self.adjacency_list[u].add(v)
    self.adjacency_list[v].add(u)

  def remove_vertex(self, vertex: int) -> None:
    "Elimina un vértice y todas las aristas incidentes."
    if vertex not in self.vertices:
      return
    for neighbor in self.adjacency_list.get(vertex, set()).copy():
      if neighbor in self.adjacency_list:
        self.adjacency_list[neighbor].discard(vertex)
    if vertex in self.adjacency_list:
      del self.adjacency_list[vertex]
    self.edges = {e for e in self.edges if e[0] != vertex and e[1] != vertex}
    self.vertices.discard(vertex)

  def get_degree(self, vertex: int) -> int:
    "Obtiene el grado (número de vértices adyacentes) de un vértice."
    return len(self.adjacency_list.get(vertex, set()))

  def get_neighbors(self, vertex: int) -> Set[int]:
    "Obtiene el conjunto de vecinos de un vértice."
    return self.adjacency_list.get(vertex, set()).copy()

  def get_max_degree(self) -> int:
    "Obtiene el grado máximo entre todos los vértices del grafo."
    return max((self.get_degree(v) for v in self.vertices), default=0)

  def get_num_vertices(self) -> int:
    "Obtiene el número de vértices en el grafo."
    return len(self.vertices)

  def get_num_edges(self) -> int:
    "Obtiene el número de aristas en el grafo."
    return len(self.edges)
# endregion

# region: TimetablingInstance Test


def test_timetabling_init():
  "Caso 1: Inicialización básica"
  instance = TimetablingInstance(n_courses=5, n_timeslot=10)

  assert instance.n_courses == 5
  assert instance.n_timeslot == 10
  assert instance.courses == [1, 2, 3, 4, 5]
  assert instance.n_groups == 0
  assert len(instance.groups) == 0

  # verificar inicialización por defecto de availability y preassignment
  for i in range(1, 6):
    for k in range(1, 11):
      assert instance.availability[(i, k)] == 1
      assert instance.preassignment[(i, k)] == 0


def test_timetabling_setters():
  "Caso 2: Uso de métodos setter"
  instance = TimetablingInstance(n_courses=3, n_timeslot=5)

  # Configurar aulas por período
  instance.set_classroom_capacity(1, 3)
  instance.set_classroom_capacity(2, 4)
  instance.set_classroom_capacity(3, 2)

  assert instance.classroom_capacity[1] == 3
  assert instance.classroom_capacity[2] == 4
  assert instance.classroom_capacity[3] == 2
  assert instance.classroom_capacity.get(4) is None  # No configurado

  # Configurar número de clases por curso
  instance.set_course_classes(1, 2)
  instance.set_course_classes(2, 3)
  instance.set_course_classes(3, 1)

  assert instance.classes_per_course[1] == 2
  assert instance.classes_per_course[2] == 3
  assert instance.classes_per_course[3] == 1

  # Configurar disponibilidad
  instance.set_availability(1, 2, False)
  assert instance.availability[(1, 2)] == 0
  instance.set_availability(1, 2, True)
  assert instance.availability[(1, 2)] == 1

  # Configurar preasignación
  instance.set_preassignment(2, 3, True)
  assert instance.preassignment[(2, 3)] == 1
  instance.set_preassignment(2, 3, False)
  assert instance.preassignment[(2, 3)] == 0


def test_timetabling_groups_and_conflicts():
  "Caso 3: Grupos y conflictos"
  instance = TimetablingInstance(n_courses=4, n_timeslot=6)

  # Agregar grupos
  instance.add_group({1, 2, 3})
  instance.add_group({2, 4})

  assert instance.n_groups == 2
  assert instance.groups == [{1, 2, 3}, {2, 4}]

  # Verificar conflictos generados automáticamente
  conflicts_1 = instance.get_conflicting_courses(1)
  assert 2 in conflicts_1
  assert 3 in conflicts_1
  assert 4 not in conflicts_1

  conflicts_2 = instance.get_conflicting_courses(2)
  assert 1 in conflicts_2
  assert 3 in conflicts_2
  assert 4 in conflicts_2

  # Configurar conflicto manual
  instance.set_conflict(1, 4, True)
  conflicts_1 = instance.get_conflicting_courses(1)
  assert 4 in conflicts_1  # Ahora debería estar en conflicto


def test_timetabling_totals_and_feasibility():
  "Caso 4: Totales y factibilidad"
  instance = TimetablingInstance(n_courses=3, n_timeslot=4)

  # Configurar aulas
  for period in range(1, 5):
    instance.set_classroom_capacity(period, 2)

  # Configurar clases por curso
  instance.set_course_classes(1, 3)
  instance.set_course_classes(2, 2)
  instance.set_course_classes(3, 1)

  # Verificar totales
  total_classes = instance.get_total_classes()
  assert total_classes == 6  # 3 + 2 + 1

  total_slots = instance.get_total_classroom_slots()
  assert total_slots == 8  # 4 períodos * 2 aulas

  # Verificar factibilidad
  assert instance.is_feasible() == True  # 6 <= 8

  # Hacerlo no factible
  instance.set_course_classes(1, 5)  # Ahora total = 5 + 2 + 1 = 8
  # Todavía factible (8 <= 8)
  instance.set_course_classes(2, 3)  # Ahora total = 5 + 3 + 1 = 9
  assert instance.is_feasible() == False  # 9 > 8


def test_timetabling_edge_cases():
  "Caso 5: Casos límite"
  # Instancia vacía
  instance = TimetablingInstance(n_courses=0, n_timeslot=0)
  assert instance.courses == []
  assert instance.get_total_classes() == 0
  assert instance.get_total_classroom_slots() == 0
  assert instance.is_feasible() == True  # 0 <= 0

  # Un solo curso, un solo período
  instance = TimetablingInstance(n_courses=1, n_timeslot=1)
  instance.set_course_classes(1, 1)
  instance.set_classroom_capacity(1, 1)
  assert instance.is_feasible() == True

  instance.set_classroom_capacity(1, 0)
  assert instance.is_feasible() == False

  # Curso sin disponibilidad en ningún período
  instance = TimetablingInstance(n_courses=2, n_timeslot=3)
  for period in range(1, 4):
    instance.set_availability(1, period, False)

  # Verificar que todos los períodos están en 0
  for period in range(1, 4):
    assert instance.availability[(1, period)] == 0

  # Disponibilidad insuficiente para k_i
  instance = TimetablingInstance(n_courses=1, n_timeslot=3)
  instance.set_classroom_capacity(1, 1)
  instance.set_classroom_capacity(2, 1)
  instance.set_course_classes(1, 2)
  instance.set_availability(1, 1, True)
  instance.set_availability(1, 2, False)
  instance.set_availability(1, 3, False)
  assert instance.is_feasible() == False
  instance.set_availability(1, 2, True)
  assert instance.is_feasible() == True


def test_timetabling_custom_initialization():
  """Caso 6: Inicialización con parámetros personalizados"""
  courses = [101, 102, 103]
  availability = {(101, 1): 1, (101, 2): 0, (102, 1): 1, (102, 2): 1}
  preassignment = {(101, 1): 1, (103, 2): 1}

  instance = TimetablingInstance(
      n_courses=3,
      courses=courses,
      n_timeslot=2,
      availability=availability,
      preassignment=preassignment
  )

  assert instance.courses == [101, 102, 103]
  assert instance.availability[(101, 1)] == 1
  assert instance.availability[(101, 2)] == 0
  assert instance.preassignment[(101, 1)] == 1
  assert instance.preassignment[(103, 2)] == 1
  # Valores no especificados deberían ser 0 en preassignment
  assert instance.preassignment.get((102, 1), 0) == 0


def test_timetabling_preassignment_consistency():
  "Caso 7: Consistencia de preasignaciones"
  instance = TimetablingInstance(n_courses=3, n_timeslot=5)

  # Preasignar un curso
  instance.set_preassignment(1, 3, True)

  # Verificar que otras combinaciones no están preasignadas
  assert instance.preassignment[(1, 1)] == 0
  assert instance.preassignment[(1, 2)] == 0
  assert instance.preassignment[(1, 4)] == 0
  assert instance.preassignment[(2, 3)] == 0

  # Preasignación no debería afectar disponibilidad
  instance.set_availability(1, 3, False)
  assert instance.availability[(1, 3)] == 0
  assert instance.preassignment[(1, 3)] == 0


def test_timetabling_to_graph_conversion():
  "Caso 8: Conversión a grafo de coloración"
  instance = TimetablingInstance(n_courses=3, n_timeslot=5)
  instance.set_course_classes(1, 2)
  instance.set_course_classes(2, 1)
  instance.set_course_classes(3, 1)
  instance.add_group({1, 2})
  graph = instance.to_graph_instance()
  assert graph.get_num_vertices() == 4
  c1_vertices = [vid for vid, label in graph.labels.items() if label[0] == 1]
  c2_vertices = [vid for vid, label in graph.labels.items() if label[0] == 2]
  c3_vertices = [vid for vid, label in graph.labels.items() if label[0] == 3]
  assert len(c1_vertices) == 2
  assert len(c2_vertices) == 1
  assert len(c3_vertices) == 1
  u, w = sorted(c1_vertices)
  assert (u, w) in graph.edges
  v2 = c2_vertices[0]
  assert (min(u, v2), max(u, v2)) in graph.edges
  assert (min(w, v2), max(w, v2)) in graph.edges
  v3 = c3_vertices[0]
  assert (min(u, v3), max(u, v3)) not in graph.edges
  assert (min(w, v3), max(w, v3)) not in graph.edges

# endregion

# region: GraphInstance Test


def test_graph_initialization():
  "Caso 1: Inicialización básica"
  vertices = {1, 2, 3, 4}
  edges = {(1, 2), (2, 3), (3, 4), (1, 4)}

  graph = GraphInstance(vertices=vertices, edges=edges)

  assert graph.vertices == {1, 2, 3, 4}
  assert graph.edges == {(1, 2), (2, 3), (3, 4), (1, 4)}

  # Verificar lista de adyacencia
  assert graph.adjacency_list[1] == {2, 4}
  assert graph.adjacency_list[2] == {1, 3}
  assert graph.adjacency_list[3] == {2, 4}
  assert graph.adjacency_list[4] == {1, 3}


def test_graph_add_vertex():
  "Caso 2: Agregar vértices"
  graph = GraphInstance(vertices={1, 2}, edges={(1, 2)})

  # Agregar vértice nuevo
  graph.add_vertex(3)
  assert 3 in graph.vertices
  assert graph.adjacency_list[3] == set()
  assert graph.get_degree(3) == 0

  # Agregar vértice existente (no debería cambiar nada)
  original_vertices = graph.vertices.copy()
  graph.add_vertex(1)
  assert graph.vertices == original_vertices


def test_graph_add_edge():
  "Caso 3: Agregar aristas"
  graph = GraphInstance(vertices={1, 2, 3}, edges=set())

  # Agregar arista entre vértices existentes
  graph.add_edge(1, 2)
  assert (1, 2) in graph.edges
  assert 2 in graph.adjacency_list[1]
  assert 1 in graph.adjacency_list[2]

  # Agregar arista que crea nuevo vértice
  graph.add_edge(3, 4)  # 4 no existe
  assert 4 in graph.vertices
  assert (3, 4) in graph.edges
  assert graph.get_num_vertices() == 4

  # Agregar arista duplicada (no debería crear duplicados)
  graph.add_edge(1, 2)
  assert len(graph.edges) == 2  # (1,2) y (3,4)
  assert len(graph.adjacency_list[1]) == 1  # Solo el 2


def test_graph_degree_and_neighbors():
  "Caso 4: Grado y vecinos"
  vertices = {1, 2, 3, 4, 5}
  edges = {(1, 2), (1, 3), (1, 4), (2, 3), (4, 5)}

  graph = GraphInstance(vertices=vertices, edges=edges)

  # Verificar grados
  assert graph.get_degree(1) == 3
  assert graph.get_degree(2) == 2
  assert graph.get_degree(3) == 2
  assert graph.get_degree(4) == 2
  assert graph.get_degree(5) == 1

  # Verificar vecinos
  assert graph.get_neighbors(1) == {2, 3, 4}
  assert graph.get_neighbors(5) == {4}
  assert graph.get_neighbors(3) == {1, 2}

  # Grado máximo
  assert graph.get_max_degree() == 3


def test_graph_empty_and_single_vertex():
  "Caso 5: Grafos vacíos y con un solo vértice"
  # Grafo vacío
  graph = GraphInstance(vertices=set(), edges=set())
  assert graph.get_num_vertices() == 0
  assert graph.get_num_edges() == 0
  assert graph.get_max_degree() == 0

  # Grafo con un solo vértice
  graph = GraphInstance(vertices={1}, edges=set())
  assert graph.get_num_vertices() == 1
  assert graph.get_num_edges() == 0
  assert graph.get_degree(1) == 0
  assert graph.get_neighbors(1) == set()


def test_graph_complete_graph():
  "Caso 6: Grafo completo"
  vertices = {1, 2, 3, 4}
  edges = set()
  for i in range(1, 5):
    for j in range(i + 1, 5):
      edges.add((i, j))

  graph = GraphInstance(vertices=vertices, edges=edges)

  # En un grafo completo de 4 vértices, cada vértice tiene grado 3
  for v in vertices:
    assert graph.get_degree(v) == 3

  assert graph.get_num_edges() == 6  # 4C2 = 6
  assert graph.get_max_degree() == 3


def test_graph_edge_ordering():
  "Caso 7: Orden de aristas"
  # Las aristas deben almacenarse con u < v
  graph = GraphInstance(vertices={1, 2, 3}, edges=set())

  # Agregar arista en orden inverso
  graph.add_edge(3, 1)
  assert (1, 3) in graph.edges  # Debería almacenarse como (1, 3)
  assert (3, 1) not in graph.edges

  # Agregar arista en orden normal
  graph.add_edge(2, 3)
  assert (2, 3) in graph.edges

  # Verificar que la lista de adyacencia es correcta
  assert graph.adjacency_list[1] == {3}
  assert graph.adjacency_list[3] == {1, 2}


def test_graph_operations_consistency():
  "Caso 9: Consistencia de operaciones"
  graph = GraphInstance(vertices={1, 2}, edges={(1, 2)})

  graph.remove_vertex(1)
  assert 1 not in graph.vertices
  assert 1 not in graph.adjacency_list
  assert graph.get_num_edges() == 0
  assert 1 not in graph.adjacency_list.get(2, set())
# endregion


def main() -> None:
  test_timetabling_init()
  test_timetabling_setters()
  test_timetabling_groups_and_conflicts()
  test_timetabling_totals_and_feasibility()
  test_timetabling_edge_cases()
  test_timetabling_custom_initialization()
  test_timetabling_preassignment_consistency()
  test_timetabling_to_graph_conversion()
  test_graph_initialization()
  test_graph_add_vertex()
  test_graph_add_edge()
  test_graph_degree_and_neighbors()
  test_graph_empty_and_single_vertex()
  test_graph_complete_graph()
  test_graph_edge_ordering()
  test_graph_operations_consistency()
  print("All Test OK!")


if __name__ == "__main__":
  main()
