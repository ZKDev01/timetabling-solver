from typing import Dict, List, Optional, Tuple, Set
import random
from ..data_structures.graph import GraphInstance


def greedy_coloring(
    graph: GraphInstance,
    order: Optional[List[int]] = None,
    randomize: bool = False,
    max_colors: Optional[int] = None
) -> Tuple[Dict[int, int], List[Set[int]]]:
  """
  Colorea el grafo usando un algoritmo Greedy.

  Parámetros:
    graph: instancia de `GraphInstance`
    order: lista opcional con el orden en que colorear vértices. Si es None:
      - si randomize=True se usa una permutación aleatoria de los vértices
      - en otro caso se usa el orden ascendente de identificadores
    randomize: si es True y order es None, usa orden aleatorio
    max_colors: número máximo de colores a usar. Si None, usa tantos como sea necesario.

  Returns:
    - colors: dict {vertice: color} donde los colores son enteros 1..k
    - color_classes: lista de sets, indexada desde 0, donde cada set contiene
      los vértices coloreados con ese color (color i corresponde a index i-1)
  """
  vertices = list[int](graph.vertices)
  if order is None:
    if randomize:
      random.shuffle(vertices)
      order = vertices
    else:
      order = sorted(vertices)

  colors: Dict[int, int] = {}
  color_classes: List[Set[int]] = []

  for v in order:
    # colores usados por vecinos ya coloreados
    used: Set[int] = set[int]()
    for u in graph.get_neighbors(v):
      if u in colors:
        used.add(colors[u])

    # buscar el primer color disponible (1,2,...)
    color = 1
    while color in used or (max_colors is not None and color > max_colors):
      color += 1
    if max_colors is not None and color > max_colors:
      # No color available, skip or assign a new one? For now, assign anyway
      pass  # will assign color > max_colors

    colors[v] = color

    # asegurar que color_classes tenga suficiente longitud
    while len(color_classes) < color:
      color_classes.append(set())
    color_classes[color - 1].add(v)

  return colors, color_classes


def dsatur_coloring(graph: GraphInstance) -> Dict[int, int]:
  """Implementa el algoritmo DSatur (Degree Saturation) para coloración de grafos

  Args:
      graph (GraphInstance): Instancia del grafo

  Returns:
      Dict[int, int]: Diccionario con la asignación de colores a vértices
  """
  # 1. Inicialización
  X: Set[int] = graph.vertices.copy()   # Vértices no coloreados
  vertex_color: Dict[int, int] = {}     # Colores asignados
  S: List[Set[int]] = []                # Clases de color

  # Función para calcular saturación de un vértice
  def saturation(vertex: int) -> int:
    "Calcula el grado de saturación de un vértice"
    if vertex not in X:
      return -1  # Ya coloreado

    neighbor_colors = set()
    for neighbor in graph.get_neighbors(vertex):
      if neighbor in vertex_color:
        neighbor_colors.add(vertex_color[neighbor])
    return len(neighbor_colors)

  # 2. Bucle principal
  while X:
    # Elegir vértice con máxima saturación
    max_sat = -1
    candidates = []

    for vertex in X:
      sat = saturation(vertex)
      if sat > max_sat:
        max_sat = sat
        candidates = [vertex]
      elif sat == max_sat:
        candidates.append(vertex)

    # En caso de empate, elegir el de mayor grado
    if len(candidates) > 1:
      max_degree = -1
      degree_candidates = []
      for vertex in candidates:
        degree = graph.get_degree(vertex)
        if degree > max_degree:
          max_degree = degree
          degree_candidates = [vertex]
        elif degree == max_degree:
          degree_candidates.append(vertex)
      candidates = degree_candidates

    # Si sigue habiendo empate, elegir aleatoriamente
    v = random.choice(candidates) if len(candidates) > 1 else candidates[0]

    # Buscar el menor color disponible para v
    neighbor_colors = set()
    for neighbor in graph.get_neighbors(v):
      if neighbor in vertex_color:
        neighbor_colors.add(vertex_color[neighbor])

    # Probar colores desde 1 en adelante
    color = 1
    while color in neighbor_colors:
      color += 1

    # Actualizar estructuras de datos
    vertex_color[v] = color

    # Agregar a clase de color correspondiente
    color_idx = color - 1
    if color_idx >= len(S):
      S.append({v})
    else:
      S[color_idx].add(v)

    X.remove(v)

  return vertex_color


def rlf_coloring(graph: GraphInstance) -> Dict[int, int]:
  """Implementa el algoritmo RLF (Recursive Largest First) para coloración de grafos

  Args:
      graph (GraphInstance): Instancia del grafo

  Returns:
      Dict[int, int]: Diccionario con la asignación de colores a vértices
  """
  # 1. Inicialización
  X: Set[int] = graph.vertices.copy()  # Vértices que pueden ser coloreados con el color actual
  Y: Set[int] = set()                  # Vértices que NO pueden ser coloreados con el color actual
  S: List[Set[int]] = []               # Clases de color
  vertex_color: Dict[int, int] = {}    # Colores asignados

  # 2. Bucle principal
  color = 1
  while X:
    # Crear nueva clase de color
    color_class: Set[int] = set()

    # Bucle para construir la clase de color actual
    while X:
      # Función para seleccionar vértice en X con mayor grado en el subgrafo inducido por X
      def select_vertex():
        max_degree = -1
        candidates = []

        for vertex in X:
          # Calcular grado solo con respecto a X
          degree_in_X = len(graph.get_neighbors(vertex) & X)
          if degree_in_X > max_degree:
            max_degree = degree_in_X
            candidates = [vertex]
          elif degree_in_X == max_degree:
            candidates.append(vertex)

        # Romper empates aleatoriamente
        return random.choice(candidates) if candidates else None

      # Seleccionar vértice
      v = select_vertex()
      if v is None:
        break

      # Agregar vértice a la clase de color actual
      color_class.add(v)
      vertex_color[v] = color

      # Mover vecinos de v en X a Y
      neighbors_in_X = graph.get_neighbors(v) & X
      Y.update(neighbors_in_X)

      # Remover v y sus vecinos de X
      X.remove(v)
      X.difference_update(neighbors_in_X)

    # Agregar la clase de color completa
    S.append(color_class)

    # Preparar para siguiente iteración
    X = Y.copy()
    Y.clear()
    color += 1

  return vertex_color
