from ..data_structures.graph import GraphInstance
from ..data_structures.timetabling import TimetablingInstance


def timetabling_to_graph(instance: TimetablingInstance) -> GraphInstance:
  """
  Transforma una instancia de Timetabling en una instancia de Graph.
  Crea nodos para cada elemento (curriculums, rooms, teachers, periods, courses)
  y aristas para representar relaciones y disponibilidades.
  """
  vertices = set()
  node_types = {}
  labels = {}
  edges = set()

  # Offset para IDs de vértices para evitar colisiones
  curriculum_offset = 0
  room_offset = 10000
  teacher_offset = 20000
  period_offset = 30000
  course_offset = 40000

  # Curriculums
  for cid, curriculum in instance.curriculums.items():
    vid = cid + curriculum_offset
    vertices.add(vid)
    node_types[vid] = 'Curriculum'
    labels[vid] = {
        'name': curriculum.name,
        'num_students': curriculum.num_students,
        'courses': list(curriculum.course_names)
    }

  # Rooms
  for rid, room in instance.rooms.items():
    vid = rid + room_offset
    vertices.add(vid)
    node_types[vid] = 'Room'
    labels[vid] = {
        'name': room.name,
        'capacity': room.capacity,
        'availability': list(room.availability)
    }

  # Teachers
  for tid, teacher in instance.teachers.items():
    vid = tid + teacher_offset
    vertices.add(vid)
    node_types[vid] = 'Teacher'
    labels[vid] = {
        'name': teacher.name,
        'course_names': list(teacher.course_names),
        'availability': list(teacher.availability)
    }

  # Periods
  for period in instance.periods:
    vid = period + period_offset
    vertices.add(vid)
    node_types[vid] = 'Period'
    labels[vid] = {'period': period}

  # Sections
  section_vertices = {}
  for sid, section in instance.course_sections.items():
    vid = sid + course_offset  # reuse course_offset as section_offset
    section_vertices[sid] = vid
    vertices.add(vid)
    node_types[vid] = 'Section'
    labels[vid] = {
        'course_name': section.course_name,
        'section_id': section.section_id,
        'curriculum_ids': list(section.curriculum_ids)
    }

  # Aristas
  # Section - Curriculum
  for sid, svid in section_vertices.items():
    section = instance.course_sections[sid]
    for cid in section.curriculum_ids:
      cvid = cid + curriculum_offset
      edges.add((min(svid, cvid), max(svid, cvid)))

  # Section conflicts: sections that share curriculum can't be in same period
  from itertools import combinations
  for sid1, sid2 in combinations(instance.course_sections.keys(), 2):
    section1 = instance.course_sections[sid1]
    section2 = instance.course_sections[sid2]
    if section1.curriculum_ids & section2.curriculum_ids:
      svid1 = section_vertices[sid1]
      svid2 = section_vertices[sid2]
      edges.add((min(svid1, svid2), max(svid1, svid2)))

  # Teacher - Section
  for tid, teacher in instance.teachers.items():
    tvid = tid + teacher_offset
    for sid, section in instance.course_sections.items():
      if section.course_name in teacher.course_names:
        svid = section_vertices[sid]
        edges.add((min(tvid, svid), max(tvid, svid)))

  # Room - Period
  for rid, room in instance.rooms.items():
    rvid = rid + room_offset
    for period in room.availability:
      pvid = period + period_offset
      edges.add((min(rvid, pvid), max(rvid, pvid)))

  # Teacher - Period
  for tid, teacher in instance.teachers.items():
    tvid = tid + teacher_offset
    for period in teacher.availability:
      pvid = period + period_offset
      edges.add((min(tvid, pvid), max(tvid, pvid)))

  # Section conflicts: sections that can't share period due to room capacity
  max_capacity = max(room.capacity for room in instance.rooms.values())
  for sid1, sid2 in combinations(instance.course_sections.keys(), 2):
    section1 = instance.course_sections[sid1]
    section2 = instance.course_sections[sid2]
    if section1.total_students + section2.total_students > max_capacity:
      svid1 = section_vertices[sid1]
      svid2 = section_vertices[sid2]
      edges.add((min(svid1, svid2), max(svid1, svid2)))

  # Crear adj_list
  adj_list = {v: set() for v in vertices}
  for u, v in edges:
    adj_list[u].add(v)
    adj_list[v].add(u)

  return GraphInstance(vertices=vertices, edges=edges, adj_list=adj_list, labels=labels, node_types=node_types)


def graph_to_timetabling(graph: GraphInstance) -> TimetablingInstance:
  """
  Transforma una instancia de Graph en una instancia de Timetabling.
  Reconstruye los elementos basándose en los tipos de nodos y labels.
  """
  instance = TimetablingInstance("From Graph")

  curriculums = {}
  rooms = {}
  teachers = {}
  periods = set()
  courses = set()

  # Offsets inversos
  curriculum_offset = 0
  room_offset = 10000
  teacher_offset = 20000
  period_offset = 30000
  course_offset = 40000

  for vertex in graph.vertices:
    type_ = graph.node_types.get(vertex, '')
    label = graph.labels.get(vertex, {})

    if type_ == 'Curriculum':
      name = label.get('name', f"Curriculum_{vertex}")
      num_students = label.get('num_students', 0)
      course_names = label.get('courses', [])
      cid = instance.add_curriculum(name, num_students, course_names)
      curriculums[vertex] = cid

    elif type_ == 'Room':
      name = label.get('name', f"Room_{vertex}")
      capacity = label.get('capacity', 100)
      availability = label.get('availability', [])
      rid = instance.add_room(name, capacity, availability)
      rooms[vertex] = rid

    elif type_ == 'Teacher':
      name = label.get('name', f"Teacher_{vertex}")
      course_names = label.get('course_names', [])
      availability = label.get('availability', [])
      tid = instance.add_teacher(name, course_names, availability)
      teachers[vertex] = tid

    elif type_ == 'Period':
      period = label.get('period', vertex - period_offset)
      periods.add(period)

    elif type_ == 'Course':
      name = label.get('name', f"Course_{vertex}")
      curriculums_list = label.get('curriculums', [])
      curriculum_names = [instance.curriculums[curriculums[vid]].name for vid in curriculums_list if vid in curriculums]
      instance.add_course(name, curriculum_names)
      courses.add(name)

  # Actualizar periods
  instance.periods.update(periods)

  # Crear secciones
  instance.create_course_sections()

  return instance
