import streamlit as st
import pandas as pd
from typing import Dict, List, Set, Tuple

from src.data_structures.timetabling import (
    TimetablingInstance,
    Curriculum,
    Room,
    Teacher,
    CourseSection,
    Assignment,
)
from src.algorithms.timetabling_solver import solve_timetabling_with_graph_coloring


def parse_curriculums(text: str) -> List[Curriculum]:
  """Parse curriculums from text. Each line: id: course1, course2,..."""
  curriculums = []
  for line in text.splitlines():
    line = line.strip()
    if not line:
      continue
    if ':' in line:
      id_str, courses_str = line.split(':', 1)
      try:
        cid = int(id_str.strip())
        courses = [int(c.strip()) for c in courses_str.split(',') if c.strip()]
        curriculums.append(Curriculum(id=cid, courses=courses))
      except ValueError:
        continue
  return curriculums


def parse_curriculums(text: str) -> List[Tuple[str, int, List[str]]]:
  """Parse curriculums from text. Each line: name: num_students: course1,course2,..."""
  curriculums = []
  for line in text.splitlines():
    line = line.strip()
    if not line:
      continue
    parts = line.split(':')
    if len(parts) >= 3:
      name = parts[0].strip()
      try:
        num_students = int(parts[1].strip())
        courses = [c.strip() for c in parts[2].split(',') if c.strip()]
        curriculums.append((name, num_students, courses))
      except ValueError:
        continue
  return curriculums


def parse_rooms(text: str) -> List[Tuple[str, int]]:
  """Parse rooms from text. Each line: name: capacity"""
  rooms = []
  for line in text.splitlines():
    line = line.strip()
    if not line:
      continue
    if ':' in line:
      name, cap_str = line.split(':', 1)
      try:
        cap = int(cap_str.strip())
        rooms.append((name.strip(), cap))
      except ValueError:
        continue
  return rooms


def parse_teachers(text: str) -> List[Tuple[str, List[str]]]:
  """Parse teachers from text. Each line: name: course1,course2,..."""
  teachers = []
  for line in text.splitlines():
    line = line.strip()
    if not line:
      continue
    if ':' in line:
      name, courses_str = line.split(':', 1)
      courses = [c.strip() for c in courses_str.split(',') if c.strip()]
      teachers.append((name.strip(), courses))
  return teachers


def parse_preferences(text: str) -> List[Tuple[str, str, int, str, float]]:
  """Parse preferences from text. Each line: course | room | turn | teacher | value"""
  preferences = []
  for line in text.splitlines():
    line = line.strip()
    if not line:
      continue
    parts = line.split('|')
    if len(parts) == 5:
      course, room, turn_str, teacher, value_str = [p.strip() for p in parts]
      try:
        if turn_str.startswith('Turno '):
          period = int(turn_str[6:])
        else:
          period = int(turn_str)
        value = float(value_str)
        preferences.append((course, room, period, teacher, value))
      except ValueError:
        continue
  return preferences


def build_instance(
    days: int,
    periods_per_day: int,
    curriculums_text: str,
    rooms_text: str,
    teachers_text: str,
    preferences_text: str,
) -> TimetablingInstance:
  instance = TimetablingInstance("Manual Instance")
  periods = days * periods_per_day
  availability = list(range(1, periods + 1))

  # Add curriculums
  curriculums_data = parse_curriculums(curriculums_text)
  for name, num_students, courses in curriculums_data:
    instance.add_curriculum(name, num_students, courses)

  # Add rooms
  rooms_data = parse_rooms(rooms_text)
  for name, capacity in rooms_data:
    instance.add_room(name, capacity, availability)

  # Add teachers
  teachers_data = parse_teachers(teachers_text)
  for name, courses in teachers_data:
    instance.add_teacher(name, courses, availability)

  # Add courses (assuming all courses from curriculums)
  all_courses = set()
  for _, _, courses in curriculums_data:
    all_courses.update(courses)
  for course in all_courses:
    # Find curriculums that have this course
    curr_names = [name for name, _, courses in curriculums_data if course in courses]
    instance.add_course(course, curr_names)

  # Create sections
  instance.create_course_sections()

  # Add preferences
  preferences_data = parse_preferences(preferences_text)
  for course, room, period, teacher, value in preferences_data:
    instance.add_preference(course, period, room, teacher, value)

  # Set days and periods_per_day
  instance.days = days
  instance.periods_per_day = periods_per_day

  return instance


def assignments_matrix(instance: TimetablingInstance) -> List[Dict[str, str]]:
  rows = []
  for section_id, assignment in instance.assignments.items():
    section = instance.course_sections[section_id]
    row = {"Section": f"{section.course_name}.{section.section_id}"}
    row[f"P{assignment.period}"] = f"R{assignment.room_id}, T{assignment.teacher_id}"
    rows.append(row)
  return rows


def display_curriculum_schedules(instance: TimetablingInstance) -> None:
  days = instance.days
  periods_per_day = instance.periods_per_day

  for curriculum in instance.curriculums.values():
    st.subheader(f"Curriculum: {curriculum.name}")

    # Filtrar secciones del curriculum
    curriculum_sections = {
        sid: s for sid, s in instance.course_sections.items()
        if s.course_name in curriculum.course_names
    }

    # Crear diccionario para el DataFrame
    data = {}
    for d in range(1, days + 1):
      data[f"Día {d}"] = {}
      for p in range(1, periods_per_day + 1):
        data[f"Día {d}"][f"Período {p}"] = ""

    # Llenar con asignaciones
    for sid, section in curriculum_sections.items():
      if sid in instance.assignments:
        assignment = instance.assignments[sid]
        period = assignment.period
        day = ((period - 1) // periods_per_day) + 1
        period_in_day = ((period - 1) % periods_per_day) + 1
        room = instance.rooms[assignment.room_id]
        teacher = instance.teachers[assignment.teacher_id]
        cell = f"{section.course_name} ({room.name}, {teacher.name})"
        data[f"Día {day}"][f"Período {period_in_day}"] = cell

    # Crear DataFrame y mostrar
    df = pd.DataFrame(data)
    st.dataframe(df)


def main() -> None:
  st.title("Course Timetabling Solver")
  with st.sidebar:
    st.header("Parámetros")
    days = st.number_input("Número de días", min_value=1, max_value=10, value=5, step=1)
    periods_per_day = st.number_input("Períodos por día", min_value=1, max_value=10, value=5, step=1)
    heuristic = st.selectbox("Heurística de coloreo", options=["dsatur", "rlf"], index=0)

  st.divider()

  with st.form("config_form"):
    st.subheader("Curriculums")
    st.caption("Cada línea: nombre: número de estudiantes: curso1, curso2, ... (ej: Curriculum 1: 100: Curso 1, Curso 2)")
    curriculums_text = st.text_area("Curriculums", value="Curriculum 1: 100: Curso 1,Curso 2\nCurriculum 2: 100: Curso 2, Curso 3", height=100)

    st.subheader("Aulas")
    st.caption("Cada línea: nombre: capacidad (ej: Aula 1: 10)")
    rooms_text = st.text_area("Aulas", value="Aula 1: 10\nAula 2: 15", height=100)

    st.subheader("Profesores")
    st.caption("Cada línea: nombre: curso1,curso2,... (ej: Profesor 1: Curso 1,Curso 2)")
    teachers_text = st.text_area("Profesores", value="Profesor 1: Curso 1,Curso 2\nProfesor 2: Curso 2,Curso 3", height=100)

    st.subheader("Preferencias")
    st.caption("Cada línea: nombre_curso | aula | turno | profesor | valor (ej: Curso 1 | Aula 1 | Turno 1 | Profesor 1 | 10.0)")
    preferences_text = st.text_area("Preferencias", value="", height=100)

    submitted = st.form_submit_button("Resolver")

  if submitted:
    instance = build_instance(days, periods_per_day, curriculums_text, rooms_text, teachers_text, preferences_text)

    st.info(f"Instancia creada: {len(instance.course_sections)} secciones, {len(instance.rooms)} rooms, {len(instance.teachers)} teachers")

    solve_timetabling_with_graph_coloring(instance, heuristic)
    solved_instance = instance

    assigned_sections = len(solved_instance.assignments)
    total_sections = len(solved_instance.course_sections)
    is_valid, violations = solved_instance.check_hard_constraints()

    # Calcular valor total de preferencias satisfechas
    total_value = 0.0
    for pref in solved_instance.preferences:
      for sid, assignment in solved_instance.assignments.items():
        section = solved_instance.course_sections[sid]
        if section.course_name == pref.course_name and assignment.period == pref.period:
          room = solved_instance.rooms[assignment.room_id]
          teacher = solved_instance.teachers[assignment.teacher_id]
          if room.name == pref.room_name and teacher.name == pref.teacher_name:
            total_value += pref.value
            break

    st.info(f"Valor total de preferencias satisfechas: {total_value}")

    if is_valid:
      st.success("Instancia resuelta correctamente: todas las restricciones duras satisfechas")
      display_curriculum_schedules(solved_instance)
    else:
      st.error("Asignación inválida: se encontraron violaciones de restricciones")
      for msg in violations:
        st.write(f"- {msg}")


if __name__ == "__main__":
  main()
