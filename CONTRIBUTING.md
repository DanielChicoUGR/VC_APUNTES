# Guía de Contribución: Visión por Computador

¡Bienvenido! Este repositorio es un proyecto colaborativo abierto para estudiantes de la asignatura **Visión por Computador**. El objetivo es construir unos apuntes rigurosos, visuales y completos combinando las explicaciones de clase con la literatura canónica.

---

## 1. Flujo de Trabajo con Git (GitHub Flow)

Para evitar conflictos y mantener el repositorio siempre funcional:

1. **Nunca trabajes directamente sobre la rama `main`:**
   ```bash
   git checkout -b feature/tema2-canny-mejoras
   ```
2. **Haz commits claros y descriptivos** (usando *Conventional Commits*):
   * `feat: añadir explicación matemática de RANSAC en Tema 3`
   * `fix: corregir subíndice en fórmula de convolución en Tema 2`
   * `docs: añadir examen de convocatoria ordinaria 2025 resuelto`
3. **Sube tu rama y abre una Pull Request (PR):**
   ```bash
   git push origin feature/tema2-canny-mejoras
   ```

---

## 2. Estándares de Formato y Estilo en Obsidian

Para mantener la estética limpia y la compatibilidad con todos los visores:

### A. Fórmulas Matemáticas (KaTeX / LaTeX)
* Escribe siempre las fórmulas en formato estándar de KaTeX:
  * En línea: `$G = H * F$`
  * En bloque:
    $$ G[i, j] = \sum_{u=-k}^{k} \sum_{v=-k}^{k} H[u, v] F[i-u, j-v] $$
* **Leyenda obligatoria:** Tras cada fórmula principal, incluye un callout explicando qué representa cada variable:
  ```markdown
  > [!info] Leyenda Matemática
  > - $G[i, j]$: Píxel de la imagen resultante.
  > - $H$: Máscara o kernel de convolución.
  ```

### B. Diagramas Visuales (Mermaid)
* **Evita capturas de pantalla de baja calidad.** En su lugar, usa diagramas en código `mermaid`:
  ````markdown
  ```mermaid
  graph LR
      A[Imagen Original] --> B(Filtro Gaussiano)
      B --> C[Imagen Suavizada]
  ```
  ````

### C. Bloques de Información (Callouts de Obsidian)
Usa los bloques nativos para destacar información relevante:
* `> [!info]` para definiciones clave o leyendas.
* `> [!tip]` para consejos de examen o trucos prácticos.
* `> [!warning]` para errores frecuentes o casos donde falla un algoritmo.

---

## 3. ¿Qué contenido puedes aportar?

* 📝 **Ampliación de temas:** Añadir explicaciones más claras, demostraciones paso a paso o intuiciones físicas.
* 🧪 **Código reproducible:** Fragmentos breves y claros en Python con OpenCV o NumPy.
* 🎯 **Exámenes y ejercicios resueltos:** Preguntas teóricas de años anteriores explicadas con rigor.
* 📚 **Nuevas referencias:** Artículos clave o tutoriales recomendados.
