# Guía de Mantenimiento y Estilo: Visión por Computador

Este repositorio es un vault personal para estudiar **Visión por Computador**. El objetivo es mantener apuntes rigurosos, visuales y completos, combinando las explicaciones de clase con la literatura canónica y tarjetas de autoevaluación LearnKit.

---

## 1. Flujo de Trabajo Personal con Git

1. **Revisa el estado y el diff antes de editar y de hacer commit.** Conserva los cambios pendientes que no pertenezcan al trabajo actual.
2. **Puedes trabajar en la rama actual.** Las ramas adicionales y las Pull Requests son opcionales.
3. **Selecciona explícitamente los archivos del encargo para el commit.** Evita añadir indiscriminadamente apuntes, plugins, PDFs o ajustes locales que ya estuvieran modificados.
4. **Haz commits claros y descriptivos** (usando *Conventional Commits*):
   * `feat: añadir explicación matemática de RANSAC en Tema 3`
   * `fix: corregir subíndice en fórmula de convolución en Tema 2`
   * `docs: añadir examen de convocatoria ordinaria 2025 resuelto`
5. **Publica cambios solo cuando se solicite.** Un commit local no implica hacer push ni abrir una PR.

---

## 2. Estándares de Formato y Estilo: Obsidian (Apuntes) vs. GitHub (PRs y Chat)

Para mantener la estética limpia y garantizar que el contenido se renderice correctamente en cada plataforma:

> [!IMPORTANT]
> **Separación de Formatos según el Destino:**
> * **Apuntes del Vault (`Tema 1/` a `Tema 5/`):** Usan la sintaxis nativa de **Obsidian Callouts** (`[!info]`, `[!tip]`, `[!warning]`, `[!example]`, etc.) y **enlaces nativos de Obsidian (Wikilinks `[[...]]`)**.
> * **Pull Requests (PRs), Issues y respuestas de Chat:** Deben usar **exclusivamente GitHub Flavored Markdown (GFM) Alerts** en mayúsculas (`[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`) y enlaces estándar de Markdown. Queda prohibido usar callouts o wikilinks de Obsidian en PRs o chat porque se visualizan rotos en GitHub.

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

* Para tarjetas LearnKit, los símbolos matemáticos pueden definirse en la pregunta, respuesta o campo `I`, sin repetir obligatoriamente un callout. La teoría conserva la leyenda obligatoria de la sección A.

### B. Diagramas Visuales (Mermaid)
* **Evita capturas de pantalla de baja calidad.** En su lugar, usa diagramas en código `mermaid`:
  ````markdown
  ```mermaid
  graph LR
      A[Imagen Original] --> B(Filtro Gaussiano)
      B --> C[Imagen Suavizada]
  ```
  ````
* En ejercicios de reconocimiento, localización u oclusión visual, usar imágenes cuando formen parte del ejercicio, reutilizando recursos del vault y citando su procedencia.

### C. Bloques de Información (Callouts de Obsidian solo en apuntes)
En los archivos de apuntes del Vault, usa los bloques nativos de Obsidian:
* `> [!info]` para definiciones clave o leyendas matemáticas.
* `> [!tip]` para consejos de examen o trucos prácticos.
* `> [!warning]` para errores frecuentes o casos donde falla un algoritmo.
* `> [!example]` para ejemplos resueltos paso a paso.

*(Nota: Para el cuerpo de una Pull Request o comentarios en GitHub, reemplázalos por su equivalente GFM: `[!NOTE]`, `[!TIP]`, `[!WARNING]`, etc.)*

### D. Formato de Enlaces según el Entorno (Obsidian vs. GitHub vs. Chat)

Para asegurar que los enlaces funcionen tanto en la navegación local de Obsidian como en la web de GitHub y en el chat:

| Entorno | Formato de Enlace | Sintaxis | Ejemplo | Motivo |
| :--- | :--- | :--- | :--- | :--- |
| **Apuntes del Vault (`Tema 1/` ... `Tema 5/`)** | **Wikilinks de Obsidian** | `[[Ruta/Relativa/Nota\|Texto]]` | `[[Tema 2/1. Representacion y Filtrado\|1. Filtrado]]` | Integración con el grafo, enlaces bidireccionales y navegación nativa de Obsidian. |
| **GitHub (PRs, Issues, Comentarios)** | **Markdown Estándar Relativo** | `[Texto](ruta/relativa.md)` | `[1. Filtrado](Tema%202/1.%20Representacion%20y%20Filtrado.md)` | GitHub en la web no resuelve wikilinks `[[...]]`; requiere enlaces Markdown estándar. |
| **Chat de Asistentes IA (IDE)** | **Markdown Estándar con `file:///`** | `[Texto](file:///ruta/absoluta.md)` | `[1. Filtrado](file:///home/.../Tema%202/1.md)` | Requerido por el harness del editor para abrir el archivo directamente en el IDE al hacer clic. |

* **Prohibición de rutas absolutas en archivos del repositorio:** Ningún archivo markdown del repositorio debe contener rutas absolutas (`file:///...` o `/home/...`). Todos los enlaces dentro del vault deben ser relativos mediante Wikilinks para garantizar la portabilidad absoluta del repositorio entre diferentes usuarios y sistemas operativos.

---

## 3. Contenido del Vault

* 📝 **Ampliación de temas:** Añadir explicaciones más claras, demostraciones paso a paso o intuiciones físicas.
* 🧪 **Código reproducible:** Fragmentos breves y claros en Python con OpenCV o NumPy.
* 🎯 **Exámenes y ejercicios resueltos:** Preguntas teóricas de años anteriores explicadas con rigor.
* 📚 **Nuevas referencias:** Artículos clave o tutoriales recomendados.
* 📚 **Mejoras en la búsqueda semántica:** Mejoras en los scripts de consulta, descarga o instrucciones para el agente.

---

## 4. Tarjetas de Autoevaluación con LearnKit

Las reglas completas están en [AGENTS.md, sección 6](AGENTS.md#6-creación-y-mantenimiento-de-tarjetas-learnkit). Para crear o mantener tarjetas:

1. **Ubicación:** añadir `## Autoevaluación — LearnKit` al final de cada apunte, después de los enlaces relacionados y antes de la bibliografía. Cada nota es un mazo; las carpetas los agrupan.
2. **Formato:** usar campos canónicos con delimitador `|`, como `Q`/`A`, `CQ`, `MCQ`/`A`/`O` u `OQ` con filas numeradas. Escribir las tarjetas fuera de bloques de código, tablas y callouts. Usar grupos `G` como `VC/Tema 1/Disciplinas`.
3. **Fuentes:** consultar el RAG y leer los originales antes de redactar. Incluir en `I` una referencia concreta mediante wikilink a la fuente o al apartado que la documenta, y mantener la bibliografía formal al final. Preferir wikilinks sin alias dentro de los campos y comprobar cualquier barra `|` en el contenido.
4. **Preguntas:** una idea evaluable por tarjeta, respuestas concisas, contexto suficiente y ninguna pista accidental. Identificar autor o fecha cuando condicionen la respuesta. Las cantidades son orientativas, no cuotas.
5. **Ejercicios:** conservar los problemas largos y exámenes completos; crear tarjetas de pasos o decisiones cuando ayuden. Distinguir preguntas originales de examen y preguntas nuevas de autoevaluación.
6. **Sincronización:** comprobar los ajustes instalados y usar preferentemente `Simple` para el formato canónico. No cambiar delimitadores globales ni normalizar otros contenidos incidentalmente. Conservar los identificadores `^learnkit-…`; los nuevos los genera LearnKit al sincronizar.
7. **Mantenimiento:** comprobar las tarjetas al corregir la teoría; no editar directamente la base de datos ni el historial. El progreso es personal y su copia de seguridad debe contemplarse aparte de la copia de los apuntes.
8. **Validación:** revisar sintaxis, enlaces, fuentes y duplicados; probar una muestra de cada tipo en Obsidian cuando sea posible. Informar por separado de las comprobaciones de archivos y las pruebas visuales o funcionales pendientes.

## Referencias Bibliográficas y Técnicas

- **VC_APUNTES**. *Directivas para agentes de IA*. [AGENTS.md](AGENTS.md), secciones 3 (fuentes), 5 (formato) y 6 (LearnKit).
- **Guy, William y colaboradores** (2026). *LearnKit Documentation*. Secciones [Creating Flashcards](https://ctrlaltwill.github.io/LearnKit/Creating-Flashcards/), [Syncing](https://ctrlaltwill.github.io/LearnKit/Syncing/) y [Backups](https://ctrlaltwill.github.io/LearnKit/Backups/). Documentación web sin paginación.
