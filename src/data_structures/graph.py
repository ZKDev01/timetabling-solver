from typing import Never, Any, Set, List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class GraphInstance:
  """Representación de instancia de un grafo G = (V, E) usado para el Problema de Coloración de Grafos

  Atributos:
    vertices: Conjunto de identificadores de vértices
    edges: Conjunto de aristas representadas como tuplas (u, v) donde u < v
    adj_list: Diccionario que mapea cada vértice a su conjunto de vértices adyacentes
    labels: Diccionario que mapea cada vértice a su etiqueta (información adicional)
    node_types: Diccionario que mapea cada vértice a su tipo ('Period', 'Teacher', 'Room', 'Course', 'Curriculum')
  """
  vertices: Set[int]
  edges: Set[Tuple[int, int]] = field(default_factory=set)
  adj_list: Dict[int, Set[int]] = field(default_factory=dict)
  labels: Dict[int, Any] = field(default_factory=dict)
  node_types: Dict[int, str] = field(default_factory=dict)

  def __post_init__(self) -> Never:
    "Inicializa la lista de adyacencia si se proporcionan vértices sin aristas."
    if not self.adj_list and self.vertices:
      self.adj_list = {v: set() for v in self.vertices}

    for u, v in self.edges:
      if u not in self.adj_list:
        self.adj_list[u] = set()
      if v not in self.adj_list:
        self.adj_list[v] = set()

      self.adj_list[u].add(v)
      self.adj_list[v].add(u)

  def add_vertex(self, vertex: int) -> None:
    "Agrega un vértice al grafo"
    if vertex not in self.vertices:
      self.vertices.add(vertex)
      self.adj_list[vertex] = set()
    else:
      raise Exception(f"El vértice ({vertex}) ya existe en el grafo.")

  def add_edge(self, u: int, v: int) -> None:
    "Agrega una arista entre los vértices u y v"
    if u not in self.vertices:
      self.add_vertex(u)
    if v not in self.vertices:
      self.add_vertex(v)

    # almacena la arista con u < v para consistencia
    edge: Tuple[int, int] = (min(u, v), max(u, v))
    if edge not in self.edges:
      self.edges.add(edge)
      self.adj_list[u].add(v)
      self.adj_list[v].add(u)
    else:
      raise Exception(f"La arista ({edge}) ya existe en el grafo.")

  def remove_vertex(self, vertex: int) -> None:
    "Elimina un vértice y todas las aristas incidentes"
    if vertex not in self.vertices:
      return
    for neighbor in self.adj_list.get(vertex, set()).copy():
      if neighbor in self.adj_list:
        self.adj_list[neighbor].discard(vertex)
    if vertex in self.adj_list:
      del self.adj_list[vertex]
    self.edges = {e for e in self.edges if e[0] != vertex and e[1] != vertex}
    self.vertices.discard(vertex)

  def get_degree(self, vertex: int) -> int:
    "Obtiene el grado (número de vértices adyacentes) de un vértice"
    if vertex not in self.vertices:
      raise Exception(f"El vértice ({vertex}) no existe en el grafo")
    return len(self.adj_list.get(vertex, set()))

  def get_neighbors(self, vertex: int) -> Set[int]:
    "Obtiene el conjunto de vecinos de un vértice"
    if vertex not in self.vertices:
      raise Exception(f"El vértice ({vertex}) no existe en el grafo")
    return self.adj_list.get(vertex, set()).copy()

  def get_max_degree(self) -> int:
    "Obtiene el grado máximo entre todos los vértices del grado"
    return max((self.get_degree(v) for v in self.vertices), default=0)

  def get_num_vertices(self) -> int:
    "Obtiene el número de vértices en el grafo"
    return len(self.vertices)

  def get_num_edges(self) -> int:
    "Obtiene el numero de aristas en el grafo"
    return len(self.edges)
