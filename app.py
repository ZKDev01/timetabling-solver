import streamlit as st
from typing import Dict, List, Set, Tuple

from src.data_structures.timetabling import TimetablingInstance
from src.algorithms.timetabling_solver import solve_timetabling, TimetablingResult


def parse_groups(text: str, q: int) -> List[Set[int]]:
  "Parsea grupos desde texto. Cada línea representa un grupo."
  groups: List[Set[int]] = []
  for raw in text.splitlines():
    raw = raw.strip()
    if not raw:
      continue
    # reemplazar comas por espacios y dividir
    tokens = raw.replace(",", " ").split()
    try:
      group = set()
      for tok in tokens:
        c = int(tok)
        if 1 <= c <= q:
          group.add(c)
      if group:
        groups.append(group)
    except ValueError:
      # ignorar líneas mal formadas
      continue
  return groups


def build_instance(
    q: int,
    p: int,
    k_values: Dict[int, int],
    l_values: Dict[int, int],
    groups_text: str,
    preassign: Dict[Tuple[int, int], int],
    availability: Dict[Tuple[int, int], int],
) -> TimetablingInstance:
  groups = parse_groups(groups_text, q)
  instance = TimetablingInstance(
      q=q,
      p=p,
      k=k_values,
      l=l_values,
      groups=groups,
      preassignment=preassign,
      availability=availability,
  )
  return instance


def result_matrix(result: TimetablingResult, q: int, p: int) -> List[Dict[str, int]]:
  rows: List[Dict[str, int]] = []
  for i in range(1, q + 1):
    row: Dict[str, int] = {"Curso": i}
    for k in range(1, p + 1):
      row[f"P{k}"] = result.assignment.get((i, k), 0)
    rows.append(row)
  return rows


def main() -> None:
  st.title("Course Timetabling Solver")
  st.caption("Inicializa una instancia y ejecuta un algoritmo greedy para resolverla")

  with st.sidebar:
    st.header("Parámetros")
    q = st.number_input("Número de cursos (q)", min_value=1, max_value=200, value=5, step=1)
    p = st.number_input("Número de períodos (p)", min_value=1, max_value=50, value=5, step=1)

  st.divider()

  with st.form("config_form"):
    st.subheader("Clases por curso (k_i)")
    k_values: Dict[int, int] = {}
    cols_k = st.columns(min(q, 6))
    for i in range(1, q + 1):
      col = cols_k[(i - 1) % len(cols_k)]
      k_values[i] = col.number_input(f"Curso {i}", min_value=0, max_value=p, value=1, step=1)

    st.subheader("Capacidad de aulas por período (l_k)")
    l_values: Dict[int, int] = {}
    cols_l = st.columns(min(p, 6))
    for k in range(1, p + 1):
      col = cols_l[(k - 1) % len(cols_l)]
      l_values[k] = col.number_input(f"Período {k}", min_value=0, max_value=1000, value=3, step=1)

    st.subheader("Grupos de conflicto (una línea por grupo)")
    st.caption("Ejemplo: '1 2 3' en una línea y '4,5' en otra")
    groups_text = st.text_area("Grupos", value="1 2\n3 4", height=100)

    st.subheader("Preasignaciones y Disponibilidades")
    advanced = st.checkbox("Configurar preasignaciones y disponibilidades (opcional)", value=False)

    preassign: Dict[Tuple[int, int], int] = {}
    availability: Dict[Tuple[int, int], int] = {}

    if advanced:
      st.caption("Selecciona períodos para cada curso")
      for i in range(1, q + 1):
        st.markdown(f"**Curso {i}**")
        cols = st.columns(2)
        pre_sel = cols[0].multiselect(
            f"Preasignaciones (y=1)", options=list(range(1, p + 1)), default=[], key=f"pre_{i}"
        )
        avail_sel = cols[1].multiselect(
            f"Disponibles (a=1)", options=list(range(1, p + 1)), default=list(range(1, p + 1)), key=f"avail_{i}"
        )
        for k in range(1, p + 1):
          preassign[(i, k)] = 1 if k in pre_sel else 0
          availability[(i, k)] = 1 if k in avail_sel else 0
    else:
      # por defecto: sin preasignaciones, todo disponible
      for i in range(1, q + 1):
        for k in range(1, p + 1):
          preassign[(i, k)] = 0
          availability[(i, k)] = 1

    submitted = st.form_submit_button("Resolver")

  if submitted:
    instance = build_instance(q, p, k_values, l_values, groups_text, preassign, availability)

    st.info(f"Factible por slots (clases totales {instance.get_total_classes()} <= slots totales {instance.get_total_classroom_slots()}): {instance.is_feasible()}")

    result = solve_timetabling(instance)

    if result.ok:
      st.success("Instancia resuelta: todos los cursos asignados")
    else:
      st.warning("No se pudo asignar completamente la instancia")

    if result.messages:
      for msg in result.messages:
        st.write(f"- {msg}")

    st.subheader("Asignación y_{ik} (0/1)")
    rows = result_matrix(result, q, p)
    st.dataframe(rows, use_container_width=True)

    st.subheader("Carga por período")
    carga_rows = [{"Período": k, "Usado": result.period_load[k], "Capacidad": l_values.get(k, 0)} for k in range(1, p + 1)]
    st.dataframe(carga_rows, use_container_width=True)


if __name__ == "__main__":
  main()
