import os
import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from google import genai
from dotenv import load_dotenv
from image_generator import generate_social_media_image
import shutil
import subprocess

# --- Configuración de la Página ---
st.set_page_config(page_title="Generador de Historias - Club de la Libertad", page_icon="🗽", layout="wide")

# Cargar variables de entorno
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Inicialización de Base de Datos Vectorial ---
@st.cache_resource
def get_chroma_collection():
    db_dir = os.path.join(base_dir, "data", "chroma_db")
    
    client = chromadb.PersistentClient(path=db_dir)
    local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    collection = client.get_collection(
        name="textos_clasicos",
        embedding_function=local_ef
    )
    return collection

try:
    collection = get_chroma_collection()
except Exception as e:
    st.error(f"Error al conectar con la base de datos de textos. ¿Ya corriste el ingest.py?\n{e}")
    st.stop()

# --- Extraer Metadatos para Filtros ---
try:
    all_data = collection.get(include=["metadatas"])
    autores_unicos = set()
    libros_por_autor = {}
    
    for meta in all_data.get('metadatas', []):
        if meta and 'author' in meta and 'title' in meta:
            autor = meta['author']
            titulo = meta['title']
            autores_unicos.add(autor)
            if autor not in libros_por_autor:
                libros_por_autor[autor] = set()
            libros_por_autor[autor].add(titulo)
except Exception:
    autores_unicos = set()
    libros_por_autor = {}

lista_autores = ["Todos"] + sorted(list(autores_unicos))

# --- Funciones Auxiliares ---
def generar_respuesta(prompt_texto):
    if not GEMINI_API_KEY:
        st.error("No se encontró la GEMINI_API_KEY en el archivo .env")
        return None
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    modelos_disponibles = ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']
    
    ultimo_error = None
    for modelo in modelos_disponibles:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt_texto,
            )
            return response.text
        except Exception as e:
            ultimo_error = e
            continue
            
    st.error(f"Error al comunicarse con Gemini (incluso tras probar modelos de respaldo): {ultimo_error}")
    return None

# --- Estado de la Sesión ---
if 'posteo_generado' not in st.session_state:
    st.session_state.posteo_generado = None
if 'contexto_actual' not in st.session_state:
    st.session_state.contexto_actual = None

# --- Interfaz de Usuario Principal ---
st.title("🗽 Generador de Contenido: Club de la Libertad")
st.markdown("Busca conceptos en nuestros libros clásicos y genera borradores automáticos para redes sociales.")
st.divider()

tab_generador, tab_admin = st.tabs(["📝 Generador de Posteos", "⚙️ Administración de Biblioteca"])

with tab_generador:
    col_filtros, col_principal = st.columns([1, 2])

    with col_filtros:
        st.subheader("⚙️ Configuración")
        with st.container(border=True):
            st.markdown("**Filtros de Búsqueda**")
            autor_seleccionado = st.selectbox("Filtrar por Autor", lista_autores)
            
            lista_libros = ["Todos"]
            if autor_seleccionado != "Todos" and autor_seleccionado in libros_por_autor:
                lista_libros += sorted(list(libros_por_autor[autor_seleccionado]))
                
            libro_seleccionado = st.selectbox("Filtrar por Libro", lista_libros)
            
            st.markdown("**Estilo del Posteo**")
            tono = st.selectbox("Tono del mensaje", ["Inspirador", "Académico", "Polémico / Debate", "Directo y Comercial", "Explicación Sencilla"])

    with col_principal:
        st.subheader("✨ Crear Nuevo Posteo")
        tema = st.text_input("¿De qué querés hablar hoy?", placeholder="Ej: libre mercado, propiedad, tiranía...")
        
        if st.button("🔍 Buscar y Generar", type="primary", use_container_width=True):
            if not tema:
                st.warning("Por favor ingresá un tema primero.")
            else:
                with st.spinner("Buscando en la base de datos..."):
                    where_clause = None
                    if libro_seleccionado != "Todos":
                        where_clause = {"title": libro_seleccionado}
                    elif autor_seleccionado != "Todos":
                        where_clause = {"author": autor_seleccionado}

                    kwargs = {"query_texts": [tema], "n_results": 3}
                    if where_clause:
                        kwargs["where"] = where_clause
                        
                    results = collection.query(**kwargs)
                    
                    if not results['documents'] or not len(results['documents'][0]):
                        st.error("No se encontraron fragmentos con estos filtros. Probá ampliando la búsqueda.")
                    else:
                        fragmentos = results['documents'][0]
                        metadatos = results['metadatas'][0]
                        
                        contexto_text = ""
                        for i in range(len(fragmentos)):
                            autor = metadatos[i].get("author", "Desconocido")
                            titulo = metadatos[i].get("title", "Desconocido")
                            contexto_text += f"\n- Fragmento de {autor} en '{titulo}':\n\"{fragmentos[i]}\"\n"

                        st.session_state.contexto_actual = contexto_text

                        with st.spinner("Redactando posteo con IA..."):
                            prompt_inicial = f"""
    Actúa como un Community Manager experto del 'Club de la Libertad'.
    Tu objetivo es crear el texto para una Historia de Instagram (o posteo corto) sobre el tema: "{tema}".

    Debes basarte ESTRICTAMENTE en los siguientes fragmentos extraídos de nuestros libros clásicos:
    {contexto_text}

    Instrucciones:
    1. El tono debe ser: {tono}.
    2. Usa emojis apropiados.
    3. El posteo debe incluir la cita central o un parafraseo muy fiel, mencionando claramente al autor y al libro.
    4. MODERNIZA EL LENGUAJE: Si los fragmentos contienen ejemplos históricos oscuros (ej. impuestos antiguos como la 'alcabala'), palabras en inglés antiguo, o lenguaje arcaico, extrae ÚNICAMENTE la lección filosófica o económica y explícala con palabras modernas, claras y accesibles para el público general de hoy.
    5. Finaliza el posteo con un Call to Action (CTA) invitando a los seguidores a COMPRAR el libro en la tienda del Club de la Libertad.
    6. Hazlo conciso, dinámico y apto para redes sociales.
    """
                            texto_generado = generar_respuesta(prompt_inicial)
                            if texto_generado:
                                st.session_state.posteo_generado = texto_generado

        if st.session_state.posteo_generado:
            st.divider()
            st.subheader("📝 Posteo Generado")
            
            with st.container(border=True):
                st.info(st.session_state.posteo_generado)
                
            with st.expander("Ver citas originales encontradas"):
                st.markdown(st.session_state.contexto_actual)
                
            st.markdown("---")
            col_ajuste, col_placa = st.columns(2)
            
            with col_ajuste:
                st.subheader("🛠️ ¿No te convence?")
                instruccion_ajuste = st.text_input("Instrucción de cambio:", placeholder="Ej: Hacelo más corto.")
                
                if st.button("Ajustar Posteo"):
                    if instruccion_ajuste:
                        with st.spinner("Reescribiendo..."):
                            prompt_ajuste = f"""
    Actúa como Community Manager del 'Club de la Libertad'.
    Anteriormente escribiste este posteo: "{st.session_state.posteo_generado}"
    El director pide este ajuste: "{instruccion_ajuste}"
    Reescribe el posteo aplicando este cambio. Manten mención al autor y CTA.
    """
                            nuevo_texto = generar_respuesta(prompt_ajuste)
                            if nuevo_texto:
                                st.session_state.posteo_generado = nuevo_texto
                                st.rerun()
                                
            with col_placa:
                st.subheader("🎨 Generar Placa (Instagram)")
                frase_placa = st.text_area("Frase para la placa", value="Pega aquí la mejor frase corta del posteo...")
                autor_placa = st.text_input("Firma/Autor", value="Autor - Libro")
                
                if st.button("Generar Imagen"):
                    with st.spinner("Creando diseño..."):
                        img_path = os.path.join(base_dir, "placa_generada.png")
                        generate_social_media_image(frase_placa, autor_placa, img_path)
                        st.image(img_path, caption="¡Placa lista para subir!")
                        with open(img_path, "rb") as file:
                            st.download_button(label="Descargar Placa", data=file, file_name="placa_club_libertad.png", mime="image/png")

with tab_admin:
    st.subheader("📚 Carga de Nuevos Libros")
    st.markdown("Arrastra un archivo `.txt` con el formato `Título - Autor.txt`. Luego haz clic en Actualizar Base de Datos.")
    
    uploaded_file = st.file_uploader("Subir libro (.txt)", type=['txt'])
    if uploaded_file is not None:
        raw_dir = os.path.join(base_dir, "data", "raw")
        save_path = os.path.join(raw_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Archivo '{uploaded_file.name}' subido a data/raw/")
        
    if st.button("🔄 Actualizar Base de Datos (Correr Ingesta)", type="primary"):
        with st.spinner("Ingestando nuevos libros... Esto puede tardar unos minutos."):
            try:
                ingest_script = os.path.join(base_dir, "src", "ingest.py")
                # Ejecutar ingest.py como subproceso
                result = subprocess.run(["uv", "run", "python", ingest_script], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("¡Ingesta completada! La base de datos fue actualizada.")
                    st.cache_resource.clear() # Limpiar cache para recargar la db
                    st.rerun()
                else:
                    st.error(f"Hubo un error en la ingesta:\n{result.stderr}")
            except Exception as e:
                st.error(f"Error al ejecutar script: {e}")
