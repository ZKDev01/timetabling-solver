# Reducción: Course Timetabling Problem a un Graph Coloring Problem

La reducción del problema de Course Timetabling a un problema de Coloración de Grafos, se construye formalmente de la siguiente manera: transformar una instancia del problema de planificación de horarios en una instancia de coloración de grafos, donde los colores representan períodos de tiempo y las restricciones de timetabling se capturan mediante la estructura del grafo y restricciones adicionales de capacidad. 

___

**Construcción del Grafo** $G = (V,E)$

**Vértices** ($V$)

- *Vértices de clases*: Para cada curso $K_{j}$ (con $j=1,\dots,q$) y cada una de sus $k_{j}$ clases, se crea un vértice $m_{j,i}$, donde $i=1,\dots,k_{j}$. Así, el conjunto de vértices de clases es:
$$V_{1} = \{ m_{j,i} | j = 1, \dots, q; i = 1,\dots,k_{j} \}$$
- *Vértices de períodos*: Para cada período $k$ (con $k = 1,\dots,p$), se crea un vértice $t_{k}$. Así, el conjunto de vértices de períodos es:

$$V_{2} = \{ t_{k} | k=1,\dots,p \}$$

- *Conjunto Total de Vértices*: $V = V_{1} \cup V_{2}$

**Aristas** ($E$): Las aristas se definen para capturar las restricciones del problema de timetabling:

- *Aristas dentro de un curso*: Para cada curso $K_{j}$, se añade un conjunto de aristas entre todos los vértices $m_{j,1},m_{j,2},\dots,m_{j,k_{j}}$. Esto asegura que todas las clases de un mismo curso se asignen a períodos diferentes. Formalmente:

$$E_{1} = \{ (m_{j,i},m_{j,i'}) | j = 1, \dots, q ; i, i' = 1,\dots,k_{j}; i \neq i' \}$$

- *Aristas por conflictos entre cursos*: Para cada par de cursos $K_{ j 1 }$ y $K_{j 2}$ que son conflictivos (es decir, comparten estudiantes por estar en al menos un grupo común $S_{l}$), se añaden aristas entre todo par de vértices de $K_{j 1}$ y $K_{j 2}$. Esto asegura que clases de cursos conflictivos no se asignen al mismo período. Formalmente: 

$$E_2 = \{ (m_{j 1, i_{1}}, m_{j 2, i_{2}}) | K_{j 1} \text{ y } K_{j 2} \text{ son conflictivos}; i_{1} = 1,\dots,k_{j 1}; i_{2} = 1,\dots,k_{j 2}\}$$

Alternativamente, si se usa la matriz de conflictos $C$, esto se aplica para todo par $j 1, j 2$ con $c_{j 1, j 2} = 1$

- *Aristas entre períodos*: Se añade un conjunto de aristas entre todos los vértices $t_{1},t_{2},\dots,t_{p}$. Esto fuerza a que cada período reciba un color único, ya que los vértices $t_{k}$ deben tener colores distintos. Formalmente:

$$E_{3} = \{ (t_{k}, t_{k}') | k, k' = 1, \dots, p ; k \neq k' \}$$

- *Aristas por no-disponibilidades*: Si una clase $m_{j,i}$ debe programarse en el período $k$, se añaden aristas entre $m_{j,i}$ y todos los vértices $t_{k'}$ para $k' \neq k$. Esto fuerza a que la clase solo pueda asignarse al período $k$. Formalmente. 

$$E_{4} = \{ (m_{j,i},t_{k'}) | \text{la clase $m_{j,i}$ debe asignarse al período $k$, y $k' \neq k$} \} $$

- *Conjunto Total de Aristas*: $E = E_{1} \cup E_{2} \cup E_{3} \cup E_{4}$

___

**Problema de Coloración Resultante**: El problema de coloración asociado consiste en asignar colores a los vértices de $G$ desde el conjunto de colores $\{ 1,2,\dots,p \}$ (donde cada color $k$ representa el período $k$), sujeto a las siguientes condiciones:
- *Restricción de coloración estándar*: Vértices adyacentes deben tener colores diferentes. Es decir, para toda arista $(u,v) \in E$, los colores de $u$ y $v$ deben ser distintos
- *Restricción de capacidad de color*: Para cada color $k$ (período $k$), el número de vértices de clases (es decir, vértices en $V_{1}$) asignados al color $k$ no puede exceder $l_{k}$ (el número de aulas disponibles en el período $k$). Esta restricción captura la limitación de recursos en el Timetabling

___

**Correspondencia entre Soluciones**: Una asignación válida de colores en $G$ que satisface ambas condiciones corresponde directamente a una solución factible del problema de timetabling:

- Si un vértice de clase $m_{j,i}$ tiene color $k$, entonces la clase correspondiente se programa en el período $k$
- La variable $y_{ik}$ del modelo de timetabling se define como 1 si existe al menos un vértice $m_{j,i}$ con color $k$, y 0 en caso contrario. Debido al conjunto de aristas por curso, cada curso $K_{j}$ tendrá exactamente $k_{j}$ vértices con colores distintos, lo que asegura que $\sum_{k=1}^p y_{ik} = k_{j}$

Tener en cuenta que:

- Las aristas de conflicto aseguran que cursos con estudiantes comunes no comparten períodos, cumpliendo la restricción de los grupos. 
- Las aristas con vértices de período manejan las preasignaciones y no disponibilidades. 
- La restricción de capacidad por color asegura que en cada período que no exceda el número de aulas disponibles. 

___

**Observaciones**:

- Esta reducción muestra que el problema de Course Timetabling es NP-Completo, ya que el problema de coloración de grafos es NP-Completo y la construcción puede realizarse en tiempo polinomial. 
- La restricción de capacidad de color no es parte del problema de coloración estándar, pero es esencial para capturar las limitaciones del problema de Timetabling. Sin ella, la reducción no sería completa. Esto implica que, si no hay restricciones de capacidad ($l_{k}$ es suficientemente grande), el problema se reduce a un problema de coloración estándar.  

Asociar a cada clase $l_{i}$ de cada curso $K_{i}$ un vértice $m_{ij}$; para cada curso $K_{i}$ introducir una camarilla entre los vértices $m_{ij}$ (para $i = 1,\dots,q$). Introducir todas las aristas entre la camarilla para $K_{i}$ y la camarilla para $K_{j}$ siempre que $K_{i}$ y $K_{j}$ estén en conflicto 