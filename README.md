# 🚀 Algoritmo para Conjunto Independiente Máximo en Grafos Outerplanar

Este repositorio implementa un algoritmo eficiente para encontrar el Conjunto Independiente Máximo (MIS) en grafos outerplanar, junto con una implementación de fuerza bruta para comparación.

## 📌 Características clave

- **Algoritmo especializado**: Encuentra el MIS en grafos outerplanar en tiempo polinomial
- **Comparación con fuerza bruta**: Incluye implementación de referencia para validación
- **Análisis de tiempos**: Mide el rendimiento de cada etapa del algoritmo
- **Soporte para grafos grandes**: Maneja componentes conectados eficientemente
- **Módulos separados**:
  - `main.py`: Implementación principal del algoritmo
  - `test.py`: Pruebas y métricas de rendimiento

## 🛠 Requisitos

- Python 3.6+
- NetworkX (`pip install networkx`)

## 🏃‍♂️ Cómo ejecutar

1. Clona el repositorio:

   ```bash
   git clone https://github.com/daniellg01/outerplanar-mis.git
   cd outerplanar-mis
   ```

2. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el código principal:

   ```bash
   python main.py
   ```

4. Para pruebas y métricas:
   ```bash
   python test.py
   ```

## 📊 Resultados esperados

### En main.py:

- Tiempos de ejecución para cada componente del algoritmo
- Tamaño del conjunto independiente máximo encontrado
- Nodos que forman parte del conjunto
- Comparación con el resultado de fuerza bruta

### En test.py:

- Pruebas automatizadas con diferentes grafos
- Métricas detalladas de rendimiento
- Comparación de tiempos entre el algoritmo y fuerza bruta
- Validación de resultados

## 🧪 Grafos de prueba incluidos

El script prueba el algoritmo con varios grafos:

- Caminos (Path graphs)
- Ciclos (Cycle graphs)
- Estrellas (Star graphs)
- Grafos escalera (Ladder graphs)
- Árboles binarios
- Grafos con combinaciones de las características anteriores

## ⏱ Análisis de rendimiento

El algoritmo desglosa su tiempo de ejecución en:

1. Descomposición en componentes conectados
2. Reducción y fill-in para hacer el grafo chordal
3. Identificación de cliques
4. Construcción del árbol de cliques
5. Programación dinámica
6. Reconstrucción de la solución

## 📚 Teoría detrás del algoritmo

El algoritmo aprovecha las propiedades de los grafos outerplanar:

1. Son K₄-minor-free y K₂,₃-minor-free
2. Tienen ancho arbóreo acotado
3. Pueden hacerse chordales añadiendo aristas adecuadas (fill-in)

La implementación sigue estos pasos:

1. Descomponer el grafo en componentes conectados
2. Para cada componente:
   - Aplicar reducción para hacerlo chordal
   - Encontrar todas las cliques maximales
   - Construir el árbol de cliques
   - Usar programación dinámica sobre el árbol

## 📈 Comparación con fuerza bruta

El script incluye una implementación de fuerza bruta (O(2ⁿ)) para:

- Validar los resultados del algoritmo principal
- Demostrar la ventaja de tiempo en grafos grandes

## 📝 Licencia

Este proyecto está bajo la licencia MIT.

---

✨ **Contribuciones son bienvenidas!** Si encuentras algún problema o tienes sugerencias, por favor abre un issue.
