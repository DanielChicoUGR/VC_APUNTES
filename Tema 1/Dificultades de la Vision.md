# Dificultades de la Visión por Computador

A pesar de que para los humanos ver parece fácil, es un problema computacionalmente muy complejo. Szeliski (2022) menciona que inicialmente (en los 60s) se subestimó enormemente su dificultad.

>[!failure] La Brecha Semántica (Semantic Gap)
> El ordenador solo "ve" una matriz gigante de números (valores de intensidad/color entre 0 y 255). Nosotros percibimos conceptos holísticos (ej: "un gato"). No hay una traducción directa y simple entre esos números y el concepto.

## Desafíos Principales
1.  **Pérdida de información (3D $\rightarrow$ 2D)**: Al proyectar el mundo 3D en una imagen plana, se pierde la profundidad. Es un problema "mal planteado" (ill-posed) con múltiples soluciones posibles.
2.  **Variación del Punto de Vista**: Al mover la cámara, todos los píxeles de la imagen cambian drásticamente, aunque el objeto sea el mismo.
3.  **Iluminación**: La intensidad de un píxel depende de la luz, la reflectancia del material y la geometría. Es difícil separar estos factores (ej: ¿es una mancha oscura o una sombra?).
4.  **Deformación y Oclusión**: Los objetos no rígidos cambian de forma. Los objetos pueden estar parcialmente tapados.
5.  **Desorden de fondo (Background Clutter)**: Los objetos de interés pueden camuflarse con un fondo complejo.
6.  **Variación Intra-clase**: Una "silla" puede tener infinitas formas, colores y tamaños, pero todas son sillas.
7.  **Ambigüedad Local**: Mirando a través de una "ventana" pequeña (apertura), es imposible saber qué es el objeto globalmente.
8.  **Ilusiones Ópticas**: El sistema visual humano usa "atajos" y conocimiento previo que a veces fallan; la visión artificial debe lidiar con ambigüedades similares.
