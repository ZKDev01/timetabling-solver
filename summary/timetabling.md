# Descripción de Timetabling Problem
El problema estandarizado de planificación de horarios implica asignar recursos limitados (como aulas y profesores) a un conjunto de actividades (clase o exámenes) dentro de un marco temporal específico. El objetivo es crear un horario que minimice conflictos (como solapamientos entre clases) y maximice la utilización eficiente del espacio y del tiempo. Este problema presenta múltiples restricciones, como la disponibilidad de los profesores y las preferencias de los estudiantes. Dichas restricciones dependen exclusivamente del alcance de la institución. 

El problema específico de planificación de horarios es **Planificación de Horarios de Cursos Universitarios** (**University Course Timetabling Problem**) y este tiene dos posibles clasificaciones: Curriculum-based UCTP (CB-UCTP) y Post-Enrolment UCTP (PE-UCTP)
- **CB-UCTP**: El horario se construye para grupos abstractos de estudiantes que siguen un plan de estudios fijo (curriculum) Un curriculum se define como un grupo de cursos que comparten estudiantes comunes. El objetivo es garantizar que no se impartan cursos dentro del mismo curriculum a la misma hora. 
- **PE-UCTP**: El horario se construye después de que los estudiantes se hayan inscrito en cursos individuales, utilizando las listas reales de matriculados para evitar conflictos. 
# Análisis Preliminar de CB-UCTP
El CB-UCTP es un subtipo específico del University Course Timetabling Problem, que se enfoque en construir horarios de cursos universitarios antes de que los estudiantes realicen su matrícula individual. Se basa en la estructura fija de los planes de estudio (curriculum), que definen grupos de cursos que suelen ser cursados por un mismo conjunto de estudiantes.

**Diferencia CB-UCTP y PE-UCTP**: En lugar de usar listas de inscripción, como en PE-UCTP, el CB-UCTP usa "curriculum" como conjuntos de cursos que comparten estudiantes hipotéticos. Ejemplo: Curriculum "Ciencias de la Computación (Semestre 1)" incluye: "Lógica", "Análisis Matemático", "Álgebra", "Programación". Estos cursos no deben programarse a la misma hora, porque un mismo grupo de estudiantes debería poder asistir a todos

**Elementos Principales del Problema**: Cursos, Curriculum, Períodos, Recursos (Aulas y Profesores)
- **Cursos**: Unidades principales que requieren planificación horaria. 
- **Curriculum**: Agrupaciones lógicas de cursos que representan grupos de estudiantes. Cada curriculum contiene un conjunto de cursos relacionados y la cantidad de estudiantes que posee
- **Períodos**: Unidades discretas de tiempo para programación
- **Aulas**: Espacios físicos disponibles para impartir clases y cada aula tiene una capacidad máxima de estudiantes. 
- **Profesores**: Personal docente responsable de impartir los cursos y cada profesor está calificado para impartir un conjunto de cursos

**Características Específicas del Problema**:
- Los profesores y aulas tienen disponibilidad limitada en ciertos períodos.
- Las clases poseen un número finito de clases pero para simplicidad del modelo y sus restricciones se va a decir que todas las clases que tiene un curso serán impartidas en el período, aula y profesor asignado

**Restricciones Duras**: Restricciones que deben cumplirse para que una planificación sea válida:
- *Asignación Completa de Cursos*: Todos los cursos deben ser asignados a un período y un aula
- *No Superposición por Profesor*: Un profesor no puede impartir múltiples clases al mismo tiempo
- *No Superposición por Curriculum*: Dos cursos pertenecientes al mismo curriculum no pueden tener clases programadas simultáneamente
- *Unicidad de Aula por Período*: Cada aula puede albergar como máximo una clase por período
- *Capacidad del Profesor sobre un Curso*: Cada profesor está calificado para impartir un conjunto de cursos y la clase a la cual este asignado debe pertenecer a ese conjunto
- *Respecto de Disponibilidad*: Los profesores y las aulas tienen disponibilidad limitada
- *Capacidad de Aula*: El aula asignada tiene que tener capacidad para todos los estudiantes que van a recibir el curso

**Observaciones**:
- Un aula puede ser utilizada para dar clases a dos o más grupos que compartan un curso, pero está aula tiene que tener la capacidad 

**Restricciones Blandas**: Restricciones que no son necesarias su validación para que una asignación sea válida, pero se busca minimizar el número de restricciones violadas:
- *Preferencias de Turno*: Asignar ciertos tipos de cursos a turnos preferentes 
- *Minimizar GAP por Curriculum*: Minimizar períodos vacíos entre clases del mismo curriculum

**Futuras Restricciones Blandas a Considerar**:
- *Adecuación de Capacidad para Cursos en Múltiples Curriculum*: Para cada curso que está presente en más de un curriculum, cuando se asigna un aula a una clase de dicho curso, se prefiere que la capacidad del aula sea suficiente para acomodar al número total estimado de estudiantes de todos los curriculums que incluyen este curso. Si el aula asignada tiene una capacidad menor a ese total, se incurre en una penalización que aumenta con el déficit de capacidad
- *Agrupamiento por Tipo de Actividad*: Para un curriculum, se prefiere agrupar temporalmente las clases del mismo tipo (todas las clases teóricas juntas, todas las clases prácticas juntas) 
- *Distribución Uniforme de las Clases*: Las clases de cada curso se distribuyen uniformemente en un número mínimo de días laborales
# Evaluación de una Instancia del Problema
**Evaluación de una Instancia del Problema**: El problema al ser un problema NP-Completo encontrar una instancia que sea factible es NP y puede la instancia encontrada ser evaluada, ya sea factible o no, a través de una *función objetivo*. Esta función objetivo determina la calidad de una solución. En caso de que el problema tenga más de una instancia factible entonces, dependiendo de lo que se desee, una instancia es mejor que otra utilizando como medición la función objetivo. 
- *Factibilidad*: Una solución es considerable factible cuando satisface todas las restricciones duras enumeradas anteriormente
- *Calidad*: La calidad de una solución factible se mide mediante una función de costo ponderada que cuantifica el grado de violación de las restricciones blandas, donde cada restricción blanda tiene un peso asignado según su importancia relativa (los valores de los pesos puede ajustarse según las prioridades del instituto). Se busca minimizar esta función de costo ponderada. 
___
**UCTP como Problema de Decisión**: Se busca conocer si una instancia cualquiera del problema es factible. Esto significa que satisface las restricciones presentadas. Este problema es NP-Completo porque es reducible a través del Problema de Coloración de Grafos y existe un certificado para una instancia que confirma en tiempo polinomial si es solución factible

**UCTP como Problema de Optimización**: Se busca optimizar el problema de maximizar las asignaciones según una función de preferencias que mapea una asignación de: curso, período, aula, profesor con un valor real positivo. Este problema es NP-Duro porque es reducible a través del Problema de Coloración de Grafos (UCTP clásico). Mientras que la definición del problema con la función objetivo presentada sigue siendo NP-Duro pero es más fácil demostrar la clase de complejidad a través de una reducción al Maximum Weight Independent Set Problem.
# Modelo Matemático
**Conjuntos**:
- $C:$ Conjunto de cursos
- $Q:$ Conjunto de curriculums. Cada curriculum $q \in Q$ es un subconjunto de cursos: $C_{q} \subseteq C$
- $P:$ Conjunto de períodos de tiempo
- $R:$ Conjunto de aulas
- $T:$ Conjunto de profesores
- $F:$ Conjunto de preferencias. Cada preferencia $f \in F$ es una tupla ($c_{f}, p_{f}, r_{f}, t_{f}$) 
---
**Parámetros**:
- $\text{estudiantes}(c):$ número de estudiantes del curso $c \in C$
- $\text{capacidad}(r):$ capacidad (número de estudiantes) del aula $r \in R$
- $C_{t} \subseteq C:$ conjunto de cursos para los que el profesor $t \in T$ está calificado 
- $\text{disposición}(t,p) \in \{ 0,1 \}:$ $1$ si el profesor $t$ está disponible en el período $p$, $0$ en caso contrario
- $\text{disposición}(r,p) \in \{ 0,1 \}:$ $1$ si el aula $r$ está disponible en el período $p$, $0$ en caso contrario
---
**Variables de Decisión**: 
- $x_{c,p,r,t} \in \{ 0,1 \}$ para todo $c \in C, p \in P, r \in R, t \in T$ tal que $c \in C(t)$ y $\text{capacidad}(r) \geq \text{estudiantes}(c)$
- $x_{c,p,r,t} = 1$ si el curso $c$ se asigna al período $p$, aula $r$ y profesor $t$; $0$ en caso contrario.
---
**Restricciones Duras**: 
- *Asignación completa de cada curso*:
$$\sum_{p \in P} \sum_{r \in R} \sum_{t \in T} x_{c,p,r,t} = 1 : \forall c \in C $$
- *No superposición por profesor*:
$$\sum_{c \in C_t} \sum_{r \in R} x_{c,p,r,t} \leq 1 : \forall t \in T, \forall p \in P$$
- *No superposición por curriculum*:
$$\sum_{ c\in C_q } \sum_{r \in R} \sum_{t \in T} x_{c,p,r,t} \leq 1 : \forall q \in Q, \forall p \in P$$
- *Unicidad de aula por período*:
$$\sum_{c \in C} \sum_{t \in T} x_{c,p,r,t} \leq 1 : \forall r \in R, \forall p \in P$$
- *Respeto de disponibilidad de profesores*:
$$x_{c,p,r,t} \leq \text{disposición}(t,p) : \forall c \in C, p \in P, r \in R, t \in T \text{ con } c \in C_t$$
- *Respeto de disponibilidad de aulas*:
$$x_{c,p,r,t} \leq \text{disposición}(r,p) : \forall c \in C, p \in P, r \in R, t \in T \text{ con } c \in C_t$$
___
**Función Objetivo**: Maximizar el número de preferencias cumplidas:
$$\max \sum_{f \in F} x_{ c_f, p_f, r_f, t_f }$$
---
**Observaciones**:
- Las restricciones de *capacidad del aula y calificación del profesor* se incorporan implícitamente al definir las variables $x_{c,p,r,t}$ solo para combinaciones factibles ($\text{capacidad}(r) \geq \text{estudiantes}(c)$ y $c \in C_{t}$)
- El modelo busca una solución factible (que cumpla todas las restricciones duras) y, entre ellas, maximiza el número de preferencias asignadas según la institución
# Transformación: Grafo de Conflicto
Un Grafo de Conflicto representa las incompatibilidades entre asignaciones posibles. Cada vértice corresponde a una asignación factible individual, y las aristas indican conflictos que impiden que dos asignaciones coexistan en una solución válida. 
## Pasos de Transformación
**Paso 1**: **Definición de Vértices**
- Cada vértice representa una asignación factible individual de un curso a un período, aula y profesor
- *Expresión*: Para cada combinación $(c,p,r,t)$ que cumple lo siguiente, se crea $v = (c,p,r,t)$:
	- $c \in C$ (curso)
	- $p \in P$ (período)
	- $r \in R$ con $\text{capacidad}(r) \geq \text{estudiantes}(c)$
	- $t \in T$ con $c \in C_t$ (profesor calificado)
	- $\text{disposición}(t, p) = 1$ (profesor disponible)
	- $\text{disposición}(r, p) = 1$ (aula disponible)
- *Observación*: Este vértice $v$ corresponde a las variables $x_{c,p,r,t}$ con dominio restringido a combinaciones válidas. 
___
**Paso 2**: **Definición de Aristas** (**Conflictos**) $\Rightarrow$ Si dos asignaciones comparten cualquier recurso (curso, profesor, aula) en el mismo período, o pertenecen al mismo curriculum en el mismo período, no pueden coexistir en una solución factible. Se crea una arista no dirigida entre dos vértices $v_1 = (c_1, p_1, r_1, t_1)$ y $v_2 = (c_2,p_2,r_2,t_2)$ si al menos una de las siguientes condiciones de conflicto se cumplen:
- $c_1 = c_2:$ un curso no puede asignarse dos veces
- $t_1 = t_2 \land p_1 = p_2:$ un profesor no puede dar dos puntos cursos simultáneamente 
- $r_1 = r_2 \land p_1 = p_2:$ un aula no puede albergar dos cursos simultáneamente 
- $p_1 = p_2 \land \exists q \in Q$ tal que $c_1 \in C_q$ y $c_2 \in C_q:$ cursos de un mismo curriculum no pueden superponerse temporalmente
___
**Paso 3**: **Estructura del Grafo Resultante**. Grafo no dirigido $G = (V,E)$ donde $V$ es el conjunto de vértices (asignaciones individuales factibles) y $E$ es el conjunto de aristas (pares de asignaciones conflictivas)
## Interpretación de la Solución en el Grafo
Una solución factible del UCTP corresponde a un subconjunto $S \subseteq V$ que cumple:
1. *Cobertura de Cursos*:  Para cada curso $c \in C$, existe exactamente un vértice en $S$ con curso $c$.
2. *Independencia*: $S$ es un conjunto independiente en $G$ (ningún par de vértices en $S$ está conectado por una arista)
## Evaluación de la Solución en el Grafo
Una solución factible del UCTP utilizando el Grafo de Conflicto puede evaluarse con la función objetivo presentada en el modelo matemático. Esta función es usada para calcular el cumplimiento de preferencias y se quiere maximizar el valor de dicha función. En el grafo definido anterior, a cada vértice se le asigna un peso según el conjunto de preferencias $F$. 

*Observación*: Cada preferencia $f \in F$ es una tupla $(c_f,p_f,r_f,t_f)$ 
## Complejidad Temporal de la Transformación
**Complejidad Polinomial**: Complejidad que puede expresarse como $O(n^k)$ donde $n$ es el tamaño de la entrada y $k$ es una constante (independiente de $n$). 
___
**Generación de Vértices**: Para cada combinación $(c,p,r,t)$: 
- Número de combinaciones brutas: $|C| \cdot |P| \cdot |R| \cdot |T|$
- Verificaciones por combinación (tiempo constante $O(1)$) 

**Complejidad de Generación de Vértices**: $O(|C| \cdot |P| \cdot |R| \cdot |T|)$ 
___
**Generación de Aristas**: Comparar todos los pares ($v_1,v_2$) con las 4 condiciones de conflicto en $O(1)$. Se tienen $n(n-1)/2$, donde $n$ es el número de vértices válidos. 

**Complejidad de Generación de Aristas**: $O(n^2)$
___
**Complejidad Total**: Complejidad de Generación de Vértices $+$ Complejidad de Generación de Aristas $\to$ $O(n^2)$ donde $n = |C| \cdot |P| \cdot |R| \cdot |T|$ tomando como peor caso: combinaciones totalmente factibles. 
