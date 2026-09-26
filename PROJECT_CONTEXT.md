# 🗽 Proyecto: Generador de Contenido RAG - Club de la Libertad

## 📖 Descripción General
El proyecto es una herramienta interna diseñada para facilitar la labor de los voluntarios del **Club de la Libertad**. Su función principal es asistir en la creación de contenido para redes sociales (Historias de Instagram, posteos en X, etc.) extrayendo inteligentemente frases de libros clásicos de la filosofía y economía liberal, para luego utilizar IA Generativa que redacte un mensaje moderno, atractivo y que incluya un *Call to Action* (CTA) para la venta de dichos libros en la tienda de la organización.

---

## 🏗️ Arquitectura Actual (MVP Completado)
El sistema está construido bajo el paradigma **RAG** (*Retrieval-Augmented Generation*) utilizando Python y el gestor de paquetes rápidos `uv`.

### 1. Ingesta de Datos Automática (`src/ingest.py` y Automatizaciones)
- **Archivos Fuente:** Ubicados en `data/raw/` y `data/raw/pdfs/`. 
- **Extracción de PDFs:** El script `src/find_and_convert_pdfs.py` utiliza Inteligencia Artificial difusa (*Fuzzy Matching*) para escanear directorios masivos de Google Drive, detectar libros deseados y extraer el texto plano de los PDFs usando `PyPDF2`.
- **Metadata Inteligente:** Se extraen el Autor y Título dinámicamente desde el nombre del archivo en español. Los IDs se generan por hash MD5 para evitar colisiones.
- **Embeddings y Base Vectorial:** `SentenceTransformers` (`all-MiniLM-L6-v2`, dimensión 384) inyectando en base **ChromaDB** persistente. Costo de ingesta: $0.

### 2. Frontend Web y RAG (`src/app.py`)
- **Framework:** **Streamlit** dividido en dos pestañas ("Generador" y "Administración").
- **Generación Textual:** Usa `google-genai` (modelos Gemini 3.8 Flash) con prompt engineering avanzado y fallbacks. Permite iteración y ajuste en memoria.
- **Dashboard Administrativo:** Los usuarios pueden subir archivos `.txt` desde la web y presionar un botón para lanzar la ingesta vectorial en background (`subprocess`), sin tocar la consola.

### 3. Diseñador de Placas Automáticas (`src/image_generator.py`)
- **Pillow (PIL):** Módulo incorporado que toma una frase seleccionada y el autor, y renderiza automáticamente una imagen cuadrada `.png` de color sólido.
- Integrado en Streamlit con un botón directo de descarga para uso rápido en Instagram.

---

## 🚀 Alcance Futuro (Roadmap de Mejoras)
Este documento servirá de base para que las IAs asistan en los próximos pasos del proyecto:

1. **Templates de Imagen para Placas:**
   - Reemplazar el fondo de color sólido generado por `Pillow` por una plantilla institucional (`template.png`) provista por el Club, para que las frases se rendericen con el diseño oficial de la organización.

2. **Registro Histórico y "Favoritos" (Base Relacional):**
   - Acoplar una base de datos ligera (como SQLite o Supabase) para guardar los textos e imágenes generadas.
   - Permitir que el equipo le dé "Me gusta", creando un banco de posteos listos para publicar (Cola de publicación).

3. **Limpieza Avanzada (Data Cleansing) y Chunking Semántico:**
   - Mejorar la calidad de los textos extraídos de PDFs limpiando encabezados y números de página. Implementar segmentación por párrafos semánticos (LangChain).

4. **Publicación Automática:**
   - Integración directa con APIs de redes sociales (Instagram/Facebook Graph API o X API) para postear directamente desde la aplicación.

---

## 🤖 Guía para Asistentes de IA
- **Prioridad Tecnológica:** Modificaciones visuales en **Streamlit**. Dependencias en **uv**. Generación de imágenes con **Pillow**.
- **Precaución Base de Datos:** Si el modelo de embedding (actual `384`) cambia, la carpeta `data/chroma_db` debe purgarse.
- **Mantenimiento:** Al alcanzar un nuevo hito, actualiza este archivo para asegurar la persistencia del conocimiento arquitectónico.
