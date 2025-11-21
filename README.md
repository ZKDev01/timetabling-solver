# Timetabling-Solver

## 📋 Descripción General

**Timetabling-Solver** es un proyecto integral de investigación y desarrollo que aborda el **University Course Timetabling Problem** (Problema de Planificación de Horarios Universitarios), un problema computacionalmente complejo de la clase **NP-Completo**. 

El proyecto aplica conocimientos teóricos y prácticos de Diseño y Análisis de Algoritmos, siguiendo un ciclo completo que va desde la formalización matemática hasta la implementación y evaluación experimental de algoritmos de solución.

---

## 🎯 Objetivo del Proyecto

**Objetivo Fundamental**: Aplicar de manera integral los conocimientos teóricos y prácticos de Diseño y Análisis de Algoritmos mediante:

- Elección de un problema computacionalmente difícil (NP-Duro/NP-Completo)
- Ciclo completo de análisis: formalización matemática $\to$ diseño $\to$ implementación $\to$ evaluación empírica

**Problema Elegido**: University Course Timetabling Problem (UCTP)

### Habilidades Críticas a Desarrollar

- Modelado y formalización de problemas complejos
- Análisis riguroso de complejidad computacional
- Diseño de algoritmos para problemas complejos (aproximación, heurísticas)
- Implementación de software de calidad
- Evaluación experimental y análisis comparativo de rendimiento
- Comunicación técnica mediante informes y documentación

---

## 📁 Estructura del Proyecto

```
timetabling-solver/
├── requirements.txt               # Dependencias del proyecto
├── todo.md                        # Tareas pendientes y en progreso
│
├── src/                          # Código fuente principal
│   ├── data_structures.py        # Estructuras: GraphInstance, TimetablingInstance
│   ├── algorithms/               # TODO: Implementación de algoritmos
│   ├── generators/               # TODO: Generadores de instancias de prueba
│   └── evaluation/               # TODO: Evaluación y análisis experimental
│
├── summary/                      # Documentación teórica
│   ├── timetabling.md            # Formalización del problema de Timetabling
│   ├── coloring.md               # Teoría de grafos y coloración
│   └── reduction.md              # Reducción polinomial a Graph Coloring
│
└── labs/                         # TODO: Experimentos y pruebas
```

---

## 📊 Estructura Teórica

### Conceptos Clave

**Graph Coloring Problem**: Asignar colores $\{1, 2, \ldots, k\}$ a vértices de un grafo $G = (V,E)$ tal que:
- Vértices adyacentes tienen colores distintos
- $k$ es mínimo (número cromático $\chi(G)$)

**University Course Timetabling**: Asignar $q$ cursos a $p$ períodos de tiempo, respetando:
- Cada curso tiene $k_i$ clases
- Cursos conflictivos (comparten estudiantes) no pueden asignarse al mismo período
- Cada período tiene capacidad limitada de aulas $l_k$

**Reducción Polinomial**: El problema de Timetabling se transforma en una instancia equivalente de Graph Coloring con restricciones de capacidad.

---

## 📚 Documentación de Referencia

- `summary/timetabling.md`: Definición formal y modelo matemático del problema
- `summary/coloring.md`: Teoría de grafos, algoritmos de coloración y sus propiedades
- `summary/reduction.md`: Demostración de la reducción polinomial

---

## 🚀 Inicio Rápido

### Instalación

```bash
# Clonar repositorio y crear/activar el entorno virtual
python -m venv ".env"
.\.env\Scripts\Activate.ps1  # Windows
source .env/bin/activate      # Linux

# Instalar dependencias
pip install -r requirements.txt
```