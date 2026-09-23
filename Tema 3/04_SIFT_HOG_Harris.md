# Detectores y Descriptores Locales

## Conceptos Clave
*   **Keypoint (Punto de interés):** Punto distintivo, estable y repetible (ej: esquinas).
*   **Descriptor:** Vector numérico que describe la apariencia local alrededor del keypoint.
*   **Invarianza:** Propiedad deseada. Que el descriptor no cambie ante rotación, escala, iluminación.

---

## 1. Harris Corner Detector
Detecta esquinas basándose en que la intensidad cambia en **todas** las direcciones.
*   Analiza la matriz de autokorrelación de gradientes.
*   Si los dos autovalores $(\lambda_1, \lambda_2)$ son grandes $\to$ Esquina.
*   Si uno es grande y otro pequeño $\to$ Borde.
*   Si ambos son pequeños $\to$ Región plana.

---

## 2. SIFT (Scale-Invariant Feature Transform)
Algoritmo patentado (Lowe, 2004) para detectar y describir características locales. Invariante a escala y rotación.

### Etapas de SIFT
1.  **Detección de Extremos en Espacio de Escala:**
    *   Usa **DoG (Difference of Gaussians)** para aproximar el Laplaciano.
    *   Busca máximos/mínimos en vecindad 3x3x3 (espacio $x, y, \sigma$).
2.  **Localización de Keypoints:** Refinamiento sub-píxel y eliminación de bordes (usando Hessiana).
3.  **Asignación de Orientación:**
    *   Calcula gradientes en una vecindad.
    *   Crea histograma de orientaciones ponderado.
    *   Asigna la dirección del pico principal para lograr **invarianza a rotación**.
4.  **Descriptor SIFT:**
    *   Toma una ventana de 16x16 alrededor del keypoint.
    *   La divide en 4x4 celdas.
    *   Calcula histograma de gradientes (8 direcciones) para cada celda.
    *   **Dimensión final:** $4 \times 4 \times 8 = 128$ valores.

---

## 3. HOG (Histogram of Oriented Gradients)
Descriptor denso (no busca keypoints, se aplica en rejilla). Muy usado para **detección de peatones**.

### Proceso HOG
1.  Calcular gradientes (magnitud y dirección).
2.  Dividir imagen en **Celdas** (ej: 8x8 píxeles).
3.  Calcular histograma de gradientes (9 bins 0-180°) para cada celda.
4.  Agrupar celdas en **Bloques** (ej: 2x2 celdas) y **Normalizar** el histograma dentro del bloque.
    *   *Importante:* La normalización combate cambios de iluminación y contraste.
5.  Vector final: Concatenación de todos los bloques normalizados.

### Comparativa Rápida
| Descriptor | Uso Principal | Invarianza |
| :--- | :--- | :--- |
| **Harris** | Esquinas | Rotación (No escala) |
| **SIFT** | Matching objetos | Escala, Rotación, Iluminación |
| **HOG** | Peatones/Formas | Pequeñas deformaciones |
