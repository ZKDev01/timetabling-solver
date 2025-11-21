# Definiciones de Teoría de Grafos

**Fundamentos**: 

- *Grafo*: Un grafo $G$ es un par ordenado $G = (V,E)$, donde $V$ es un conjunto de vértices y $E$ es un conjunto de aristas que representan conexiones entre vértices
- *Subgrafo*: Un grafo $G' = (V',E')$ es subgrafo de $G$ si $V' \subseteq V$ y $E' \subseteq E$
- *Grafo Conexo*: Un grafo es conexo si para cada par de vértices existe al menos una arista que los conecta

**Estructura y Propiedades**:

- *Clique*: Subconjunto de vértices $C \subseteq V$ donde cada par de vértices está conectado por una arista. El tamaño del mayor clique se denota $\omega(G)$
- *Matriz de Adyacencia*: Matriz $\mathbf{A} \in \mathbb{R}^{n \times n }$ donde $A_{ij} = 1$ si existe arista entre $v_{i}$ y $v_{j}$, y 0 en otro caso 
- *Vecindad*: $\Gamma_{G}(v) = \{ u \in V : \{ v,u \} \in E \}$ es el conjunto de vértices adyacentes a $v$
- *Grado*: $\text{deg}_{G}(v) = |\Gamma_{G}(v)|$ es el número de vecinos del vértice $v$

# Definición Formal del Problema

**Problema de Coloración de Grafos**: Dado un grafo $G = (V,E)$, el problema busca asignar a cada vértice $v \in V$ un color $\text{color}(v) \in \{ 1,2,\dots,k \}$ tal que: $\text{color}(v) \neq \text{color}(u)$ para todo $\{ u,v \} \in E$ y $k$ es mínimo

**Formulación como Problema de Particiones**: Una solución $S = \{ S_{1},S_{2},\dots,S_{k} \}$ debe satisfacer:

1. *Cobertura Completa*: $\bigcup_{i=1}^k S_{i} = V$
2. *Partición Disjunta*: $S_{i} \cap S_{j} = \emptyset$ para $i \neq j$
3. *Conjuntos Independientes*: Para cada $S_{i}$, ningún par de vértices en $S_{i}$ es adyacente

**Número Cromático y Optimalidad**:

- *Número Cromático*: $_{\mathcal{X}}(G)$ es el mínimo número de colores necesarios para una coloración factible
- *Coloración Óptima*: Coloración factible que utiliza exactamente $_{\mathcal{X}}(G)$ colores 

**Complejidad Computacional**:

- *Problema* **NP-Completo**: El problema de decisión (¿puede $G$ colorearse con $k$ colores?) es NP-Completo
- *Reducción desde* **3-SAT**: El problema 3-SAT es reducible polinomialmente al problema de coloración
- *Fuerza Bruta*: Requeriría evaluar $n^n$ posibles asignaciones para $n$ vértices

# Algoritmos

## Algoritmo Greedy

**Descripción**: Opera tomando los vértices del grafo uno a uno, siguiendo un orden (que puede ser aleatorio), y asignando a cada vértice el primer color disponible. Al tratarse de un algoritmo heurístico, la solución proporcionada por este algoritmo puede no ser óptima. Sin embargo, una correcta elección del orden de los vértices para su coloración puede producir una solución óptima para cualquier grafo. Produce soluciones factibles de forma rápida, aunque estas soluciones pueden resultar "pobres" en base al número de colores que requiere el algoritmo, comparando con el número cromático del grafo. 

**Algoritmo Greedy**:
1. *Inicialización*: $S \gets \emptyset$, permutación $\pi$ de $V$
2. *Procesar Vértices*:
	1. Para $i = 1$ hasta $|\pi|$
		1. Para $j = 1$ hasta $|S|$
			1. Si $S_{j} \cup \{ \pi_{i} \}$ es un conjunto independiente:
				1. $S_{j} \gets S_{j} \cup \{ \pi_{i} \}$
				2. Salir del bucle (break)
			2. En caso contrario: 
				1. $j \gets j + 1$
		2. Si $j > |S|$:
			1. $S_{j} \gets \{ \pi_{i} \}$
			2. $S \gets S \cup S_{j}$ 

**Funcionamiento**: Se parte de la solución vacía $S = \emptyset$ y de una permutación aleatoria de vértices $\pi$. En cada iteración, el algoritmo selecciona el vértice $i$-ésimo en la permutación, $\pi_{i}$, y trata de encontrar una clase de color $S_{j} \in S$ en la cual pueda ser incluido dicho vértice. Si es posible, se añade dicho vértice a la clase de color correspondiente y el algoritmo pasa a considerar el siguiente vértice $\pi_{i+1}$. En caso contrario, se crea una nueva clase de color para el vértice considerado

**Propiedades del Algoritmo**:

- Considerando el peor caso $K_{n}$ se debe realizar una comprobación de $0 + 1 + 2 + \dots + (n-1)$ restricciones, lo que proporciona a este algoritmo una complejidad de orden $O(n^2)$ 

**Teorema**: Sea $S$ una coloración factible de un grafo $G$. Si cada clase de color $S_{i} \in S$ (para $1 \leq i \leq |S|$) se considera en su momento, y todos los vértices se introducen de uno en uno en el algoritmo Greedy, la solución resultante $S'$ será también factible, con $|S'|\leq |S|$.

**Teorema**: Sea $G$ un grafo con una solución óptima $S = \{ S_{1},\dots,S_{k} \}$ al problema de coloración de grafos, donde $k = _{\mathcal{X}}(G)$. Entonces existe al menos
$$_{\mathcal{X}}(G)! \prod_{i=1}^{_{\mathcal{X}}(G)} |S_{i}|! $$
permutaciones de los vértices donde, al aplicar el algoritmo Greedy sobre ellas, se obtendrá una solución óptima del problema.

> *Demostración*: Se deduce inmediatamente del Teorema anterior: puesto que $S$ es óptima, se puede generar una permutación adecuada de la forma descrita. Además, como las clases de color y los vértices sin clase de color asociada se pueden permutar, la fórmula indicada resulta consistente. 

**Teorema**: Sea $G$ un grafo conexo con grado máximo $\Delta(G)$, con $\Delta(G) = \max\{ \text{deg}(v):v\in V \}$, y $\text{deg}(v)$ el grado del vértice $v$. Entonces $_\mathcal{X}(G) \leq \Delta(G) + 1$

> *Demostración*: Tomando el comportamiento del algoritmo Greedy. Aquí, el vértice $i$-ésimo en la permutación $\pi$, denotado por $\pi_{i}$, será asignado a la clase de color con menor índice que no contenga a ninguno de sus vértices vecinos. Como cada vértice tiene un máximo de $\Delta(G)$ vecinos, como máximo serán necesarios $\Delta(G)+ 1$ colores para colorear de forma factible todos los vértices de $G$

## Algoritmo DSatur 

**Descripción**: Abreviatura de "Degree Saturation". Similar al algoritmo Greedy, con la salvedad de que, en este caso, la ordenación de los vértices es generada por el propio algoritmo. Así como en el algoritmo Greedy la ordenación se decidía antes de que ningún vértice fuera coloreado, en el algoritmo DSatur, el orden de los vértices se decide de forma heurística en base a las características del coloreado parcial del grafo en el momento en el que se selecciona cada uno de los vértices. 

**Definición**: Sea $\text{color}(v) = \text{NULL}$ para cualquier vértice $v \in V$ que todavía no haya sido asignado a ninguna clase de color. Dado entonces el vértice $v$, el *grado de saturación* de $v$, $\text{sat}(v)$, es el número de colores diferentes asignados a los vértices adyacentes, es decir:
$$\text{sat}(v) = | \{ \text{color}(u): u \in \Gamma(v) \land \text{color}(u) \neq \text{NULL} \} |$$

**Algoritmo DSatur**:
1. *Inicialización*: $S \gets \emptyset$, $X \gets V$ 
2. *Bucle Principal*: Mientras que $X \neq \emptyset$:
	1. Elegir $v \in X$
	2. Para $j = 1$ hasta $|S|$:
		1. Si $S_{j} \cup \{ v \}$ es un conjunto independiente:
			1. $S_{j} \gets S_{j} \cup \{ v \}$
			2. Salir del bucle (break)
		2. En caso contrario:
			1. $j \gets j + 1$
	3. Para $j > |S|$:
		1. $S_{j} \gets \{ v \}$
		2. $S \gets S \cup S_{j}$
	4. $X \gets X - \{ v \}$

**Explicación**: Aquí, se hace uso de un conjunto $X$ para definir el conjunto de vértices que todavía no se le ha sido asignado un color. Lo importante sería el paso **(2)**: el siguiente vértice en ser coloreado será aquel vértice en $X$ que presente el máximo grado de saturación, y en caso de existir más de uno, aquel con mayor grado. Si sigue existiendo más de un vértice en estas condiciones, se escoge uno de ellos aleatoriamente. Este algoritmo busca priorizar la coloración de aquellos vértices que tienen menos opciones de ser coloreados con un color ya existente (los que presentan un mayor número de restricciones). Una vez que un vértice es coloreado, se elimina del conjunto $X$ y se vuelve a comenzar el algoritmo para un nuevo vértice. 

**Propiedades**: 

- *Complejidad Temporal*: $O(n^2)$ (Grafos $K_{n}$), aunque en la práctica se puede considerar que el hecho de realizar el seguimiento de saturación de los vértices no coloreados produce un pequeño extra en cuanto a dicha complejidad. 
- **Teorema** (**Brélaz, 1979**): El algoritmo DSatur es exacto para grafos bipartitos. 
	- El algoritmo DSatur garantiza la solución óptima para grafos bipartitos, así como también para otras topologías (**Teorema**: El algoritmo DSatur es exacto para ciclos y para grafos circulares)
- **¿Por qué no garantiza óptimo?**: 

## Algoritmo RLF

**Descripción**: Abreviatura de "Recursive Largest First", funciona coloreando un grafo con un color por cada iteración del algoritmo, en vez de un vértice por iteración. En cada iteración, el algoritmo busca conjuntos de vértices independientes en el grafo, los cuales serán asociados al mismo color. Dicho conjunto independiente será eliminado del grafo, y se procederá de la misma forma con el subgrafo restante, hasta que dicho subgrafo sea vacío, en cuyo caso todos los vértices estarán asignados a algún color, produciendo así una solución factible.

**Algoritmo RLF**:
1. *Inicialización*: $S \gets \emptyset$, $X \gets V$, $Y \gets \emptyset$, $i \gets 0$
2. *Bucle Principal*: Mientras que $X \neq \emptyset$:
	1. $i \gets i  +1$
	2. $S_{i} \gets \emptyset$
	3. Mientras que $X \neq \emptyset$:
		1. Escoger $v \in X$
		2. $S_{i} \gets S_{i} \cup \{ v \}$
		3. $Y \gets Y \cup \Gamma_{X}(v)$
		4. $X \gets X - ( Y \cup \{ v \} )$
	4. $S \gets S \cup \{ S_{i} \}$
	5. $X \gets Y$
	6. $Y \gets \emptyset$

En este algoritmo se utilizan dos conjuntos:

- $X$: contiene los vértices que no han sido coloreados y que se pueden añadir a la clase $S_{i}$, sin provocar ningún conflicto (es decir, una situación en la que, dado $u,v \in V$ tales que $\{ u,v \} \in E$, se tiene que $\text{color}(u) = \text{color}(v)$)
- $Y$: contiene a los vértices que no han sido coloreados y que no pueden ser añadidos de forma factible por $S_{i}$ (es decir, que no pueden ser coloreados por el color $i$).

*Observaciones*:

- Al inicio del algoritmo: $X = V$ e $Y = \emptyset$ 
- Al finalizar el algoritmo $X = Y = \emptyset$ (todos los vértices han sido coloreados)
- Entre los pasos **(4)** y **(8)** del algoritmo, se selecciona un vértice $v \in X$ y se añade al conjunto $S_{i}$ (se colorea con el color $i$). A continuación se mueven al conjunto $Y$ todos los vértices vecinos a $v$ en el subgrafo inducido por $X$, pues estos no pueden ser coloreados con el color $i$. Se colorea al resto de elementos de $X$ con el color $i$, y, por último, se vuelve a mover todos los elementos de $Y$ a $X$ para volver a comenzar con el primer paso del algoritmo y continuar con la clase de color $S_{i + 1}$ en caso de que fuera necesario

**Propiedades**:

- *Complejidad Temporal*: $O(n^3)$
- **Teoremas**: El algoritmo RLF es exacto para grafos: bipartitos, cíclicos y circulares

## Comparación Empírica de Greedy, DSatur Y RLF

Se generaron 50 grafos aleatorios para distintos números de vértices y se muestran los resultados con la coloración promedio + desviación estándar: coloración para $n$ vértices de $\mu + \sigma$ colores (Tabla: $n | \mu + \sigma$)

**Definición** (**Grafo Erdos-Renyi**): Un grafo aleatorio, denotado como $G_{n,p}$ es un grafo comprendiendo $n$ vértices en donde cada par de vértices es adyacente con probabilidad $p$. En consecuencia, los grados de los vértices en un grafo aleatorio siguen una distribución binomial, es decir, $\text{deg}(v) \sim \text{Binomial}(n-1,p)$ 