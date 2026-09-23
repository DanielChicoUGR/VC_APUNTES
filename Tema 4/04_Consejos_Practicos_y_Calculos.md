# 04. Consejos Prácticos y Cálculos

## Cálculo del Tamaño de Salida
Dada una entrada de tamaño $N$, un filtro de tamaño $F$, un padding $P$ y un una entrada de tamaño ￼￼, un filtro de tamaño ￼￼, un padding ￼￼stride $S$, el tamaño de salida $O$ es:

$$ O = \frac{N - F + 2P}{S} + 1 $$ 

> **Leyenda:**
> *   $N$: Dimensión de la entrada (ancho o alto).
> *   $F$: Tamaño del filtro/kernel.
> *   $P$: Padding (píxeles añadidos al borde).
> *   $S$: Stride (paso de desplazamiento del filtro).
> *   $O$: Dimensión de la salida. (Si no es entero, generalmente se toma el suelo `floor`).

**Ejemplo:** Entrada 224x224, Filtro 7x7, Stride 2, Padding 3.
$$ O = \frac{224 - 7 + 2(3)}{2} + 1 = \frac{223}{2} + 1 = 111.5 + 1 \approx 112 $$ 

## Número de Parámetros
Para calcular el tamaño del modelo (pesos):

1.  **Capa Convolucional:**
    $$ \text{Params} = (F \times F \times C_{in} + 1) \times K $$ 
    > *   $F$: Tamaño espacial del filtro.
    > *   $C_{in}$: Número de canales de entrada (profundidad).
    > *   $1$: Bias.
    > *   $K$: Número de filtros (canales de salida).

2.  **Capa Fully Connected:**
    $$ \text{Params} = (N_{in} + 1) \times N_{out} $$ 
    > *   $N_{in}$: Número de neuronas de entrada.
    > *   $N_{out}$: Número de neuronas de salida.

## Transfer Learning (Aprendizaje por Transferencia)
Estrategia vital cuando se tienen pocos datos.
1.  Tomar una red pre-entrenada en un dataset grande (ej. ImageNet).
2.  **Feature Extraction:** Congelar los pesos de la red base (backbone) y entrenar solo un nuevo clasificador (capas FC) al final para la nueva tarea.
3.  **Fine-tuning:** Descongelar algunas o todas las capas de la red base y re-entrenar con una tasa de aprendizaje muy baja para adaptar los pesos a la nueva tarea.

## Diagnóstico de Curvas de Aprendizaje (Loss Curves)

*   **Overfitting (Sobreajuste):** Error de entrenamiento baja mucho, pero error de validación se estanca o sube. Existe un gran "gap" entre ambas.
    *   *Solución:* Regularización (Dropout, Data Augmentation), más datos, modelo más simple.
*   **Underfitting (Subajuste):** Ambos errores son altos. El modelo no aprende.
    *   *Solución:* Modelo más complejo, entrenar más tiempo, ajustar learning rate.
*   **Buen ajuste:** Ambas curvas bajan y convergen cerca.
*   **Validación mejor que Training:** Puede ocurrir por Dropout (activo en train, inactivo en val) o porque los datos de validación son "más fáciles"/menos diversos.

## Problemas Comunes
*   **Vanishing Gradient (Desvanecimiento):** En redes profundas, el gradiente se vuelve muy pequeño al retroceder hacia las primeras capas, impidiendo que aprendan.
    *   *Solución:* Conexiones residuales (ResNet), Batch Normalization, funciones ReLU.
*   **Exploding Gradient:** El gradiente crece demasiado causando inestabilidad (NaN).
    *   *Solución:* Gradient Clipping.
*   **Dead ReLU:** Neuronas ReLU que quedan en la zona negativa y siempre devuelven 0, "muriendo" y dejando de aprender.
    *   *Solución:* Bajar learning rate, usar Leaky ReLU.
