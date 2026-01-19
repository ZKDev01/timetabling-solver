from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional


@dataclass
class CourseSection:
  "Representa una sección de un curso con un subconjunto de estudiantes"
  id: int
  course_name: str
  section_id: int                       # Identificador de sección (0 para la única sección, 1,2,... para múltiples)
  curriculum_students: Dict[int, int]   # curriculum_id -> número de estudiantes

  @property
  def total_students(self) -> int:
    return sum(self.curriculum_students.values())

  @property
  def curriculum_ids(self) -> Set[int]:
    return set(self.curriculum_students.keys())

  def get_name(self) -> str:
    if self.section_id == 0:
      return self.course_name
    return f"{self.course_name} - Sección {self.section_id}"

  def __str__(self):
    return f"{self.get_name()} ({self.total_students} estudiantes)"


@dataclass
class Room:
  "Representa un aula con su capacidad y disponibilidad"
  id: int
  name: str
  capacity: int = 0
  availability: Set[int] = field(default_factory=set)

  def __str__(self):
    return f"{self.name} (Capacidad: {self.capacity})"


@dataclass
class Teacher:
  "Representa un profesor con sus cursos y disponibilidad"
  id: int
  name: str
  course_names: Set[str] = field(default_factory=set)
  availability: Set[int] = field(default_factory=set)

  def __str__(self):
    return f"{self.name}"


@dataclass
class Curriculum:
  "Representa un curriculum con sus cursos y número de estudiantes"
  id: int
  name: str
  num_students: int = 0
  course_names: Set[str] = field(default_factory=set)

  def __str__(self):
    return f"{self.name} ({self.num_students} estudiantes)"


@dataclass
class Preference:
  "Representa una preferencia de asignación"
  course_name: str
  period: int
  room_name: Optional[str]
  teacher_name: Optional[str]
  value: float


@dataclass
class Assignment:
  "Representa una asignación de sección de curso a período, aula y profesor"
  section_id: int
  period: int
  room_id: int
  teacher_id: int


class TimetablingInstance:
  def __init__(self, name: str = "Instancia sin nombre"):
    self.name = name
    self.course_sections: Dict[int, CourseSection] = {}
    self.course_base_info: Dict[str, Dict] = {}
    self.rooms: Dict[int, Room] = {}
    self.teachers: Dict[int, Teacher] = {}
    self.curriculums: Dict[int, Curriculum] = {}
    self.periods: Set[int] = set()
    self.preferences: List[Preference] = []
    self.assignments: Dict[int, Assignment] = {}

    self._next_section_id = 1
    self._next_room_id = 1
    self._next_teacher_id = 1
    self._next_curriculum_id = 1

  def add_course(self, name: str, curriculum_names: List[str] = None) -> None:
    "Agrega un curso base (sin crear secciones aún)."
    if name not in self.course_base_info:
      # Convertir nombres de curriculums a IDs
      curriculum_ids = set()
      if curriculum_names:
        for curriculum_name in curriculum_names:
          curriculum_id = self._find_curriculum_by_name(curriculum_name)
          if curriculum_id is None:
            raise ValueError(
                f"Curriculum '{curriculum_name}' no encontrado. "
                f"Debe crear el curriculum primero."
            )
          curriculum_ids.add(curriculum_id)

      self.course_base_info[name] = {
          'curriculum_ids': curriculum_ids,
          'max_section_id': 0
      }

  def add_room(self, name: str, capacity: int, available_periods: List[int] = None) -> int:
    "Agrega un aula"
    room_id = self._next_room_id
    self._next_room_id += 1

    room = Room(
        id=room_id,
        name=name,
        capacity=capacity,
        availability=set(available_periods) if available_periods else set()
    )
    self.rooms[room_id] = room
    self.periods.update(room.availability)

    return room_id

  def add_teacher(self, name: str, course_names: List[str] = None, available_periods: List[int] = None) -> int:
    "Agrega un profesor"
    teacher_id = self._next_teacher_id
    self._next_teacher_id += 1

    teacher = Teacher(
        id=teacher_id,
        name=name,
        course_names=set(course_names) if course_names else set(),
        availability=set(available_periods) if available_periods else set()
    )
    self.teachers[teacher_id] = teacher
    self.periods.update(teacher.availability)

    return teacher_id

  def add_curriculum(self, name: str, num_students: int, course_names: List[str] = None) -> int:
    "Agrega un curriculum con número de estudiantes"
    curriculum_id = self._next_curriculum_id
    self._next_curriculum_id += 1

    curriculum = Curriculum(
        id=curriculum_id,
        name=name,
        num_students=num_students,
        course_names=set(course_names) if course_names else set()
    )
    self.curriculums[curriculum_id] = curriculum

    # Actualizar cursos base con este curriculum
    for course_name in curriculum.course_names:
      if course_name not in self.course_base_info:
        self.add_course(course_name, [])
      self.course_base_info[course_name]['curriculum_ids'].add(curriculum_id)

    return curriculum_id

  def add_preference(self, course_name: str, period: int, room_name: str, teacher_name: str, value: float) -> None:
    "Agrega una preferencia de asignación"
    preference = Preference(course_name, period, room_name, teacher_name, value)
    self.preferences.append(preference)

  def create_course_sections(self) -> None:
    "Crea secciones para todos los cursos basándose en la capacidad de las aulas. Si un curso tiene más estudiantes que la capacidad máxima del aula, se divide en múltiples secciones."
    if not self.rooms:
      raise ValueError("No hay aulas definidas. Debe agregar aulas primero.")

    # Encontrar la capacidad máxima del aula
    max_capacity = max(room.capacity for room in self.rooms.values())

    # Limpiar secciones existentes
    self.course_sections.clear()
    self._next_section_id = 1

    for course_name, course_info in self.course_base_info.items():
      curriculum_ids = course_info['curriculum_ids']

      if not curriculum_ids:
        continue

      # Calcular estudiantes totales por curriculum para este curso
      curriculum_students = {}
      total_students = 0

      for curriculum_id in curriculum_ids:
        if curriculum_id in self.curriculums:
          curriculum = self.curriculums[curriculum_id]
          curriculum_students[curriculum_id] = curriculum.num_students
          total_students += curriculum.num_students

      if total_students == 0:
        continue

      # Verificar si necesitamos dividir en secciones
      if total_students <= max_capacity:
        # No es necesario dividir, crear una sola sección
        section = CourseSection(
            id=self._next_section_id,
            course_name=course_name,
            section_id=0,
            curriculum_students=curriculum_students.copy()
        )
        self.course_sections[self._next_section_id] = section
        self._next_section_id += 1
      else:
        # Necesitamos dividir en múltiples secciones
        # Estrategia: intentar agrupar estudiantes de curriculums juntos cuando sea posible
        sections = self._split_course_into_sections(course_name, curriculum_students, max_capacity)

        for i, section_students in enumerate(sections):
          section = CourseSection(
              id=self._next_section_id,
              course_name=course_name,
              section_id=i + 1,
              curriculum_students=section_students
          )
          self.course_sections[self._next_section_id] = section
          self._next_section_id += 1

  def _split_course_into_sections(self, course_name: str, curriculum_students: Dict[int, int], max_capacity: int) -> List[Dict[int, int]]:
    sections = []

    for curriculum_id, students in curriculum_students.items():
      while students > max_capacity:
        # Crear una sección con capacidad máxima para este curriculum
        section = {curriculum_id: max_capacity}
        sections.append(section)
        students -= max_capacity

      if students > 0:
        # Si queda algo de este curriculum, lo manejaremos después
        curriculum_students[curriculum_id] = students

    remaining_curriculums = [(cid, students) for cid, students in curriculum_students.items() if students > 0]

    if not remaining_curriculums:
      return sections

    # Ordenar por número de estudiantes (descendente)
    remaining_curriculums.sort(key=lambda x: x[1], reverse=True)

    # Algoritmo greedy para agrupar
    current_section = {}
    current_total = 0

    for curriculum_id, students in remaining_curriculums:
      if current_total + students <= max_capacity:
        # Agregar a la sección actual
        current_section[curriculum_id] = students
        current_total += students
      else:
        if current_section:
          sections.append(current_section)

        # Si este curriculum por sí solo cabe en una sección
        if students <= max_capacity:
          current_section = {curriculum_id: students}
          current_total = students
        else:
          # Esto no debería pasar si ya manejamos curriculums grandes arriba
          # Pero por si acaso, dividimos
          while students > max_capacity:
            sections.append({curriculum_id: max_capacity})
            students -= max_capacity

          if students > 0:
            current_section = {curriculum_id: students}
            current_total = students
          else:
            current_section = {}
            current_total = 0

    if current_section:
      sections.append(current_section)

    return sections

  def assign_section(self, section_id: int, period: int, room_id: int, teacher_id: int) -> None:
    "Asigna una sección de curso a un período, aula y profesor"
    assignment = Assignment(
        section_id=section_id,
        period=period,
        room_id=room_id,
        teacher_id=teacher_id
    )
    self.assignments[section_id] = assignment

  def assign_by_name(self, course_name: str, section_num: int, period: int,
                     room_name: str, teacher_name: str) -> None:
    """Asigna una sección usando nombres en lugar de IDs."""
    # Encontrar la sección
    section_id = None
    for sid, section in self.course_sections.items():
      if section.course_name == course_name and section.section_id == section_num:
        section_id = sid
        break

    if section_id is None:
      raise ValueError(f"No se encontró la sección {section_num} del curso {course_name}")

    room_id = self._find_room_by_name(room_name)
    teacher_id = self._find_teacher_by_name(teacher_name)

    if room_id is None or teacher_id is None:
      raise ValueError("No se pudo encontrar aula o profesor con los nombres proporcionados")

    self.assign_section(section_id, period, room_id, teacher_id)

  def check_hard_constraints(self) -> Tuple[bool, List[str]]:
    "Verifica todas las restricciones duras"
    violations = []

    # 1. Asignación Completa de Secciones
    missing_sections = set(self.course_sections.keys()) - set(self.assignments.keys())
    if missing_sections:
      section_names = [self.course_sections[sid].get_name() for sid in missing_sections]
      violations.append(f"Secciones sin asignar: {', '.join(section_names)}")

    # Verificar restricciones solo si hay asignaciones
    if self.assignments:
      # Check if periods are valid
      for section_id, assignment in self.assignments.items():
        if assignment.period not in self.periods:
          violations.append(f"Período {assignment.period} no está definido en la instancia")

      # 2. No Superposición por Profesor
      teacher_periods: Dict[Tuple[int, int], List[int]] = {}  # (teacher_id, period) -> [section_ids]
      for section_id, assignment in self.assignments.items():
        key = (assignment.teacher_id, assignment.period)
        if key not in teacher_periods:
          teacher_periods[key] = []
        teacher_periods[key].append(section_id)

      for (teacher_id, period), section_ids in teacher_periods.items():
        if len(section_ids) > 1:
          teacher_name = self.teachers[teacher_id].name
          section_names = [self.course_sections[sid].get_name() for sid in section_ids]
          violations.append(
              f"Profesor {teacher_name} tiene múltiples secciones en período {period}: {', '.join(section_names)}"
          )

      # 3. No Superposición por Curriculum
      # Para cada curriculum, no puede haber dos secciones del mismo curriculum a la misma hora
      # Incluso si son de cursos diferentes
      curriculum_periods: Dict[Tuple[int, int], List[int]] = {}  # (curriculum_id, period) -> [section_ids]
      for section_id, assignment in self.assignments.items():
        section = self.course_sections[section_id]
        for curriculum_id in section.curriculum_ids:
          key = (curriculum_id, assignment.period)
          if key not in curriculum_periods:
            curriculum_periods[key] = []
          curriculum_periods[key].append(section_id)

      for (curriculum_id, period), section_ids in curriculum_periods.items():
        if len(section_ids) > 1:
          curriculum_name = self.curriculums[curriculum_id].name
          section_names = [self.course_sections[sid].get_name() for sid in section_ids]
          violations.append(
              f"Curriculum {curriculum_name} tiene múltiples secciones en período {period}: {', '.join(section_names)}"
          )

      # 4. Unicidad de Aula por Período
      room_periods: Dict[Tuple[int, int], List[int]] = {}  # (room_id, period) -> [section_ids]
      for section_id, assignment in self.assignments.items():
        key = (assignment.room_id, assignment.period)
        if key not in room_periods:
          room_periods[key] = []
        room_periods[key].append(section_id)

      for (room_id, period), section_ids in room_periods.items():
        if len(section_ids) > 1:
          room_name = self.rooms[room_id].name
          section_names = [self.course_sections[sid].get_name() for sid in section_ids]
          violations.append(
              f"Aula {room_name} tiene múltiples secciones en período {period}: {', '.join(section_names)}"
          )

      # 5. Capacidad del Profesor sobre un Curso
      for section_id, assignment in self.assignments.items():
        teacher = self.teachers.get(assignment.teacher_id)
        section = self.course_sections[section_id]
        if teacher and section.course_name not in teacher.course_names:
          violations.append(
              f"Profesor {teacher.name} no está calificado para impartir {section.get_name()}"
          )

      # 6. Respecto de Disponibilidad
      for section_id, assignment in self.assignments.items():
        # Verificar disponibilidad del profesor
        teacher = self.teachers.get(assignment.teacher_id)
        if teacher and assignment.period not in teacher.availability:
          violations.append(
              f"Profesor {teacher.name} no disponible en período {assignment.period}"
          )

        # Verificar disponibilidad del aula
        room = self.rooms.get(assignment.room_id)
        if room and assignment.period not in room.availability:
          violations.append(
              f"Aula {room.name} no disponible en período {assignment.period}"
          )

      # 7. Capacidad de Aula
      for section_id, assignment in self.assignments.items():
        room = self.rooms.get(assignment.room_id)
        section = self.course_sections.get(section_id)
        if room and section and room.capacity < section.total_students:
          violations.append(
              f"Aula {room.name} (capacidad: {room.capacity}) "
              f"no tiene suficiente espacio para {section.get_name()} "
              f"({section.total_students} estudiantes)"
          )

    is_valid = len(violations) == 0
    return is_valid, violations

  def calculate_objective(self) -> float:
    "Calcula el valor de la función objetivo"
    total_value = 0.0

    for section_id, assignment in self.assignments.items():
      section = self.course_sections.get(section_id)
      if not section:
        continue

      # Buscar preferencia que coincida con esta asignación
      for preference in self.preferences:
        if (preference.course_name == section.course_name and
            preference.period == assignment.period and
            preference.room_name == self.rooms[assignment.room_id].name and
                preference.teacher_name == self.teachers[assignment.teacher_id].name):
          total_value += preference.value
          break

    return total_value

  def _find_curriculum_by_name(self, name: str) -> Optional[int]:
    "Busca un curriculum por nombre y devuelve su ID"
    for curriculum in self.curriculums.values():
      if curriculum.name == name:
        return curriculum.id
    return None

  def _find_room_by_name(self, name: str) -> Optional[int]:
    "Busca un aula por nombre y devuelve su ID"
    for room in self.rooms.values():
      if room.name == name:
        return room.id
    return None

  def _find_teacher_by_name(self, name: str) -> Optional[int]:
    "Busca un profesor por nombre y devuelve su ID"
    for teacher in self.teachers.values():
      if teacher.name == name:
        return teacher.id
    return None

  def print_summary(self) -> None:
    "Imprime un resumen de la instancia"
    print(f"Resumen de Instancia: {self.name}")

    print(f"\nCurriculums:")
    for curriculum in self.curriculums.values():
      print(f"- {curriculum}")

    print(f"\nCursos base:")
    for course_name, info in self.course_base_info.items():
      curriculum_names = [self.curriculums[cid].name for cid in info['curriculum_ids'] if cid in self.curriculums]
      print(f"- {course_name}: {', '.join(curriculum_names)}")

    print(f"\nSecciones creadas:")
    for section in self.course_sections.values():
      curriculum_details = []
      for curriculum_id, students in section.curriculum_students.items():
        if curriculum_id in self.curriculums:
          curriculum_details.append(f"{self.curriculums[curriculum_id].name} ({students})")
      print(f"- {section.get_name()}: {', '.join(curriculum_details)}")

    print(f"\nAulas: {len(self.rooms)}")
    for room in self.rooms.values():
      print(f"- {room}")

    print(f"\nProfesores: {len(self.teachers)}")
    for teacher in self.teachers.values():
      print(f"- {teacher}")

    print(f"\nPeríodos definidos: {len(self.periods)}")
    print(f"Asignaciones actuales: {len(self.assignments)}")

    # Verificar restricciones
    is_valid, violations = self.check_hard_constraints()
    status = "VÁLIDO" if is_valid else "INVÁLIDO"
    print(f"\nEstado: {status}")

    if not is_valid:
      print("Violaciones encontradas:")
      for violation in violations:
        print(f"  - {violation}")

    # Calcular función objetivo si hay asignaciones
    if self.assignments:
      objective = self.calculate_objective()
      print(f"Función objetivo: {objective:.2f}")

  def get_assignment_details(self) -> List[Dict]:
    "Obtiene detalles de todas las asignaciones"
    details = []
    for section_id, assignment in self.assignments.items():
      section = self.course_sections.get(section_id)
      room = self.rooms.get(assignment.room_id)
      teacher = self.teachers.get(assignment.teacher_id)

      if section and room and teacher:
        details.append({
            'sección': section.get_name(),
            'periodo': assignment.period,
            'aula': room.name,
            'profesor': teacher.name,
            'estudiantes': section.total_students,
            'capacidad_aula': room.capacity
        })
    return details

  def add_preference(self, course_name: str, period: int, room_name: str, teacher_name: str, value: float) -> None:
    "Agrega una preferencia de asignación"
    if not any(course_name == course for course in self.course_base_info):
      raise ValueError(f"Curso '{course_name}' no encontrado")
    if room_name is not None and not any(room_name == room.name for room in self.rooms.values()):
      raise ValueError(f"Aula '{room_name}' no encontrada")
    if teacher_name is not None and not any(teacher_name == teacher.name for teacher in self.teachers.values()):
      raise ValueError(f"Profesor '{teacher_name}' no encontrado")

    preference = Preference(
        course_name=course_name,
        period=period,
        room_name=room_name,
        teacher_name=teacher_name,
        value=value
    )
    self.preferences.append(preference)


def create_simple_example() -> TimetablingInstance:
  instance = TimetablingInstance("Ejemplo Simple: Aulas Grandes y Aulas Pequeñas")

  # 1. Crear curriculums con número de estudiantes
  # Curriculum 1: 100 estudiantes, cursos 1 y 2
  # Curriculum 2: 100 estudiantes, cursos 2 y 3
  instance.add_curriculum("Curriculum 1", 100, ["Curso 1", "Curso 2"])
  instance.add_curriculum("Curriculum 2", 100, ["Curso 2", "Curso 3"])

  # 2. Crear cursos base
  instance.add_course("Curso 1", ["Curriculum 1"])
  instance.add_course("Curso 2", ["Curriculum 1", "Curriculum 2"])
  instance.add_course("Curso 3", ["Curriculum 2"])

  # 3. Crear aulas con diferentes capacidades
  # Aula pequeña -> capacidad 100
  # Aula grande -> capacidad 200
  instance.add_room("Aula Pequeña", 100, list(range(1, 6)))
  instance.add_room("Aula Grande", 200, list(range(1, 6)))

  # 4. Crear profesores
  instance.add_teacher("Profesor A", ["Curso 1", "Curso 2"], list(range(1, 6)))
  instance.add_teacher("Profesor B", ["Curso 2", "Curso 3"], list(range(1, 6)))

  # 5. Crear secciones automáticamente basándose en la capacidad de las aulas
  instance.create_course_sections()

  return instance


def create_simple_example_2() -> TimetablingInstance:
  instance = TimetablingInstance("Ejemplo Simple: Solo Aulas Pequeñas")

  # 1. Crear curriculums
  instance.add_curriculum("Curriculum 1", 100, ["Curso 1", "Curso 2"])
  instance.add_curriculum("Curriculum 2", 100, ["Curso 2", "Curso 3"])

  # 2. Crear cursos base
  instance.add_course("Curso 1", ["Curriculum 1"])
  instance.add_course("Curso 2", ["Curriculum 1", "Curriculum 2"])
  instance.add_course("Curso 3", ["Curriculum 2"])

  # 3. Crear solo aulas pequeñas (capacidad 100)
  instance.add_room("Aula 101", 100, list(range(1, 6)))
  instance.add_room("Aula 102", 100, list(range(1, 6)))
  instance.add_room("Aula 103", 100, list(range(1, 6)))

  # 4. Crear profesores
  instance.add_teacher("Profesor A", ["Curso 1", "Curso 2"], list(range(1, 6)))
  instance.add_teacher("Profesor B", ["Curso 2", "Curso 3"], list(range(1, 6)))

  # 5. Crear secciones automáticamente
  instance.create_course_sections()

  return instance

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
