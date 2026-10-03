import os
import re
import html
import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from google import genai
from groq import Groq
from dotenv import load_dotenv
from image_generator import generate_social_media_image
import shutil
import subprocess
import db
import ingest
import random
import theme
from theme import get_theme_css

# Inicializar Base de Datos de forma eficiente (solo 1 vez por sesión/arranque)
@st.cache_resource
def setup_database():
    db.init_db()
    return True

setup_database()

# --- Funciones de Limpieza y Formato Editorial ---
def clean_emojis(text: str) -> str:
    """Elimina emojis y símbolos de redes de un texto, preservando puntuación y acentos en español."""
    if not text:
        return ""
    emoji_pattern = re.compile(
        r'[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002300-\U000023FF\U00002B50-\U00002B55\U0000FE00-\U0000FE0F]+'
    )
    cleaned = emoji_pattern.sub('', str(text))
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)
    return cleaned.strip()

def extract_quote_preview(content: str):
    """Extrae la frase central y el autor para el renderizado editorial de tarjetas."""
    cleaned = clean_emojis(content)
    lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
    quote_lines = []
    author_text = ""
    in_quote = False
    
    for l in lines:
        if l.startswith('>') or l.startswith('“') or l.startswith('"') or l.startswith('«'):
            q_clean = l.lstrip('>').strip().strip('"“”«»')
            if q_clean:
                quote_lines.append(q_clean)
                in_quote = True
        elif in_quote and (l.startswith('—') or l.startswith('-') or l.startswith('–')):
            author_text = l.lstrip('—-– ').strip('*_')
            break
        elif in_quote and quote_lines:
            break

    if quote_lines:
        return ' '.join(quote_lines), author_text
    
    # Fallback: primera frase sustancial que no sea título de opción o imagen
    for l in lines:
        if not l.startswith('**[') and not l.startswith('---') and not l.startswith('Opción') and not l.startswith('**Opción'):
            return l[:170] + ('...' if len(l) > 170 else ''), ''
            
    return cleaned[:150], ''

def render_post_card_content(topic, tone, content, created_at):
    """Renderiza el bloque editorial de una publicación con jerarquía visual clásica e iconos nítidos."""
    date_str = created_at[:10] if created_at else ""
    clean_topic = clean_emojis(str(topic))
    clean_tone = clean_emojis(str(tone))
    header_html = f"""
    <div class="card-meta-header">
        <span class="card-author-title">
            <span class="material-symbols-rounded" style="font-size: 18px; color: #E85D04;">format_quote</span>
            {html.escape(clean_topic)}
        </span>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span class="meta-pill">
                <span class="material-symbols-rounded" style="font-size: 13px;">label</span>
                {html.escape(clean_tone)}
            </span>
            <span class="meta-date">
                <span class="material-symbols-rounded" style="font-size: 13px;">calendar_today</span>
                {html.escape(date_str)}
            </span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    quote_text, author_text = extract_quote_preview(content)
    if quote_text:
        author_html = f'<div class="quote-author">— {html.escape(author_text)}</div>' if author_text else ""
        quote_html = f"""
        <div class="editorial-quote">
            “{html.escape(quote_text)}”
            {author_html}
        </div>
        """
        st.markdown(quote_html, unsafe_allow_html=True)
    else:
        preview = clean_emojis(content)[:160]
        st.markdown(f'<div class="editorial-quote">“{html.escape(preview)}...”</div>', unsafe_allow_html=True)

# --- Configuración de la Página ---
st.set_page_config(page_title="Club de la Libertad - Sistema de Frases", layout="wide")

# --- Gestión Dinámica de Tema (Oscuro / Claro) ---
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Oscuro"

is_dark_mode = (st.session_state.theme_mode == "Oscuro")
st.markdown(get_theme_css(is_dark=is_dark_mode), unsafe_allow_html=True)

# Cargar variables de entorno
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Inicialización del Motor de Búsqueda Vectorial (Dual: Neon pgvector / ChromaDB local) ---
@st.cache_resource
def get_embedding_model():
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

@st.cache_resource
def get_raw_chroma_collection():
    db_dir = os.path.join(base_dir, "data", "chroma_db")
    if not os.path.exists(db_dir):
        return None
    try:
        client = chromadb.PersistentClient(path=db_dir)
        local_ef = get_embedding_model()
        return client.get_collection(name="textos_clasicos", embedding_function=local_ef)
    except Exception:
        return None

raw_collection = get_raw_chroma_collection()

class UnifiedVectorCollection:
    """Capa de abstracción que enruta consultas a Neon PostgreSQL (pgvector) o a ChromaDB local."""
    def query(self, query_texts, n_results=3, where=None, **kwargs):
        if db.is_postgres():
            ef = get_embedding_model()
            q_text = query_texts[0] if isinstance(query_texts, list) and query_texts else str(query_texts)
            embeddings = ef([q_text])
            emb = list(embeddings[0]) if embeddings is not None else []
            
            author_filter = None
            title_filter = None
            if where:
                if "author" in where:
                    author_filter = where["author"]
                if "title" in where:
                    title_filter = where["title"]
                if "$and" in where:
                    for cond in where["$and"]:
                        if "author" in cond:
                            author_filter = cond["author"]
                        if "title" in cond:
                            title_filter = cond["title"]

            if author_filter and isinstance(author_filter, dict) and "$in" in author_filter:
                author_filter = author_filter["$in"]

            rows = db.search_chunks_pgvector(emb, n_results=n_results, author=author_filter, title=title_filter)
            docs = [r[3] for r in rows]
            metas = [{"title": r[1], "author": r[2]} for r in rows]
            ids = [r[0] for r in rows]
            return {
                "ids": [ids],
                "documents": [docs],
                "metadatas": [metas]
            }
        else:
            if raw_collection is not None:
                kw = {"query_texts": query_texts, "n_results": n_results}
                if where:
                    kw["where"] = where
                return raw_collection.query(**kw)
            return {"ids": [[]], "documents": [[]], "metadatas": [[]]}

    def get(self, *args, **kwargs):
        if raw_collection is not None:
            return raw_collection.get(*args, **kwargs)
        return {"ids": [], "metadatas": [], "documents": []}

collection = UnifiedVectorCollection()

# --- Normalización de Autores ---
MAPA_AUTORES = {
    "Mises": "Ludwig von Mises",
    "Rothbard": "Murray Rothbard",
    "Rothbard Murray": "Murray Rothbard",
    "Rothbard Murray N": "Murray Rothbard",
    "VVAA": "Robert Wenzel",
    "Tannehill Morris y Linda": "Morris y Linda Tannehill",
    "De Jasay Anthony": "Anthony de Jasay",
    "Chodorov Frank": "Frank Chodorov"
}

# --- Extraer Metadatos para Filtros con Caché (@st.cache_data) ---
@st.cache_data(ttl=1800)
def get_catalog_metadata():
    autores_unicos = set()
    libros_por_autor = {}

    # 1. Priorizar lectura estructurada de la base de datos relacional (~2ms)
    try:
        books_db = db.get_all_books_metadata()
        for b in books_db:
            raw_author = b[1].strip() if b[1] else "Desconocido"
            autor = MAPA_AUTORES.get(raw_author, raw_author)
            titulo = b[0]
            autores_unicos.add(autor)
            if autor not in libros_por_autor:
                libros_por_autor[autor] = set()
            libros_por_autor[autor].add(titulo)
    except Exception:
        pass

    # 2. Si la base de datos está vacía, consultar la colección vectorial como fallback
    if not autores_unicos:
        try:
            coll = get_chroma_collection()
            all_data = coll.get(include=["metadatas"])
            for meta in all_data.get('metadatas', []):
                if meta and 'author' in meta and 'title' in meta:
                    raw_author = meta['author'].strip()
                    autor = MAPA_AUTORES.get(raw_author, raw_author)
                    titulo = meta['title']
                    autores_unicos.add(autor)
                    if autor not in libros_por_autor:
                        libros_por_autor[autor] = set()
                    libros_por_autor[autor].add(titulo)
        except Exception:
            pass

    return sorted(list(autores_unicos)), {k: sorted(list(v)) for k, v in libros_por_autor.items()}

autores_lista_raw, libros_por_autor = get_catalog_metadata()
lista_autores = ["Todos"] + autores_lista_raw

# --- Diccionario de Temas Clave (Predeterminados + Dinámicos desde DB) ---
AUTORES_TEMAS_CLAVE = {
    "Ludwig von Mises": ["Praxeología", "Acción Humana", "Cálculo Económico", "Intervencionismo", "Inflación"],
    "Friedrich Hayek": ["Orden Espontáneo", "Sistema de Precios", "Conocimiento Disperso", "Camino de Servidumbre", "Socialismo"],
    "Adam Smith": ["Mano Invisible", "División del Trabajo", "Libre Comercio", "Simpatía"],
    "Frederic Bastiat": ["Lo que se ve y no se ve", "La Ley", "Saqueo Legal", "Falacia de la Ventana Rota", "Estado"],
    "Murray Rothbard": ["Anarcocapitalismo", "Derechos Naturales", "Abolición del Estado", "Banca Libre", "Estado"],
    "Juan Bautista Alberdi": ["Constitución", "Inmigración", "Libre Navegación", "Gobierno Limitado"],
    "Milton Friedman": ["Libertad de Elegir", "Monetarismo", "Impuesto Negativo", "Libre Mercado"],
    "Ayn Rand": ["Objetivismo", "Egoísmo Racional", "Virtud del Egoísmo", "Capitalismo"],
    "Lysander Spooner": ["Anarquismo Individualista", "Contrato Social", "Ley Natural", "Vicios no son Delitos"]
}

# Cargar autores dinámicos dados de alta en la base de datos con caché
@st.cache_data(ttl=600)
def get_cached_author_topics():
    try:
        return db.get_all_authors_with_topics()
    except Exception:
        return {}

for dynamic_author, dynamic_topics in get_cached_author_topics().items():
    if dynamic_author not in AUTORES_TEMAS_CLAVE or not AUTORES_TEMAS_CLAVE[dynamic_author]:
        AUTORES_TEMAS_CLAVE[dynamic_author] = dynamic_topics

# --- Funciones Auxiliares ---
def generar_respuesta(prompt_texto):
    ultimo_error = None

    # 1. Intentar con Gemini
    if GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            modelos_disponibles = ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']
            for modelo in modelos_disponibles:
                try:
                    response = client.models.generate_content(model=modelo, contents=prompt_texto)
                    return clean_emojis(response.text)
                except Exception as e:
                    ultimo_error = e
                    continue
        except Exception as e:
            ultimo_error = e

    # 2. Respaldo: Groq
    if GROQ_API_KEY:
        try:
            groq_client = Groq(api_key=GROQ_API_KEY)
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_texto}],
                model="llama3-8b-8192",
            )
            return clean_emojis(chat_completion.choices[0].message.content)
        except Exception as e:
            ultimo_error = e

    if not GEMINI_API_KEY and not GROQ_API_KEY:
        st.error("No se encontró GEMINI_API_KEY ni GROQ_API_KEY en el archivo .env")
        return None

    st.error(f"Error al comunicarse con las APIs (Gemini y Groq fallaron o están sin cuota): {ultimo_error}")
    return None

# --- Estado de la Sesión ---
if 'posteo_generado' not in st.session_state:
    st.session_state.posteo_generado = None
if 'contexto_actual' not in st.session_state:
    st.session_state.contexto_actual = None
if 'frase_rapida_generada' not in st.session_state:
    st.session_state.frase_rapida_generada = None
if 'frase_rapida_original' not in st.session_state:
    st.session_state.frase_rapida_original = None
if 'citas_crudas' not in st.session_state:
    st.session_state.citas_crudas = None
if 'citas_crudas_meta' not in st.session_state:
    st.session_state.citas_crudas_meta = None

# --- Encabezado Institucional y Selector de Tema (Arriba a la Derecha) ---
col_head_brand, col_theme_switch = st.columns([3.8, 1.2], vertical_alignment="center")

with col_head_brand:
    st.markdown("""
    <div class="brand-header-box">
        <div class="brand-logo-icon" title="Club de la Libertad — Antorcha de la Libertad">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C10.5 4.5 11 7 9.5 8.5C8.5 7.5 8.5 6 9 4.5C6.5 6.5 6 10 7.5 12.5C8 13.3 8.8 14 9.8 14.5C9.5 13.5 9.7 12.5 10.3 11.8C10.8 12.8 11.7 13.5 12.8 13.8C14.8 14.3 16.5 13 16.8 11C17.2 9 16 7 14.5 5.5C14.8 7 14 8 13.2 8.5C13.2 6.5 13 4 12 2Z" fill="#FFF275"/>
                <path d="M12 5.5C11.2 7 11.5 8.5 10.8 9.5C10.2 8.8 10.2 7.8 10.5 7C9 8.2 8.8 10.5 9.8 12C10.1 12.5 10.6 13 11.2 13.2C11 12.6 11.2 12 11.5 11.5C11.8 12.2 12.5 12.7 13.2 12.8C14.5 13.1 15.5 12.2 15.7 11C16 9.8 15.2 8.5 14.2 7.5C14.5 8.5 14 9.2 13.5 9.5C13.5 8.2 13.2 6.8 12 5.5Z" fill="#FFFFFF"/>
                <path d="M7 14H17L15.6 17.2H8.4L7 14Z" fill="#FFFFFF"/>
                <rect x="8" y="17.8" width="8" height="1.4" rx="0.7" fill="#FFF275"/>
                <path d="M9.5 19.8L10.3 26H13.7L14.5 19.8H9.5Z" fill="#FFFFFF"/>
                <rect x="10" y="26.3" width="4" height="1.4" rx="0.7" fill="#FFF275"/>
            </svg>
        </div>
        <div class="brand-title-group">
            <h1>Club de la Libertad</h1>
            <p>Generador Editorial de Contenido & Banco de Publicaciones</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_theme_switch:
    current_default = ":material/dark_mode: Oscuro" if st.session_state.theme_mode == "Oscuro" else ":material/light_mode: Claro"
    selected_theme = st.segmented_control(
        "Tema",
        options=[":material/dark_mode: Oscuro", ":material/light_mode: Claro"],
        default=current_default,
        key="theme_mode_selector",
        label_visibility="collapsed"
    )
    if selected_theme:
        target_mode = "Oscuro" if "Oscuro" in selected_theme else "Claro"
        if target_mode != st.session_state.theme_mode:
            st.session_state.theme_mode = target_mode
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TABS — Navegación Sobria y Limpia con Iconos
# ═══════════════════════════════════════════════════════════════════════════════
tab_frases, tab_generador, tab_banco, tab_biblioteca, tab_admin = st.tabs([
    ":material/bolt: Frases Rápidas",
    ":material/article: Generador de Posteos",
    ":material/inventory_2: Banco de Publicaciones",
    ":material/library_books: Catálogo de Libros",
    ":material/admin_panel_settings: Administración",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FRASES RÁPIDAS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_frases:
    st.markdown("## :material/bolt: Frases Rápidas")
    st.caption("Citas y reflexiones editoriales basadas en el acervo de libros de la Fundación.")

    with st.container(key="card_main_f", border=True):
        col_aut, col_lib = st.columns(2)
        with col_aut:
            autor_frase = st.selectbox(":material/person: Autor", lista_autores, key="frase_autor")
        with col_lib:
            lista_libros_f = ["Todos"]
            if autor_frase != "Todos" and autor_frase in libros_por_autor:
                lista_libros_f += sorted(list(libros_por_autor[autor_frase]))
            libro_frase = st.selectbox(":material/menu_book: Libro", lista_libros_f, key="frase_libro")

        tema_libre = st.text_input(
            ":material/lightbulb: Concepto o idea clave (opcional)",
            placeholder="Ej: libertad individual, propiedad privada, cálculo económico...",
            key="tema_frase_input"
        )

        # Sugerencias dinámicas según el autor
        sugerencias = ["Libertad", "Propiedad Privada", "Estado", "Mercado"]
        if autor_frase != "Todos":
            sugerencias = AUTORES_TEMAS_CLAVE.get(autor_frase, sugerencias)

        tema_pildora = st.pills("Sugerencias", options=sugerencias, selection_mode="single", key="pills_tema", label_visibility="collapsed")
        tema_frase = tema_pildora if tema_pildora else tema_libre

        col_btn1, col_btn2 = st.columns([1.4, 1])
        with col_btn1:
            btn_generar = st.button("Generar Publicación (IA)", icon=":material/auto_awesome:", type="primary", use_container_width=True, key="btn_generar_frase")
        with col_btn2:
            btn_extraer = st.button("Citas Directas (Sin IA)", icon=":material/search:", use_container_width=True, key="btn_extraer_sin_ia")

    with st.expander(":material/tune: Opciones Avanzadas (Formato, variantes, CTA)", expanded=False):
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            tipo_frase = st.radio(
                ":material/category: Formato de Publicación",
                ["Frase inspiradora", "Efeméride / Fecha histórica", "Recomendación de libro"],
                key="frase_tipo",
            )
            if tipo_frase == "Efeméride / Fecha histórica":
                fecha_efemeride = st.text_input(
                    ":material/event: ¿Qué efeméride?",
                    placeholder="Ej: Nacimiento de Bastiat, 30 de junio",
                    key="efem_input"
                )
            else:
                fecha_efemeride = None
        with col_opt2:
            n_variaciones = st.slider(":material/format_list_numbered: Cantidad de opciones", 1, 4, 1, key="frase_n_var")
            incluir_cta = st.checkbox(":material/campaign: Incluir placa CTA (Biblioteca)", value=False, key="frase_incluir_cta")

    dispo_texto = "Disponible en la Biblioteca del Club de la Libertad."

    if btn_extraer:
        with st.spinner("Extrayendo citas del libro..."):
            st.session_state.frase_rapida_generada = None
            search_query = tema_frase or "importante fundamental esencial principal"
            where_c = None
            if libro_frase != "Todos":
                where_c = {"title": libro_frase}
            elif autor_frase != "Todos":
                aliases = [k for k, v in MAPA_AUTORES.items() if v == autor_frase] + [autor_frase]
                where_c = {"author": {"$in": aliases}}
            
            kwargs = {"query_texts": [search_query], "n_results": 20}
            if where_c: kwargs["where"] = where_c
            
            res = collection.query(**kwargs)
            if res['documents'] and len(res['documents'][0]):
                docs = res['documents'][0]
                metas = res['metadatas'][0]
                indices = list(range(len(docs)))
                random.shuffle(indices)
                indices = indices[:4]
                st.session_state.citas_crudas = [docs[i] for i in indices]
                st.session_state.citas_crudas_meta = [metas[i] for i in indices]
            else:
                st.warning("No se encontraron citas con esos parámetros.")

    if btn_generar:
        with st.spinner("Buscando en la biblioteca y generando redacción editorial..."):
            st.session_state.citas_crudas = None
            search_query = fecha_efemeride or tema_frase or (autor_frase if autor_frase != "Todos" else "libertad")
            where_c = None
            if libro_frase != "Todos":
                where_c = {"title": libro_frase}
            elif autor_frase != "Todos":
                aliases = [k for k, v in MAPA_AUTORES.items() if v == autor_frase] + [autor_frase]
                where_c = {"author": {"$in": aliases}}

            kwargs = {"query_texts": [search_query], "n_results": max(10, n_variaciones * 3)}
            if where_c:
                kwargs["where"] = where_c

            results = collection.query(**kwargs)

            fragmentos_seleccionados = []
            meta_base = {}
            if results['documents'] and len(results['documents'][0]):
                docs = results['documents'][0]
                metas = results['metadatas'][0]
                indices = list(range(len(docs)))
                random.shuffle(indices)
                indices = indices[:n_variaciones]
                
                for i in indices:
                    fragmentos_seleccionados.append(docs[i])
                meta_base = metas[indices[0]] if metas else {}
            
            fragmentos_texto = "\n\n---\n\n".join([f"Fragmento de Referencia {i+1}:\n\"{f}\"" for i, f in enumerate(fragmentos_seleccionados)])

            autor_real = meta_base.get("author", autor_frase if autor_frase != "Todos" else "Autor clásico")
            libro_real = meta_base.get("title", "")

            instruccion_vars = f"\n\nATENCIÓN: Genera {n_variaciones} opciones DISTINTAS para este posteo. Numéralas como 'Opción 1', 'Opción 2', etc. y sepáralas con una línea divisoria (---)." if n_variaciones > 1 else ""

            # ── Prompts editoriales según tipo ──
            if tipo_frase == "Frase inspiradora":
                prompt = f"""Actúa como el Community Manager y Editor de Contenido de la Fundación Club de la Libertad (Corrientes, Argentina).

Tu tarea es crear una publicación CORTA para Instagram Stories o feed, al estilo de las cuentas de alto nivel que publican citas de pensadores clásicos liberales.

FORMATO REQUERIDO (estricto):
1. Una frase impactante del autor (máximo 2 oraciones). **DEBE estar formateada como un blockquote de Markdown (usando el símbolo `>` al principio de la línea).** Si no encontrás una cita textual perfecta, parafraseá fielmente basándote en los fragmentos. Si generás varias opciones, basate en un fragmento distinto para cada una.
2. La firma claramente separada: — **{autor_real}**
3. Caption para Instagram: máximo 2-3 líneas explicando brevemente la lección filosófica o económica en lenguaje moderno, accesible y riguroso. Sin hashtags.
4. Aviso: {dispo_texto}

Fragmentos extraídos del libro '{libro_real}' para usar de inspiración:
{fragmentos_texto}

Tema: {tema_frase or 'libertad, ideas liberales'}

REGLA ESTRICTA: PROHIBIDO EL USO DE EMOJIS bajo cualquier circunstancia. Mantén un estilo sobrio, periodístico y formal.{instruccion_vars}"""

            elif tipo_frase == "Efeméride / Fecha histórica":
                prompt = f"""Actúa como el Community Manager y Editor de Contenido de la Fundación Club de la Libertad (Corrientes, Argentina).

Tu tarea es crear una publicación para Instagram sobre la efeméride: "{fecha_efemeride}".

FORMATO REQUERIDO (estricto, estilo Efemérides Libertarias del Club):
1. Encabezado: la fecha y el nombre del personaje o evento histórico.
2. Una frase icónica del personaje (si aplica). **DEBE estar formateada como un blockquote de Markdown (usando el símbolo `>`).** Con la firma: — **{autor_real}**
3. Caption para Instagram: 3-5 líneas máximo. Explica quién fue esta persona y por qué es importante para las ideas de la libertad. Tono respetuoso, formal y directo. Sin hashtags.
4. Aviso: {dispo_texto}

Si hay material del autor en la biblioteca, usá estos fragmentos como referencia (si generás varias opciones, intentá variar el fragmento que citás):
{fragmentos_texto}

REGLA ESTRICTA: PROHIBIDO EL USO DE EMOJIS. Estilo editorial sobrio y clásico.{instruccion_vars}"""

            else:  # Recomendación de libro
                prompt = f"""Actúa como el Community Manager y Editor de Contenido de la Fundación Club de la Libertad (Corrientes, Argentina).

Tu tarea es crear una publicación CORTA para Instagram recomendando el libro '{libro_real}' de {autor_real}.

FORMATO REQUERIDO:
1. Frase gancho: una cita provocadora o reflexión central extraída del libro (1 oración). **DEBE estar formateada como un blockquote de Markdown (usando el símbolo `>`).**
2. La firma claramente separada: — **{autor_real}** (del libro *{libro_real}*)
3. Breve reseña editorial (2-3 oraciones): tesis central y relevancia para el debate de ideas contemporáneo.
4. Disponibilidad: {dispo_texto}

Fragmentos de referencia del libro (para inspirar el gancho o la descripción):
{fragmentos_texto}

REGLA ESTRICTA: PROHIBIDO EL USO DE EMOJIS. Tono riguroso, intelectual y directo. Sin hashtags.{instruccion_vars}"""

            resultado = generar_respuesta(prompt)
            if resultado:
                if incluir_cta:
                    cta_text = "\n\n---\n**Texto sugerido para Story CTA:**\n¿Te interesa profundizar en estas ideas? Conseguí este y otros libros en la Biblioteca del Club de la Libertad.\nMandanos un mensaje directo para más información."
                    resultado += cta_text
                st.session_state.frase_rapida_generada = clean_emojis(resultado)
                st.session_state.frase_rapida_original = fragmentos_texto

    # ── Mostrar resultado IA ──
    if st.session_state.frase_rapida_generada:
        st.divider()
        st.markdown("### :material/history_edu: Borrador Generado")
        with st.container(key="card_result_f", border=True):
            st.markdown(st.session_state.frase_rapida_generada)
            
        if st.session_state.frase_rapida_original:
            with st.expander("Ver fragmento original del libro (fuente)", icon=":material/source:"):
                st.markdown(st.session_state.frase_rapida_original)

        # Botones de acción: Guardar / Descartar / Regenerar
        col_guardar, col_descartar, col_limpiar = st.columns(3)

        with col_guardar:
            if st.button("Guardar en Banco", icon=":material/bookmark:", type="primary", use_container_width=True, key="save_frase"):
                topic_label = clean_emojis(fecha_efemeride or tema_frase or f"Frase de {autor_frase}")
                tone_label = clean_emojis(tipo_frase)
                content_clean = clean_emojis(st.session_state.frase_rapida_generada)
                db.insert_post(topic_label, tone_label, content_clean)
                st.success("Guardada exitosamente en el Banco de Publicaciones.")

        with col_descartar:
            if st.button("Descartar", icon=":material/close:", use_container_width=True, key="discard_frase"):
                st.session_state.frase_rapida_generada = None
                st.rerun()

        with col_limpiar:
            if st.button("Regenerar", icon=":material/refresh:", use_container_width=True, key="regen_frase"):
                st.session_state.frase_rapida_generada = None
                st.rerun()

        # Sección de placa visual
        st.divider()
        st.markdown("### :material/image: Placa Gráfica para Redes")
        with st.container(key="card_placa_f", border=True):
            col_placa_frase, col_placa_autor = st.columns(2)
            with col_placa_frase:
                frase_placa = st.text_area(":material/format_quote: Frase para la placa", value="Pega aquí la frase corta...", key="placa_frase_txt")
            with col_placa_autor:
                autor_placa = st.text_input(":material/badge: Firma / Autor", value=autor_frase if autor_frase != "Todos" else "Autor", key="placa_frase_autor")

            if st.button("Generar Imagen", icon=":material/palette:", type="primary", key="gen_placa_frase"):
                with st.spinner("Creando placa gráfica..."):
                    img_bytes = generate_social_media_image(frase_placa, autor_placa)
                    st.image(img_bytes, caption="Placa lista para publicar")
                    st.download_button(label="Descargar Placa", icon=":material/download:", data=img_bytes, file_name="placa_club_libertad.png", mime="image/png", key="dl_placa_frase")

    # ── Mostrar citas directas (Sin IA) ──
    if st.session_state.citas_crudas:
        st.divider()
        st.markdown("### :material/format_quote: Citas Extraídas Directamente de la Biblioteca")
        for i, cita in enumerate(st.session_state.citas_crudas):
            meta = st.session_state.citas_crudas_meta[i] if st.session_state.citas_crudas_meta else {}
            with st.container(key=f"card_raw_quote_{i}", border=True):
                st.markdown(f"*{clean_emojis(cita)}*")
                st.caption(f"— {clean_emojis(meta.get('author', 'Autor'))} en '{clean_emojis(meta.get('title', 'Libro'))}'")
                
        if st.button("Limpiar Resultados", icon=":material/clear_all:", key="clear_citas_crudas"):
            st.session_state.citas_crudas = None
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GENERADOR DE POSTEOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_generador:
    st.markdown("## :material/article: Generador de Posteos Editoriales")
    modo = st.segmented_control(
        "Flujo de trabajo",
        [":material/lightbulb: Inspiración Libre", ":material/search: Buscar Cita Exacta", ":material/person_search: Explorar Autor"],
        default=":material/lightbulb: Inspiración Libre",
        label_visibility="collapsed"
    )
    st.divider()

    if modo and "Inspiración Libre" in modo:
        col_filtros, col_principal = st.columns([1, 1.8], gap="large")

        with col_filtros:
            st.markdown("### :material/filter_alt: Filtros de Búsqueda")
            with st.container(key="card_filtros_g", border=True):
                st.markdown("**Catálogo y Autor**")
                autor_seleccionado = st.selectbox(":material/person: Filtrar por Autor", lista_autores)

                lista_libros = ["Todos"]
                if autor_seleccionado != "Todos" and autor_seleccionado in libros_por_autor:
                    lista_libros += sorted(list(libros_por_autor[autor_seleccionado]))

                libro_seleccionado = st.selectbox(":material/menu_book: Filtrar por Libro", lista_libros)

                st.markdown("**Estilo y Enfoque**")
                tono = st.selectbox(":material/tune: Tono del mensaje", ["Inspirador", "Académico", "Polémico / Debate", "Directo y Comercial", "Explicación Sencilla"])

        with col_principal:
            st.markdown("### :material/edit_document: Crear Nuevo Posteo")
            with st.container(key="card_main_g", border=True):
                tema = st.text_input(":material/topic: ¿De qué querés hablar hoy?", placeholder="Ej: libre mercado, propiedad, tiranía...")

                if st.button("Buscar y Generar", icon=":material/auto_awesome:", type="primary", use_container_width=True):
                    if not tema:
                        st.warning("Por favor ingresá un tema primero.")
                    else:
                        with st.spinner("Buscando en la base de datos de textos clásicos..."):
                            where_clause = None
                            if libro_seleccionado != "Todos":
                                where_clause = {"title": libro_seleccionado}
                            elif autor_seleccionado != "Todos":
                                aliases = [k for k, v in MAPA_AUTORES.items() if v == autor_seleccionado] + [autor_seleccionado]
                                where_clause = {"author": {"$in": aliases}}

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
Actúa como el Community Manager y Editor de Contenido de la Fundación Club de la Libertad (Corrientes, Argentina).
Tu objetivo es crear el texto para un posteo de Instagram sobre el tema: "{tema}".

Debes basarte ESTRICTAMENTE en los siguientes fragmentos extraídos de nuestros libros clásicos:
{contexto_text}

Instrucciones:
1. El tono debe ser: {tono}.
2. REGLA ESTRICTA: PROHIBIDO EL USO DE EMOJIS. Mantén un estilo estrictamente editorial y sobrio.
3. El posteo debe incluir la cita central formateada como un blockquote de Markdown (usando `>`), mencionando claramente al autor y al libro.
4. MODERNIZA EL LENGUAJE: extrae la lección filosófica o económica y explícala con palabras modernas, claras y accesibles.
5. Finaliza con un llamado sutil invitando a conocer más del autor en la biblioteca del Club o adquirir el ejemplar.
6. Máximo 5-6 líneas de caption. Sin hashtags.
7. Estilo acorde a una publicación académica o de divulgación de ideas.
"""
                                    texto_generado = generar_respuesta(prompt_inicial)
                                    if texto_generado:
                                        st.session_state.posteo_generado = clean_emojis(texto_generado)

            if st.session_state.posteo_generado:
                st.divider()
                st.markdown("### :material/description: Posteo Generado")

                with st.container(key="card_result_g", border=True):
                    st.markdown(st.session_state.posteo_generado)

                col_save, col_discard = st.columns(2)
                with col_save:
                    if st.button("Guardar en Banco", icon=":material/bookmark:", type="primary", use_container_width=True, key="save_post_libre"):
                        db.insert_post(clean_emojis(tema), clean_emojis(tono), clean_emojis(st.session_state.posteo_generado))
                        st.success("Guardado exitosamente en el Banco de Publicaciones.")
                with col_discard:
                    if st.button("Descartar", icon=":material/close:", use_container_width=True, key="discard_post_libre"):
                        st.session_state.posteo_generado = None
                        st.rerun()

                with st.expander("Ver citas originales encontradas", icon=":material/source:"):
                    st.markdown(st.session_state.contexto_actual)

                st.divider()
                col_ajuste, col_placa = st.columns(2, gap="large")

                with col_ajuste:
                    st.markdown("### :material/instant_mix: ¿Deseas ajustar el texto?")
                    with st.container(key="card_ajuste_g", border=True):
                        instruccion_ajuste = st.text_input(":material/edit: Instrucción de cambio:", placeholder="Ej: Hacelo más corto o enfócate en la libertad.")

                        if st.button("Ajustar Posteo", icon=":material/replay:", type="primary", use_container_width=True):
                            if instruccion_ajuste:
                                with st.spinner("Reescribiendo posteo..."):
                                    prompt_ajuste = f"""
Actúa como Editor de Contenido del Club de la Libertad.
Anteriormente escribiste este posteo: "{st.session_state.posteo_generado}"
El director pide este ajuste: "{instruccion_ajuste}"
Reescribe el posteo aplicando este cambio. Mantené mención al autor y formato blockquote. Sin hashtags. PROHIBIDO EL USO DE EMOJIS.
"""
                                    nuevo_texto = generar_respuesta(prompt_ajuste)
                                    if nuevo_texto:
                                        st.session_state.posteo_generado = clean_emojis(nuevo_texto)
                                        st.rerun()

                with col_placa:
                    st.markdown("### :material/image: Placa Gráfica para Redes")
                    with st.container(key="card_placa_g", border=True):
                        frase_placa = st.text_area(":material/format_quote: Frase para la placa", value="Pega aquí la mejor frase corta del posteo...")
                        autor_placa = st.text_input(":material/badge: Firma / Autor", value="Autor - Libro")

                        if st.button("Generar Imagen", icon=":material/palette:", type="primary", use_container_width=True):
                            with st.spinner("Creando diseño de placa..."):
                                img_bytes = generate_social_media_image(frase_placa, autor_placa)
                                st.image(img_bytes, caption="Placa lista para publicar")
                                st.download_button(label="Descargar Placa", icon=":material/download:", data=img_bytes, file_name="placa_club_libertad.png", mime="image/png")

    elif modo and "Buscar Cita Exacta" in modo:
        st.markdown("### :material/search: Buscar una Cita Específica")
        st.markdown("Busca una frase exacta en la base de datos para armar un posteo a partir de ella.")
        
        with st.container(key="card_exacta_input", border=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                autor_cita = st.selectbox(":material/person: Autor (Opcional)", lista_autores, key="autor_cita")
            with col_f2:
                tono_cita = st.selectbox(":material/tune: Tono del posteo", ["Inspirador", "Académico", "Polémico", "Directo", "Sencillo"], key="tono_cita")

            frase_buscada = st.text_input(":material/format_quote: Ingresa una parte de la frase que recuerdes:")
            if st.button("Buscar y Generar", icon=":material/auto_awesome:", type="primary", key="btn_cita_exacta", use_container_width=True):
                if frase_buscada:
                    with st.spinner("Buscando en la colección..."):
                        where_c = {"author": autor_cita} if autor_cita != "Todos" else None
                        res = collection.query(query_texts=[frase_buscada], n_results=1, where=where_c)
                        if res['documents'] and len(res['documents'][0]):
                            frag = res['documents'][0][0]
                            meta = res['metadatas'][0][0]
                            st.success(f"Encontrado en: {meta.get('title')} - {meta.get('author')}")
                            st.markdown(f"> “{frag}”\n— {meta.get('author')}")

                            prompt = f"""Crea un post corto para Instagram en tono {tono_cita}. 
Usa esta cita exacta obligatoriamente: "{frag}". 
Menciona a {meta.get('author')}. PROHIBIDO EL USO DE EMOJIS. Sin hashtags. Máximo 5 líneas de caption."""
                            res_texto = generar_respuesta(prompt)
                            if res_texto:
                                st.session_state.posteo_generado = clean_emojis(res_texto)
                                st.rerun()
                        else:
                            st.error("No se encontró esa frase en los libros indexados.")

        if st.session_state.posteo_generado and "Buscar Cita Exacta" in modo:
            st.divider()
            st.markdown("### :material/description: Posteo Generado")
            with st.container(key="card_exacta_result", border=True):
                st.markdown(st.session_state.posteo_generado)
            col_s, col_d = st.columns(2)
            with col_s:
                if st.button("Guardar en Banco", icon=":material/bookmark:", type="primary", use_container_width=True, key="save_cita"):
                    db.insert_post(clean_emojis(f"Cita: {frase_buscada[:20]}"), clean_emojis(tono_cita), clean_emojis(st.session_state.posteo_generado))
                    st.success("Guardado exitosamente en el Banco.")
            with col_d:
                if st.button("Descartar", icon=":material/close:", use_container_width=True, key="discard_cita"):
                    st.session_state.posteo_generado = None
                    st.rerun()

    elif modo and "Explorar Autor" in modo:
        st.markdown("### :material/person_search: Explorar Autor")
        st.markdown("Selecciona un autor de la biblioteca para inspirarte con sus temas principales.")

        with st.container(key="card_explorar_input", border=True):
            autor_exp = st.selectbox(":material/person: Autor a explorar", [a for a in lista_autores if a != "Todos"], key="autor_exp")

            libros_meta = db.get_all_books_metadata()
            libros_autor = [l for l in libros_meta if l[1] == autor_exp]

            if not libros_autor:
                st.info("Aún no hay resúmenes de este autor en la biblioteca estructurada.")
            else:
                st.markdown(f"**Hemos encontrado {len(libros_autor)} libro(s) indexado(s) de {autor_exp}:**")
                for i, libro in enumerate(libros_autor):
                    with st.container(key=f"card_explorar_book_{i}", border=True):
                        st.markdown(f"**:material/menu_book: {clean_emojis(libro[0])}**")
                        st.markdown(f"*:material/sell: Temas:* {clean_emojis(libro[3])}")

                if st.button("Generar Post Aleatorio del Autor", icon=":material/auto_awesome:", type="primary", use_container_width=True):
                    with st.spinner("Creando post editorial..."):
                        res = collection.query(query_texts=[autor_exp], n_results=1, where={"author": autor_exp})
                        if res['documents'] and len(res['documents'][0]):
                            frag = res['documents'][0][0]
                            prompt = f"""Crea un post inspirador para Instagram citando a {autor_exp}. 
Usa esta idea o cita como base: "{frag}". Hazlo reflexivo. PROHIBIDO EL USO DE EMOJIS. Estilo editorial. 
Sin hashtags. Máximo 5 líneas de caption."""
                            res_texto = generar_respuesta(prompt)
                            if res_texto:
                                st.session_state.posteo_generado = clean_emojis(res_texto)
                                st.rerun()

        if st.session_state.posteo_generado and "Explorar Autor" in modo:
            st.divider()
            st.markdown("### :material/description: Posteo Generado")
            with st.container(key="card_explorar_result", border=True):
                st.markdown(st.session_state.posteo_generado)
            col_s2, col_d2 = st.columns(2)
            with col_s2:
                if st.button("Guardar en Banco", icon=":material/bookmark:", type="primary", use_container_width=True, key="save_explorar"):
                    db.insert_post(clean_emojis(f"Explorando {autor_exp}"), "Inspirador", clean_emojis(st.session_state.posteo_generado))
                    st.success("Guardado exitosamente en el Banco.")
            with col_d2:
                if st.button("Descartar", icon=":material/close:", use_container_width=True, key="discard_explorar"):
                    st.session_state.posteo_generado = None
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BANCO DE PUBLICACIONES (Editorial Cards)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_banco:
    st.markdown("## :material/inventory_2: Banco Editorial de Publicaciones")
    st.markdown("Revisa tus posteos guardados. Aprueba los mejores para la cola de publicación o elimina los que no correspondan.")

    posts = db.get_all_posts()
    if not posts:
        st.info("Aún no hay publicaciones guardadas. Genera una desde las otras secciones y guárdala aquí.")
    else:
        aprobados = [p for p in posts if p[4] == 1]
        pendientes = [p for p in posts if p[4] == 0]

        col_pend, col_aprob = st.columns(2, gap="large")

        with col_pend:
            st.markdown(f'''
            <div class="col-header">
                <h3><span class="material-symbols-rounded">edit_note</span> Borradores</h3>
                <span class="count-badge">{len(pendientes)}</span>
            </div>
            ''', unsafe_allow_html=True)
            if not pendientes:
                st.caption("No hay borradores pendientes.")
            for p in pendientes:
                with st.container(key=f"card_pend_{p[0]}", border=True):
                    render_post_card_content(p[1], p[2], p[3], p[5])
                    clean_content = clean_emojis(p[3])
                    with st.expander("Ver contenido completo", icon=":material/read_more:"):
                        st.markdown(clean_content)

                    c1, c2 = st.columns([1, 1])
                    with c1:
                        if st.button("Aprobar", key=f"approve_{p[0]}", icon=":material/check_circle:", type="primary", use_container_width=True):
                            db.toggle_approval(p[0], p[4])
                            st.rerun()
                    with c2:
                        with st.popover("Eliminar", icon=":material/delete_outline:", use_container_width=True):
                            st.markdown("**¿Confirmar eliminación?** Esta acción no se puede deshacer.")
                            if st.button("Confirmar eliminación", key=f"confirm_del_pend_{p[0]}", type="primary", icon=":material/delete_forever:", use_container_width=True):
                                db.delete_post(p[0])
                                st.rerun()

        with col_aprob:
            st.markdown(f'''
            <div class="col-header">
                <h3><span class="material-symbols-rounded">verified</span> Cola de Publicación</h3>
                <span class="count-badge-green">{len(aprobados)}</span>
            </div>
            ''', unsafe_allow_html=True)
            if not aprobados:
                st.caption("Aprueba borradores para que aparezcan en esta lista.")
            for p in aprobados:
                with st.container(key=f"card_aprob_{p[0]}", border=True):
                    render_post_card_content(p[1], p[2], p[3], p[5])
                    clean_content = clean_emojis(p[3])
                    with st.expander("Ver contenido completo", icon=":material/read_more:"):
                        st.markdown(clean_content)

                    c1, c2 = st.columns([1, 1])
                    with c1:
                        if st.button("Mover a Borradores", key=f"remove_{p[0]}", icon=":material/undo:", use_container_width=True):
                            db.toggle_approval(p[0], p[4])
                            st.rerun()
                    with c2:
                        with st.popover("Eliminar", icon=":material/delete_outline:", use_container_width=True):
                            st.markdown("**¿Confirmar eliminación?** Esta acción no se puede deshacer.")
                            if st.button("Confirmar eliminación", key=f"confirm_del_aprob_{p[0]}", type="primary", icon=":material/delete_forever:", use_container_width=True):
                                db.delete_post(p[0])
                                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BIBLIOTECA ESTRUCTURADA
# ═══════════════════════════════════════════════════════════════════════════════
with tab_biblioteca:
    st.markdown("## :material/library_books: Catálogo de Libros Clásicos")
    st.markdown("Obras fundamentales indexadas en la biblioteca vectorial con resúmenes y temas conceptuales.")

    libros_meta = db.get_all_books_metadata()
    if not libros_meta:
        st.info("Aún no hay resúmenes de libros. Sube un libro y actualiza la base de datos.")
    else:
        for i, libro in enumerate(libros_meta):
            with st.container(key=f"card_book_catalog_{i}", border=True):
                st.markdown(f"### :material/menu_book: {clean_emojis(libro[0])}")
                st.markdown(f"**:material/person: Autor:** {clean_emojis(libro[1])}")
                st.markdown(f"*:material/sell: Temas Principales:* {clean_emojis(libro[3])}")
                st.markdown(f"**:material/description: Resumen:** {clean_emojis(libro[2])}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ADMINISTRACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
with tab_admin:
    st.markdown("## :material/admin_panel_settings: Administración de la Biblioteca")
    
    # ── Control de Acceso por Contraseña ──
    ADMIN_PWD = os.getenv("ADMIN_PASSWORD", "libertad2026")
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.markdown("### :material/lock: Acceso Exclusivo para Editores")
        st.info("Ingresa la contraseña de administración institucional para subir libros o gestionar autores.")
        
        col_pwd, col_btn = st.columns([2.5, 1], vertical_alignment="bottom")
        with col_pwd:
            input_pwd = st.text_input("Contraseña de Administrador", type="password", key="admin_password_field")
        with col_btn:
            if st.button("Iniciar Sesión", icon=":material/login:", type="primary", use_container_width=True):
                if input_pwd == ADMIN_PWD:
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta. Consulta al responsable técnico del Club.")
    else:
        col_admin_title, col_admin_logout = st.columns([3, 1], vertical_alignment="center")
        with col_admin_title:
            st.caption(":material/verified_user: Sesión activa como Administrador Editorial")
        with col_admin_logout:
            if st.button("Cerrar Sesión", icon=":material/logout:", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.rerun()

        st.divider()

        # ── Sección 1: Subida e Ingesta Incremental de Libros ──
        st.markdown("### :material/upload_file: Subir e Indexar Nuevo Libro (.txt)")
        st.markdown("El sistema procesa **únicamente el libro subido** sin recalcular los anteriores, optimizando tiempo y memoria.")

        with st.container(key="card_upload_book", border=True):
            uploaded_file = st.file_uploader("Selecciona el archivo de texto del libro (.txt)", type=['txt'], key="admin_file_uploader")
            
            if uploaded_file is not None:
                # Sanitizar nombre de archivo
                safe_filename = os.path.basename(uploaded_file.name).replace("..", "").strip()
                raw_dir = os.path.join(base_dir, "data", "raw")
                os.makedirs(raw_dir, exist_ok=True)
                save_path = os.path.join(raw_dir, safe_filename)

                # Guardar archivo en disco
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Detección inicial de metadatos sugeridos
                detected_meta = ingest.parse_filename_metadata(safe_filename)
                
                st.markdown("#### Confirmar Metadatos del Libro")
                c_title, c_author = st.columns(2)
                with c_title:
                    book_title = st.text_input("Título de la obra", value=detected_meta["title"], key="adm_in_title")
                with c_author:
                    book_author = st.text_input("Autor", value=detected_meta["author"], key="adm_in_author")
                
                book_topics = st.text_input(
                    "Temas clave (separados por coma)",
                    value="Economía, Libertad, Filosofía, Estado",
                    key="adm_in_topics",
                    help="Estos temas aparecerán en los filtros para inspirar posteos editoriales."
                )

                if st.button("Procesar e Indexar Libro", icon=":material/rocket_launch:", type="primary", use_container_width=True):
                    prog_bar = st.progress(0, text="Iniciando procesamiento incremental...")
                    
                    def update_progress(pct: float, message: str):
                        prog_bar.progress(int(pct * 100), text=message)

                    try:
                        result = ingest.ingest_single_book(
                            save_path,
                            custom_title=book_title,
                            custom_author=book_author,
                            custom_topics=book_topics,
                            progress_callback=update_progress
                        )

                        if result["status"] == "success":
                            st.success(f"¡Éxito! El libro '{result['title']}' de {result['author']} fue indexado con {result['chunks']} fragmentos.")
                            st.cache_data.clear()
                            st.cache_resource.clear()
                        elif result["status"] == "skipped":
                            st.info(result.get("message", "El libro ya estaba indexado."))
                        else:
                            st.error(f"Error durante la indexación: {result.get('message')}")
                    except Exception as e:
                        st.error(f"Error procesando el libro: {e}")

        # ── Sección 2: Gestión Directa de Autores y Temas ──
        st.divider()
        st.markdown("### :material/group_add: Alta Rápida de Autor y Tópicos")
        st.markdown("Agrega autores y temas conceptuales para enriquecer los filtros de generación de contenido.")

        with st.container(key="card_author_admin", border=True):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                new_author_name = st.text_input("Nombre del Autor", placeholder="Ej: Jesús Huerta de Soto", key="adm_new_auth")
            with col_a2:
                new_author_topics = st.text_input("Temas clave (separados por coma)", placeholder="Ej: Escuela Austríaca, Dinero, Banca, Ciclos Económicos", key="adm_new_topics")

            if st.button("Guardar Autor", icon=":material/save:", type="primary", use_container_width=True, key="btn_save_author"):
                if new_author_name.strip():
                    db.upsert_author(new_author_name.strip(), new_author_topics.strip())
                    st.success(f"Autor '{new_author_name}' guardado exitosamente.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("Por favor ingresa al menos el nombre del autor.")
