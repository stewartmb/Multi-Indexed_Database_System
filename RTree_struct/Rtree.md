# Documentación - R Tree
## Índices espaciales
Un índice espacial es una estructura de datos que permite realizar consultas eficientes sobre datos espaciales (geográficos).
Permite búsquedas como:
- Puntos dentro de un área
- Objetos que se intersectan
- Encontrar los vecinos más cercanos (K-NN).

## ¿Qué es un índice R-Tree?
El R-Tree es un índice espacial jerárquico que organiza objetos geométricos (puntos, líneas, polígonos) mediante rectángulos mínimos (MBR) para facilitar búsquedas espaciales eficientes.
- Cada rectángulo representa un nodo o entrada en el árbol.
- Los nodos internos agrupan elementos espacialmente cercanos para mejorar la eficiencia de búsqueda.

El R-Tree tiene más características:
- Es un árbol balanceado similar a un B-Tree.
- Garantiza que puntos cercanos se almacenen en lo posible en la misma página de datos osubárbol.
- Regiones de páginas jerárquicamente organizadas siempre deben estar contenidas completamente en la región de su padre.
- Estructura dinámica: operaciones de inserción y borrado eficientes O(log n)
- Permite buscar objetos espaciales en una área determinada.
