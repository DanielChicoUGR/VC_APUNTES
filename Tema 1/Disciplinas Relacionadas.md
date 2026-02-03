# Disciplinas Relacionadas y Definiciones

>[!important] Relación con otras áreas
>La Visión por Computador es una disciplina intrínsecamente multidisciplinar que se solapa con:
>- **Inteligencia Artificial (IA)**: Marco general.
>- **Machine Learning (Aprendizaje Automático)** y **Deep Learning**: Herramientas fundamentales para aprender de los datos visuales.
>- **Robótica**: Necesaria para interactuar con el mundo real.
>- **Procesamiento de Señal / Imágenes**: Operaciones base.
>- **Física (Óptica)**, **Neurociencia**, **Psicología Cognitiva**, **Matemáticas (Geometría, Estadística)**.

## Visión por Computador vs. Gráficos por Computador
Son problemas inversos:
- **Computer Vision (Análisis)**:  Entrada: Imágenes $\rightarrow$ Salida: Modelo 3D / Información semántica.
- **Computer Graphics (Síntesis)**: Entrada: Modelo 3D $\rightarrow$ Salida: Imágenes.

## Visión vs. Procesamiento de Imágenes
- **Procesamiento de Imágenes**: Operaciones de "bajo nivel" donde tanto la entrada como la salida son imágenes (ej: eliminar ruido, aumentar contraste, afilar bordes).
- **Visión por Computador**: Busca el **entendimiento** automático. La salida es una interpretación o medición del mundo (ej: reconocer un objeto, reconstruir la geometría 3D).

## Niveles de Procesamiento
Diferentes autores clasifican los procesos en:
1.  **Bajo Nivel (Early Vision)**: Operaciones con píxeles. Filtrado, detección de bordes, texturas. Poca semántica.
2.  **Nivel Medio (Mid-level)**: Agrupación y segmentación. Extraer atributos (bordes, esquinas) y contornos. Separar objetos del fondo.
3.  **Alto Nivel (High-level)**: "Dar sentido". Reconocimiento de objetos, clasificación, análisis de escenas. Imita la cognición humana.
