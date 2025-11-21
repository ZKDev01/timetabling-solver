# Timetabling Problem

**Timetabling**: Problema de asignación, sujeta a restricciones, de recursos dados a objetos que se colocan en el espacio-tiempo, de manera que se satisfaga lo más cerca posible un conjunto de objetivos deseables. Un horario muestra cuándo se llevarán a cabo eventos particulares. No necesariamente implica una asignación de recursos explícita en su definición básica, aunque a menudo se realiza como parte de un proceso que considera la asignación de recursos

**Problema de Decisión vs. Problema de Optimización**:
- *Problema de Decisión*: Este problema se puede convertir en: Dado un conjunto de eventos, tiempos, aulas y restricciones, ¿existe un horario que cumpla con todas las restricciones del problema? Este es un problema de satisfacibilidad y si la respuesta es negativa entonces se sabe que es imposible crear un horario válido y se deben relajar algunas restricciones. 
- *Problema de Optimización*: Dado un conjunto de eventos, tiempos, aulas y restricciones, encuentre un horario que, siendo válido, minimice o maximice una función objetivo que este regida a la asignación de las variables de decisión. 

## Academic Timetabling

**Academic Timetabling**: Asignar cada *evento* en un momento dado (*tiempo*) del *espacio*, vinculando las *personas* correspondientes, de modo que se cumplan todas las *restricciones duras* y se optimice la *función objetivo*, para así producir un *horario* de alta calidad.

**Componentes Clave**:
- *Eventos*: Las actividades o reuniones que necesitan ser programadas. Son la unidad básica del horario. 
- *Recursos*: Los elementos necesarios para que un evento puede llevarse a cabo. Se dividen en tres subgrupos:
	- *Tiempo*: Los períodos discretos disponibles para programar eventos.
	- *Espacio*: Las locaciones físicas con capacidad y características específicas
	- *Personas*: Los participantes involucrados en los eventos, como alumnos y profesores.

**Restricciones**: Este tipo de problema de planificación de horarios de cursos están sujetos a muchas restricciones que generalmente se dividen en dos categorías: "duras" y "blandas". Las restricciones duras se aplican de manera rígida. Ejemplos:
- Ningún recurso (estudiante/profesor) puede estar asignado a más de un lugar al mismo tiempo. 
- Para cada período de tiempo, deben haber suficientes recursos (por ejemplos, aulas, supervisores, etc.) disponibles para todos los eventos programados en ese período

Las restricciones blandas son aquellas que son deseables pero no absolutamente esenciales. En la práctica es imposible satisfacer todas las restricciones blandas. Ejemplos:

- *Asignación de tiempo*: Puede ser necesario programar un curso en un período de tiempo específico. 
- *Restricciones de tiempo entre eventos*: Un curso puede necesitar ser programado antes o después de otro
- *Distribución de eventos en el tiempo*: Los estudiantes no deberían tener clases de un mismo curso en períodos consecutivos o en el mismo día
- *Coherencia*: Los profesores pueden preferir tener todas sus clases concentradas en ciertos días y tener días libres en docencia. Estas restricciones entran en conflicto con las restricciones de distribuir los eventos en el tiempo
- *Asignación de recursos*: Los profesores pueden preferir enseñar en un aula en particular, o puede ser que un examen específico deba programarse en cierta sala
- *Continuidad*: Cualquier restricción cuyo propósito principal sea garantizar que ciertas características de los horarios de los estudiantes sean constantes o predecibles. Por ejemplo: las clases de un mismo curso deberían programarse en el mismo aula o a la misma hora del día

Además, la planificación habitual de horarios de cursos involucra a muchos departamentos diferentes, donde cada departamento ofrece una multitud de cursos entre los cuales los estudiantes deben tomar algunos obligatoriamente y luego pueden elegir otros. En la mayoría de los casos, cada departamento es responsable de su propio horario y debe intentar tener en cuenta los horarios de los otros departamentos.

**Función Objetivo**: Función matemática que mide la calidad del horario. Puede definirse como maximizar las preferencias o minimizar el número de períodos. 

**Resultado Final**: Asignación completa donde cada evento tiene asignado un tiempo, un espacio y los recursos de personas necesarios, cumpliendo con todas las restricciones duras. 

## Course Timetabling

**Descripción**: Hay $q$ cursos $K_{1},K_{2},\dots,K_{q}$, y para cada curso $K_{i}$ consiste de $k_{i}$ clases. Hay $r$ grupos $S_{1},S_{2},\dots,S_{r}$, los cuales son grupos de cursos que tienen estudiantes en común. Esto significa que los cursos en $S_{i}$ deben ser programados todos en diferentes horarios. El número de períodos es $p$, y $l_{k}$ es el número máximo de clases que pueden ser programadas en el período $k$ (es decir, el número de aulas disponibles en el período $k$). 

___

**Parámetros**:

- $q:$ número de cursos
- $K_{i}:$ curso $i$-ésimo, para $i = 1,\dots,q$
- $k_{i}:$ número de clases (lecturas) que debe tener el curso $K_{i}$
- $r:$ número de grupos
- $S_{l}:$ conjunto de cursos en el grupo $l$-ésimo, para $l=1,\dots,r$. Los cursos en $S_{l}$ comparten estudiantes, por lo que sus clases no pueden solaparse
- $p:$ número de períodos de tiempo disponibles
- $l_{k}:$ número máximo de clases que pueden programarse en el período $k$ (es decir, el número de aulas disponibles en el período $k$), para $k = 1,\dots,p$
- $p_{ik}:$ indicador de preasignación. $p_{ik} = 1$ si una clase del curso $K_{i}$ debe programarse obligatoriamente en el período $k$, y $p_{ik} = 0$ si no hay preasignación
- $a_{ik}:$ indicador de disponibilidad. $a_{ik} = 1$ si una clase del curso $K_{i}$ puede programarse en el período $k$, y $a_{ik}=0$ si no está disponible (restricción de indisponibilidad)

**Variables de Decisión**: $y_{ik} \in \{0,1\}$ para $i = 1, \dots, q$ y $k = 1, \dots, p$: 

$$y_{ik} = \bigg\{ 
\begin{array}{l} 
1 & \text{si una clase del curso $K_i$ se programa en el período $k$} \\ 
0 & \text{en caso contrario} 
\end{array}$$

___

**Propuestas de Funciones Objetivo**: 

*Minimizar el Número Total de Períodos utilizados*: Reduce a un Problema de Coloración de Grafos (asignar "colores" períodos a cursos en conflicto). 

$$\min \sum_{k=1}^p z_{k}$$

donde $z_{i} = 1$ si el período $i$ tiene al menos una clase programada, y 0 en otro caso. 

*Maximizar el Número de Clases en Períodos "preferidos"*: Generaliza el problema de asignación con restricciones de conflictos, que es NP-Hard. Se definen variables $c_{ik} \in \mathbb{R}^+$ que es el peso que indica la preferencia de programar una clase de $K_{i}$ en el período $k$. 

$$\max \sum_{i=1}^q \sum_{k=1}^p c_{ik}y_{ik}$$

Incluso $c_{ik} \in \{ 0,1 \}$, maximizar las asignaciones "preferidas" es computacionalmente difícil. 

___

**Restricciones**:

- *Restricción de Número de Clases por Curso*: Cada curso debe tener exactamente el número de clases requerido. 

$$\sum_{k=1}^p y_{ik} = k_{i} \ , \ \forall i = 1, \dots, q$$

- *Restricción de Capacidad de Aulas por Período*: En cada período, el número de clases programadas no puede exceder el número de aulas disponibles.

$$\sum_{i=1}^q y_{ik} \leq l_{k} \ , \ \forall k = 1, \dots, p$$

- *Restricción de Conflictos por Grupo*: En cada período, para cada grupo, no puede haber más de una clase programada entre los cursos que comparten estudiantes.

$$\sum_{i \in S_{l}} y_{ik} \leq 1 \ , \ \forall k = 1,\dots,p \ , \ \forall l = 1,\dots,r$$

- *Restricciones de Preasignación y Disponibilidad*: Las asignaciones deben respetar las preasignaciones y las disponibilidades

$$p_{ik} \leq y_{ik} \leq a_{ik} \ , \ \forall i = 1,\dots,q \ , \ \forall k = 1, \dots, p$$

> $p_{ik} = 1 \implies y_{ik} = 1$ (clase preasignada)

> $a_{ik} = 0 \implies y_{ik} = 0$ (período no disponible)

- *Restricción de Variables Binarias*: 

$$y_{ik} \in \{ 0,1 \} \ , \ \forall i = 1, \dots, q \ , \ \forall k = 1, \dots, p$$

___

**Observaciones del Modelo Matemático**: 

- Este modelo asume que todas las clases son iguales en duración y que cada clase ocupa un período completo
- La restricción de conflictos por grupos asegura que no haya solapamientos para cursos con estudiantes en común. Alternativamente, se puede utilizar una matriz de conflictos $C_{q\times q}$, donde $c_{ij} = 1$ si los cursos $K_{i}$ y $K_{j}$ tienen estudiantes en común, y $c_{ij} = 0$ en caso contrario. En tal caso, esta restricción se reemplazaría por:

$$y_{ik} + y_{jk} \leq 1 \ , \ \forall k = 1, \dots, p \ , \ \forall i,j | c_{ij} = 1$$

- En la práctica, pueden añadirse otras restricciones, como preferencias de profesores o distribución uniforme de clases, que requerirían extensiones del modelo. 