from typing import Set, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class GraphInstance:
  """
  Representación de instancia de un grafo G = (V, E) usado para el Problema de Coloración de Grafos

  Atributos:
    vertices: Conjunto de identificadores de vértices (típicamente enteros o cadenas)
    edges: Conjunto de aristas representadas como tuplas (u, v) donde u < v
    adjacency_list: Diccionario que mapea cada vértice a su conjunto de vértices adyacentes
  """
  vertices: Set[int]
  edges: Set[Tuple[int, int]] = field(default_factory=set)
  adjacency_list: Dict[int, Set[int]] = field(default_factory=dict)

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
