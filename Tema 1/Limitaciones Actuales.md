# Limitaciones Actuales y Desafíos

A pesar de los avances increíbles (superando a humanos en tareas específicas), la visión por computador actual tiene limitaciones serias:

>[!warning] Falta de "Sentido Común"
> Como dice Yann LeCun: "No tenemos máquinas con sentido común".
> - Las máquinas ejecutan soluciones, no resuelven problemas de forma general.
> - Carecen de un modelo mental robusto del mundo físico (física intuitiva).
> - Pueden generar vídeos donde los objetos aparecen/desaparecen mágicamente o interactúan de forma imposible.

## Principales Limitaciones
1.  **Dependencia de Datos (Data Hungry)**:
    - Los modelos de Deep Learning necesitan miles/millones de ejemplos anotados.
    - Un humano aprende a reconocer un objeto con muy pocos ejemplos.
    - Coste energético computacional muy alto.
2.  **Cajas Negras (Black Box)**:
    - Es difícil interpretar por qué una red neuronal toma una decisión.
    - Dificulta la depuración y la confianza en sistemas críticos (medicina, conducción).
3.  **Fragilidad y Contexto**:
    - **Ataques Adversarios**: Cambios imperceptibles en una imagen (ruido) o pegatinas en una señal de tráfico pueden engañar totalmente al modelo (ej: ver una señal de STOP como límite de velocidad).
    - Los modelos a menudo se basan en texturas o correlaciones espurias, no en la forma o el concepto global ("ver el todo").
4.  **Problemas Éticos y Sesgos**:
    - Los sistemas son "tan buenos como los datos con los que se entrenan".
    - Sesgos raciales o de género en reconocimiento facial.
    - Problemas de privacidad y vigilancia masiva.
