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

## 2. Estándares de Formato y Estilo: Obsidian (Apuntes) vs. GitHub (PRs y Chat)

Para mantener la estética limpia y garantizar que el contenido se renderice correctamente en cada plataforma:

> [!IMPORTANT]
> **Separación de Formatos según el Destino:**
> * **Apuntes del Vault (`Tema 1/` a `Tema 5/`):** Usan la sintaxis nativa de **Obsidian Callouts** (`[!info]`, `[!tip]`, `[!warning]`, `[!example]`, etc.).
> * **Pull Requests (PRs), Issues y respuestas de Chat:** Deben usar **exclusivamente GitHub Flavored Markdown (GFM) Alerts** en mayúsculas (`[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`). Queda prohibido usar callouts de Obsidian como `[!info]` en PRs o chat porque se visualizan rotos en GitHub.

### A. Fórmulas Matemáticas (KaTeX / LaTeX)
* Escribe siempre las fórmulas en formato estándar de KaTeX:
  * En línea: `$G = H * F$`
  * En bloque:
    $$ G[i, j] = \sum_{u=-k}^{k} \sum_{v=-k}^{k} H[u, v] F[i-u, j-v] $$
* **Leyenda obligatoria:** Tras cada fórmula principal, incluye una leyenda explicando qué representa cada variable (en apuntes se usa callout `> [!info] Leyenda Matemática`; en GitHub / PRs se usa `> [!NOTE]` seguido de `> **Leyenda Matemática**`):
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

### C. Bloques de Información (Callouts de Obsidian solo en apuntes)
En los archivos de apuntes del Vault, usa los bloques nativos de Obsidian:
* `> [!info]` para definiciones clave o leyendas matemáticas.
* `> [!tip]` para consejos de examen o trucos prácticos.
* `> [!warning]` para errores frecuentes o casos donde falla un algoritmo.
* `> [!example]` para ejemplos resueltos paso a paso.

*(Nota: Para el cuerpo de una Pull Request o comentarios en GitHub, reemplázalos por su equivalente GFM: `[!NOTE]`, `[!TIP]`, `[!WARNING]`, etc.)*

---

## 3. ¿Qué contenido puedes aportar?

* 📝 **Ampliación de temas:** Añadir explicaciones más claras, demostraciones paso a paso o intuiciones físicas.
* 🧪 **Código reproducible:** Fragmentos breves y claros en Python con OpenCV o NumPy.
* 🎯 **Exámenes y ejercicios resueltos:** Preguntas teóricas de años anteriores explicadas con rigor.
* 📚 **Nuevas referencias:** Artículos clave o tutoriales recomendados.
* 📚 **Mejoras en la busqueda semántica:** Mejoras en los scripts de consulta, descarga o instrucciones para el agente.
