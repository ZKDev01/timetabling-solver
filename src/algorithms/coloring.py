from typing import Dict, List, Optional, Tuple, Set
import random
from ..data_structures.graph import GraphInstance


def greedy_coloring(
    graph: GraphInstance,
    order: Optional[List[int]] = None,
    randomize: bool = False
) -> Tuple[Dict[int, int], List[Set[int]]]:
  """
  Colorea el grafo usando un algoritmo Greedy.

  Parámetros:
    graph: instancia de `GraphInstance`
    order: lista opcional con el orden en que colorear vértices. Si es None:
      - si randomize=True se usa una permutación aleatoria de los vértices
      - en otro caso se usa el orden ascendente de identificadores
    randomize: si es True y order es None, usa orden aleatorio

  Devuelve:
    (colors, color_classes)
    - colors: dict {vertice: color} donde los colores son enteros 1..k
    - color_classes: lista de sets, indexada desde 0, donde cada set contiene
    los vértices coloreados con ese color (color i corresponde a index i-1)
  """
  vertices = list(graph.vertices)
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
    used: Set[int] = set()
    for u in graph.get_neighbors(v):
      if u in colors:
        used.add(colors[u])

    # buscar el primer color disponible (1,2,...)
    color = 1
    while color in used:
      color += 1

    colors[v] = color

    # asegurar que color_classes tenga suficiente longitud
    while len(color_classes) < color:
      color_classes.append(set())
    color_classes[color - 1].add(v)

  return colors, color_classes


def num_colors(color_classes: List[Set[int]]) -> int:
  "Devuelve el número de colores usados (longitud de color_classes)."
  return len([c for c in color_classes if c])
