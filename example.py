from src.data_structures.graph import GraphInstance
from src.algorithms.coloring import greedy_coloring, num_colors


if __name__ == "__main__":
  g = GraphInstance(vertices={1, 2, 3, 4}, edges={(1, 2), (2, 3), (1, 3)})
  colors, classes = greedy_coloring(g)
  print("Asignación de colores:", colors)
  print("Clases de color:", classes)
  print("Número de colores:", num_colors(classes))
