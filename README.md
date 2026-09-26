# 🗽 Generador de Contenido RAG - Club de la Libertad

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Local-orange.svg)
![Gemini AI](https://img.shields.io/badge/AI-Google_Gemini-green.svg)

Una herramienta interna basada en Inteligencia Artificial y la arquitectura **RAG** (*Retrieval-Augmented Generation*) diseñada para agilizar el trabajo de los voluntarios del **Club de la Libertad**. 

Este sistema automatiza la búsqueda de fragmentos en libros clásicos de la Escuela Austríaca y el Liberalismo Clásico, redacta posteos modernos para redes sociales usando Google Gemini, y genera placas gráficas listas para publicar en Instagram con un CTA directo a la tienda del club.

---

## ✨ Características Principales

*   **Buscador Inteligente (RAG):** Busca conceptos clave en miles de páginas de autores como Rothbard, Hayek, Mises, Bastiat, Locke y Smith.
*   **Redactor IA (Gemini):** Actúa como *Community Manager*, adaptando textos del siglo XVIII/XIX a un lenguaje moderno, dinámico y apto para redes sociales.
*   **Diseñador de Placas Automático:** Genera imágenes en formato cuadrado (1080x1080) con la cita destacada, el autor y el estilo visual, listas para descargar en PNG.
*   **Gestor de Biblioteca (Admin):** Permite subir nuevos libros `.txt` directamente desde la interfaz web y actualizar la base de datos sin tocar una sola línea de código.
*   **Extracción Automática de PDFs:** Incluye scripts con IA difusa (*Fuzzy Matching*) que escurren repositorios de Google Drive para encontrar PDFs de libros, copiarlos y convertirlos a texto plano automáticamente.

## 🛠️ Arquitectura Técnica
*   **Gestor de Entornos:** `uv` (extremadamente rápido).
*   **Embeddings:** `all-MiniLM-L6-v2` corriendo **100% en local** con `SentenceTransformers` para costo cero.
*   **Base de Datos Vectorial:** `ChromaDB` (persistencia local).
*   **Frontend:** `Streamlit`.
*   **LLM:** `google-genai` (SDK nativo de Gemini con fallback dinámico entre modelos Flash y Flash-Lite).

## 🚀 Instalación y Uso Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/SantiagoScetti/Frases-Autores-CDL.git
   cd Frases-Autores-CDL/MVP
   ```

2. **Configurar el entorno y las variables:**
   Instala las dependencias y crea tu archivo `.env` en la carpeta `MVP/`.
   Debes incluir tu clave de API de Gemini:
   ```ini
   GEMINI_API_KEY=tu_clave_aqui
   ```

3. **Ingestar los Libros Iniciales:**
   Esto leerá todos los textos de `data/raw/` y creará la base de datos vectorial local. Puede demorar un par de minutos la primera vez.
   ```bash
   uv run python src/ingest.py
   ```

4. **Levantar la Aplicación Web:**
   ```bash
   uv run streamlit run src/app.py
   ```

## 🗺️ Estructura del Proyecto

*   `src/app.py`: La interfaz web principal (Streamlit).
*   `src/ingest.py`: El motor ETL que trocea textos y los inyecta en ChromaDB.
*   `src/image_generator.py`: Generador de gráficos con Pillow.
*   `src/find_and_convert_pdfs.py`: Script para cruzar listas de libros con repositorios de Google Drive e ingestar PDFs.
*   `PROJECT_CONTEXT.md`: Archivo maestro con la hoja de ruta y detalles de la arquitectura.

---
*Desarrollado para la difusión de las ideas de la libertad.*
