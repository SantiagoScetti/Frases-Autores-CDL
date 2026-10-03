"""
Módulo de Gestión de Temas (Claro / Oscuro) para el Sistema de Frases del Club de la Libertad.
Diseño editorial premium de alto impacto, contraste WCAG AAA y jerarquía visual estricta.
Soporta completamente Streamlit 1.64+ (React Aria ComboBox y Emotion cache).
"""

def get_theme_css(is_dark: bool = True) -> str:
    """Retorna el bloque CSS inyectado según el modo seleccionado con especificidad reforzada."""
    
    if is_dark:
        # Paleta Modo Oscuro (OLED Deep Slate Navy)
        bg_app = "#0B0F19"
        bg_card = "#151C2C"
        bg_panel = "#101726"
        border_card = "#253146"
        border_subtle = "#1F293D"
        text_primary = "#F8FAFC"
        text_secondary = "#CBD5E1"
        text_muted = "#94A3B8"
        brand_primary = "#E85D04"
        brand_hover = "#FF7A1A"
        brand_tint = "rgba(232, 93, 4, 0.15)"
        brand_tint_border = "rgba(232, 93, 4, 0.35)"
        brand_tint_text = "#FFBA80"
        
        quote_bg = "#111827"
        quote_border = "#FF7A1A"
        quote_text = "#E2E8F0"
        quote_highlight_bg = "rgba(245, 158, 11, 0.25)"
        quote_highlight_text = "#FDE68A"
        
        input_bg = "#1A2333"
        input_border = "#2E3D56"
        input_text = "#F8FAFC"
        
        tag_bg = "rgba(232, 93, 4, 0.22)"
        tag_border = "rgba(232, 93, 4, 0.45)"
        tag_text = "#FFBA80"
        
        badge_bg = "#1E293B"
        badge_border = "#334155"
        badge_text = "#94A3B8"
        
        shadow_card = "0 4px 14px rgba(0, 0, 0, 0.45), 0 1px 3px rgba(0, 0, 0, 0.25)"
        shadow_card_hover = "0 10px 24px rgba(0, 0, 0, 0.6), 0 2px 6px rgba(0, 0, 0, 0.35)"
        
        expander_bg = "#131926"
        btn_sec_bg = "#1A2333"
        btn_sec_border = "#2E3D56"
        btn_sec_text = "#E2E8F0"
        
        btn_destr_bg = "rgba(220, 38, 38, 0.15)"
        btn_destr_border = "rgba(220, 38, 38, 0.4)"
        btn_destr_text = "#FCA5A5"
        btn_destr_hover = "rgba(220, 38, 38, 0.25)"
        
        code_bg = "#1A2333"
        code_text = "#F8FAFC"
        code_border = "#2E3D56"
        
        seg_bg = "#111827"
        seg_border = "#253146"
        seg_unselected_text = "#94A3B8"
        
    else:
        # Paleta Modo Claro (Diseño Editorial Estructurado con Alto Contraste y Delimitación Nítida)
        bg_app = "#F1F5F9"           # Slate-100: fondo de página suave para destacar las tarjetas
        bg_card = "#FFFFFF"          # Blanco puro para tarjetas elevadas
        bg_panel = "#F8FAFC"         # Slate-50 para paneles secundarios
        border_card = "#CBD5E1"      # Slate-300: bordes nítidos y definidos (1.5px)
        border_subtle = "#E2E8F0"    # Slate-200 para divisores interiores
        text_primary = "#0F172A"     # Slate-900: legibilidad máxima
        text_secondary = "#334155"   # Slate-700
        text_muted = "#64748B"       # Slate-500
        brand_primary = "#E85D04"    # Naranja institucional Club de la Libertad
        brand_hover = "#DC4C00"
        brand_tint = "#FFF7ED"       # Orange-50
        brand_tint_border = "#FDBA74"# Orange-300
        brand_tint_text = "#9A3412"  # Orange-800
        
        quote_bg = "#F8FAFC"         # Fondo cita editorial
        quote_border = "#E85D04"     # Acento naranja institucional
        quote_text = "#1E293B"       # Slate-800 para lectura serif
        quote_highlight_bg = "#FEF3C7"
        quote_highlight_text = "#92400E"
        
        input_bg = "#FFFFFF"         # Fondo blanco puro para TODOS los inputs
        input_border = "#CBD5E1"     # Borde gris claro definido
        input_text = "#0F172A"       # Texto oscuro nítido
        
        tag_bg = "#FFF7ED"
        tag_border = "#FED7AA"
        tag_text = "#9A3412"
        
        badge_bg = "#E2E8F0"         # Slate-200
        badge_border = "#CBD5E1"     # Slate-300
        badge_text = "#334155"       # Slate-700
        
        shadow_card = "0 4px 12px -2px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04)"
        shadow_card_hover = "0 10px 25px -3px rgba(15, 23, 42, 0.12), 0 4px 10px -2px rgba(15, 23, 42, 0.06)"
        
        expander_bg = "#F8FAFC"
        btn_sec_bg = "#FFFFFF"
        btn_sec_border = "#CBD5E1"
        btn_sec_text = "#1E293B"
        
        btn_destr_bg = "#FEF2F2"
        btn_destr_border = "#FECACA"
        btn_destr_text = "#DC2626"
        btn_destr_hover = "#FEE2E2"
        
        code_bg = "#E2E8F0"
        code_text = "#0F172A"
        code_border = "#CBD5E1"
        
        seg_bg = "#E2E8F0"
        seg_border = "#CBD5E1"
        seg_unselected_text = "#475569"

    return f"""
<style>
    /* Google Fonts & Icons */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

    .material-symbols-rounded {{
        font-family: 'Material Symbols Rounded' !important;
        font-weight: normal;
        font-style: normal;
        font-size: 1.25rem;
        line-height: 1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-transform: none;
        letter-spacing: normal;
        word-wrap: normal;
        white-space: nowrap;
        direction: ltr;
        vertical-align: middle;
    }}

    /* ── Reset y Base Global con Ultra Especificidad ── */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {bg_app} !important;
        color: {text_primary} !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }}

    /* ── Eliminación del Efecto Gris y Barra Superior Animada (Cero Pantalla Lavada) ── */
    [data-stale="true"],
    [data-testid="stElementContainer"][data-stale="true"],
    .stApp[data-test-script-state="running"] [data-stale="true"],
    .stApp[data-test-script-state="running"] [data-testid="stElementContainer"],
    .stApp[data-test-script-state="running"] [data-testid="stVerticalBlock"],
    .stApp[data-test-script-state="running"] [data-testid="stHorizontalBlock"] {{
        opacity: 1 !important;
        filter: none !important;
        -webkit-filter: none !important;
        transition: none !important;
    }}

    /* Barra superior de progreso institucional (#E85D04 a #FF9E00) */
    .stApp[data-test-script-state="running"]::before,
    [data-testid="stApp"][data-test-script-state="running"]::before {{
        content: "" !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        height: 3.5px !important;
        z-index: 9999999 !important;
        background: linear-gradient(
            90deg,
            #E85D04 0%,
            #FF9E00 25%,
            #FFB703 50%,
            #FF9E00 75%,
            #E85D04 100%
        ) !important;
        background-size: 200% 100% !important;
        animation: cdlTopProgressBar 1.4s cubic-bezier(0.4, 0, 0.2, 1) infinite !important;
        box-shadow: 0 1px 12px rgba(232, 93, 4, 0.75), 0 0 5px rgba(255, 158, 0, 0.5) !important;
        pointer-events: none !important;
    }}

    @keyframes cdlTopProgressBar {{
        0% {{
            background-position: 100% 0;
        }}
        100% {{
            background-position: -100% 0;
        }}
    }}

    [data-testid="stStatusWidget"] {{
        background-color: transparent !important;
    }}
    [data-testid="stStatusWidget"] svg {{
        fill: {brand_primary} !important;
    }}

    .block-container {{
        max-width: 1440px;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
        padding-top: 1.25rem;
        padding-bottom: 3.5rem;
    }}

    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    /* ── Tipografía General ── */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_primary} !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: -0.02em;
    }}

    p, span, div {{
        color: {text_secondary};
    }}

    /* ── Labels de Formulario (Siempre Alta Legibilidad) ── */
    label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] label p,
    [data-testid="stRadio"] label span,
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] label p,
    [data-testid="stCheckbox"] label span,
    [data-testid="stSelectbox"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stSlider"] label {{
        color: {text_primary} !important;
        font-weight: 600 !important;
        font-size: 0.91rem !important;
    }}

    /* ── Encabezado Institucional ── */
    .brand-header-box {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 1.15rem 1.6rem;
        background: {bg_card} !important;
        border: 1.5px solid {border_card} !important;
        border-radius: 14px;
        box-shadow: {shadow_card};
        transition: all 0.2s ease;
    }}
    .brand-logo-icon {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 46px;
        height: 46px;
        border-radius: 12px;
        background: linear-gradient(135deg, #E85D04 0%, #FF7A1A 100%);
        color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(232, 93, 4, 0.35);
        flex-shrink: 0;
    }}
    .brand-logo-icon .material-symbols-rounded {{
        color: #FFFFFF !important;
        font-size: 26px !important;
    }}
    .brand-logo-icon svg {{
        width: 26px !important;
        height: 26px !important;
        display: block !important;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    }}
    .brand-title-group h1 {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.5rem !important;
        color: {text_primary} !important;
        margin: 0 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.02em;
    }}
    .brand-title-group p {{
        color: {text_muted} !important;
        font-size: 0.86rem !important;
        margin: 0.25rem 0 0 0 !important;
        font-weight: 500;
    }}

    /* ── Segmented Controls / Button Group (Streamlit 1.40+ & 1.64+) ── */
    html body .stApp [data-testid="stSegmentedControl"],
    html body .stApp [data-testid="stButtonGroup"]:has(button[data-variant="segmented_control"]),
    html body .stApp .stButtonGroup:has(button[data-variant="segmented_control"]),
    html body .stApp [class*="theme_mode_selector"] [data-testid="stButtonGroup"],
    html body .stApp [class*="theme_mode_selector"] .stButtonGroup {{
        background-color: {seg_bg} !important;
        border: 1.5px solid {seg_border} !important;
        border-radius: 9999px !important;
        padding: 3px !important;
        box-shadow: none !important;
        gap: 0 !important;
    }}

    html body .stApp [data-testid="stSegmentedControl"] [data-baseweb="button-group"],
    html body .stApp [data-testid="stButtonGroup"] > div,
    html body .stApp .stButtonGroup > div {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 9999px !important;
        gap: 4px !important;
        padding: 0 !important;
    }}

    /* Botón Inactivo: fondo transparente, sin bordes ni sombras de stBaseButton-secondary */
    html body .stApp [data-testid="stSegmentedControl"] button:not([aria-checked="true"]):not([data-selected]),
    html body .stApp [data-testid="stButtonGroup"] button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]),
    html body .stApp .stButtonGroup button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]),
    html body .stApp button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]),
    html body .stApp button[data-variant="segmented_control"][kind="segmented_control"],
    html body .stApp [class*="theme_mode_selector"] button:not([data-selected]):not([aria-checked="true"]) {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
        color: {seg_unselected_text} !important;
        -webkit-text-fill-color: {seg_unselected_text} !important;
        border-radius: 9999px !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        padding: 0.4rem 1.05rem !important;
        margin: 0 !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }}

    html body .stApp [data-testid="stSegmentedControl"] button:not([aria-checked="true"]):not([data-selected]) *,
    html body .stApp [data-testid="stButtonGroup"] button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]) *,
    html body .stApp .stButtonGroup button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]) *,
    html body .stApp button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]) * {{
        color: {seg_unselected_text} !important;
        -webkit-text-fill-color: {seg_unselected_text} !important;
        fill: {seg_unselected_text} !important;
    }}

    html body .stApp [data-testid="stSegmentedControl"] button:not([aria-checked="true"]):not([data-selected]):hover,
    html body .stApp [data-testid="stButtonGroup"] button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]):hover,
    html body .stApp .stButtonGroup button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]):hover,
    html body .stApp button[data-variant="segmented_control"]:not([data-selected]):not([aria-checked="true"]):hover {{
        background-color: {brand_tint} !important;
        color: {text_primary} !important;
        -webkit-text-fill-color: {text_primary} !important;
        border: none !important;
    }}

    /* Botón Activo: Naranja Institucional #E85D04 con texto blanco nítido */
    html body .stApp [data-testid="stSegmentedControl"] button[aria-checked="true"],
    html body .stApp [data-testid="stSegmentedControl"] button[data-selected],
    html body .stApp [data-testid="stButtonGroup"] button[data-variant="segmented_control"][data-selected],
    html body .stApp [data-testid="stButtonGroup"] button[data-variant="segmented_control"][aria-checked="true"],
    html body .stApp .stButtonGroup button[data-variant="segmented_control"][data-selected],
    html body .stApp .stButtonGroup button[data-variant="segmented_control"][aria-checked="true"],
    html body .stApp button[data-variant="segmented_control"][data-selected],
    html body .stApp button[data-variant="segmented_control"][aria-checked="true"],
    html body .stApp button[data-variant="segmented_control"][kind="segmented_controlActive"],
    html body .stApp [class*="theme_mode_selector"] button[data-selected],
    html body .stApp [class*="theme_mode_selector"] button[aria-checked="true"] {{
        background-color: #E85D04 !important;
        background: #E85D04 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: none !important;
        border-color: transparent !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.84rem !important;
        padding: 0.4rem 1.05rem !important;
        box-shadow: 0 2px 6px rgba(232, 93, 4, 0.4) !important;
        transition: all 0.15s ease !important;
        margin: 0 !important;
    }}

    html body .stApp [data-testid="stSegmentedControl"] button[aria-checked="true"] *,
    html body .stApp [data-testid="stButtonGroup"] button[data-variant="segmented_control"][data-selected] *,
    html body .stApp [data-testid="stButtonGroup"] button[data-variant="segmented_control"][aria-checked="true"] *,
    html body .stApp .stButtonGroup button[data-variant="segmented_control"][data-selected] *,
    html body .stApp button[data-variant="segmented_control"][data-selected] *,
    html body .stApp button[data-variant="segmented_control"][aria-checked="true"] *,
    html body .stApp button[data-variant="segmented_control"][kind="segmented_controlActive"] * {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        fill: #FFFFFF !important;
        font-weight: 700 !important;
    }}

    /* ── Pestañas de Navegación ── */
    html body .stApp .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        border-bottom: 2px solid {border_card} !important;
        padding-bottom: 4px;
        background: transparent !important;
    }}
    html body .stApp .stTabs [data-baseweb="tab"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.94rem !important;
        color: {text_muted} !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0.75rem 1.35rem !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.15s ease !important;
    }}
    html body .stApp .stTabs [data-baseweb="tab"]:hover {{
        color: {brand_primary} !important;
        background: {brand_tint} !important;
    }}
    html body .stApp .stTabs [aria-selected="true"] {{
        color: {brand_primary} !important;
        border-bottom: 3px solid {brand_primary} !important;
        background: transparent !important;
    }}
    html body .stApp .stTabs [aria-selected="true"] * {{
        color: {brand_primary} !important;
        font-weight: 700 !important;
    }}

    /* ── Elevación y Estructura de Tarjetas (Bento Grid) ── */
    html body .stApp [class*="st-key-card_"],
    html body .stApp [data-testid="stVerticalBlockBorderWrapper"],
    html body .stApp [data-testid="stColumn"] [data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] {{
        border-radius: 14px !important;
        box-shadow: {shadow_card} !important;
        border: 1.5px solid {border_card} !important;
        background-color: {bg_card} !important;
        padding: 1.35rem !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    html body .stApp [class*="st-key-card_"] > div[data-testid="stVerticalBlock"] {{
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }}
    html body .stApp [class*="st-key-card_"]:hover,
    html body .stApp [data-testid="stVerticalBlockBorderWrapper"]:hover,
    html body .stApp [data-testid="stColumn"] [data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:hover {{
        border-color: {brand_tint_border} !important;
        box-shadow: {shadow_card_hover} !important;
    }}

    /* ── Inputs y Textareas ── */
    html body .stApp [data-testid="stTextInput"] input,
    html body .stApp [data-testid="stTextArea"] textarea {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1.5px solid {input_border} !important;
        border-radius: 9px !important;
        font-size: 0.92rem !important;
        padding: 0.6rem 0.9rem !important;
    }}
    html body .stApp [data-testid="stTextInput"] input:focus,
    html body .stApp [data-testid="stTextArea"] textarea:focus {{
        border-color: {brand_primary} !important;
        box-shadow: 0 0 0 3px rgba(232, 93, 4, 0.18) !important;
    }}

    /* ── Selectbox (React Aria ComboBox & Baseweb) ── */
    html body .stApp [data-testid="stSelectbox"] .react-aria-ComboBox,
    html body .stApp [data-testid="stSelectbox"] .react-aria-ComboBox > div,
    html body .stApp [data-testid="stSelectbox"] div[class*="e1fp86qc0"],
    html body .stApp [data-testid="stSelectbox"] > div,
    html body .stApp [data-testid="stSelectbox"] [data-baseweb="select"],
    html body .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1.5px solid {input_border} !important;
        border-radius: 9px !important;
    }}
    html body .stApp [data-testid="stSelectbox"] input,
    html body .stApp [data-testid="stSelectbox"] input[class*="e1fp86qc1"],
    html body .stApp [data-testid="stSelectbox"] span {{
        color: {input_text} !important;
        background-color: transparent !important;
        -webkit-text-fill-color: {input_text} !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
    }}
    html body .stApp [data-testid="stSelectbox"] button,
    html body .stApp [data-testid="stSelectbox"] button[class*="e1fp86qc2"] {{
        background-color: transparent !important;
        color: {text_secondary} !important;
    }}
    html body .stApp [data-testid="stSelectbox"] svg {{
        fill: {text_secondary} !important;
        color: {text_secondary} !important;
    }}

    /* ── Multiselect (React Aria ComboBox & Baseweb) ── */
    html body .stApp [data-testid="stMultiSelect"] .react-aria-ComboBox,
    html body .stApp [data-testid="stMultiSelect"] .react-aria-ComboBox > div,
    html body .stApp [data-testid="stMultiSelect"] div[class*="e1kig3hy0"],
    html body .stApp [data-testid="stMultiSelect"] > div,
    html body .stApp [data-testid="stMultiSelect"] [data-baseweb="select"],
    html body .stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1.5px solid {input_border} !important;
        border-radius: 9px !important;
    }}
    html body .stApp [data-testid="stMultiSelect"] input {{
        color: {input_text} !important;
        background-color: transparent !important;
        -webkit-text-fill-color: {input_text} !important;
        font-size: 0.92rem !important;
    }}
    html body .stApp [data-testid="stMultiSelect"] [data-testid="stMultiSelectTagsContainer"] > span,
    html body .stApp [data-testid="stMultiSelect"] span[class*="e1kig3hy3"],
    html body .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"],
    html body .stApp [data-baseweb="tag"] {{
        background-color: {tag_bg} !important;
        border: 1px solid {tag_border} !important;
        border-radius: 6px !important;
        color: {tag_text} !important;
    }}
    html body .stApp [data-testid="stMultiSelect"] [data-testid="stMultiSelectTagsContainer"] span,
    html body .stApp [data-testid="stMultiSelect"] span[class*="e1kig3hy4"],
    html body .stApp [data-testid="stMultiSelect"] span[class*="e1kig3hy2"],
    html body .stApp [data-baseweb="tag"] span {{
        color: {tag_text} !important;
        font-weight: 600 !important;
    }}
    html body .stApp [data-testid="stMultiSelect"] svg,
    html body .stApp [data-testid="stMultiSelect"] button svg,
    html body .stApp [data-baseweb="tag"] svg {{
        fill: {tag_text} !important;
        color: {tag_text} !important;
    }}

    /* ── Popovers y Menús Desplegables ── */
    html body [data-baseweb="popover"],
    html body [data-baseweb="menu"],
    html body div[role="listbox"],
    html body div.react-aria-Popover,
    html body div.react-aria-ListBox {{
        background-color: {bg_card} !important;
        border: 1.5px solid {border_card} !important;
        box-shadow: {shadow_card_hover} !important;
        border-radius: 10px !important;
    }}
    html body [data-baseweb="menu"] li,
    html body div[role="option"],
    html body div.react-aria-ListBoxItem {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }}
    html body [data-baseweb="menu"] li:hover,
    html body div[role="option"]:hover,
    html body div[role="option"][aria-selected="true"],
    html body div.react-aria-ListBoxItem[data-hovered="true"],
    html body div.react-aria-ListBoxItem[data-selected="true"],
    html body div.react-aria-ListBoxItem:hover {{
        background-color: {brand_tint} !important;
        color: {brand_tint_text} !important;
    }}

    /* ── Estilización de Píldoras Interactivas (Sugerencias) ── */
    html body .stApp .st-key-pills_tema button,
    html body .stApp [data-testid="stPill"] button {{
        background-color: {brand_tint} !important;
        color: {brand_tint_text} !important;
        border: 1px solid {brand_tint_border} !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        font-size: 0.83rem !important;
        padding: 0.35rem 0.9rem !important;
        transition: all 0.15s ease-in-out !important;
        cursor: pointer !important;
    }}
    html body .stApp .st-key-pills_tema button:hover,
    html body .stApp [data-testid="stPill"] button:hover {{
        background-color: {brand_primary} !important;
        border-color: {brand_primary} !important;
        transform: translateY(-1px) !important;
        color: #FFFFFF !important;
    }}
    html body .stApp .st-key-pills_tema button[aria-checked="true"],
    html body .stApp [data-testid="stPill"] button[aria-checked="true"] {{
        background-color: {brand_primary} !important;
        color: #FFFFFF !important;
        border-color: {brand_primary} !important;
        box-shadow: 0 2px 6px rgba(232, 93, 4, 0.35) !important;
    }}

    /* ── File Uploader & Code Tags (Solución a Artefactos Oscuros) ── */
    html body .stApp [data-testid="stFileUploader"] {{
        background-color: transparent !important;
    }}
    html body .stApp [data-testid="stFileUploaderDropzone"] {{
        background-color: {bg_card} !important;
        border: 2px dashed {border_card} !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }}
    html body .stApp [data-testid="stFileUploaderDropzone"] * {{
        color: {text_secondary} !important;
    }}
    html body .stApp [data-testid="stFileUploaderDropzone"] button,
    html body .stApp [data-testid="stFileUploader"] button {{
        background-color: {btn_sec_bg} !important;
        border: 1.5px solid {btn_sec_border} !important;
        color: {btn_sec_text} !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }}
    html body .stApp [data-testid="stFileUploaderDropzone"] button:hover,
    html body .stApp [data-testid="stFileUploader"] button:hover {{
        background-color: {brand_tint} !important;
        border-color: {brand_primary} !important;
        color: {brand_primary} !important;
    }}

    /* Etiquetas de código inline */
    html body .stApp code,
    html body .stApp pre code,
    html body .stApp [data-testid="stMarkdownContainer"] code {{
        background-color: {code_bg} !important;
        color: {code_text} !important;
        border: 1px solid {code_border} !important;
        border-radius: 5px !important;
        padding: 2px 7px !important;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
        font-size: 0.88em !important;
        font-weight: 600 !important;
    }}

    /* ── Botones y Jerarquías ── */
    html body .stApp .stButton button {{
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.91rem !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.15s ease !important;
    }}
    html body .stApp .stButton button[kind="primary"],
    html body .stApp .stButton button[data-testid="stBaseButton-primary"] {{
        background-color: {brand_primary} !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(232, 93, 4, 0.3) !important;
    }}
    html body .stApp .stButton button[kind="primary"]:hover,
    html body .stApp .stButton button[data-testid="stBaseButton-primary"]:hover {{
        background-color: {brand_hover} !important;
        box-shadow: 0 5px 12px rgba(232, 93, 4, 0.4) !important;
        transform: translateY(-1px) !important;
    }}
    html body .stApp .stButton button[kind="secondary"],
    html body .stApp .stButton button[data-testid="stBaseButton-secondary"] {{
        background-color: {btn_sec_bg} !important;
        color: {btn_sec_text} !important;
        border: 1.5px solid {btn_sec_border} !important;
    }}
    html body .stApp .stButton button[kind="secondary"]:hover,
    html body .stApp .stButton button[data-testid="stBaseButton-secondary"]:hover {{
        border-color: {brand_primary} !important;
        color: {brand_primary} !important;
        background-color: {brand_tint} !important;
    }}

    /* Botón destructivo en Popovers */
    html body .stApp [data-testid="stPopover"] button {{
        border-radius: 8px !important;
        color: {btn_destr_text} !important;
        border: 1.5px solid {btn_destr_border} !important;
        background-color: {btn_destr_bg} !important;
        font-weight: 600 !important;
    }}
    html body .stApp [data-testid="stPopover"] button:hover {{
        background-color: {btn_destr_hover} !important;
    }}

    /* Popover Body */
    html body [data-testid="stPopoverBody"] {{
        background-color: {bg_card} !important;
        border: 1.5px solid {border_card} !important;
        color: {text_primary} !important;
        border-radius: 12px !important;
        box-shadow: {shadow_card_hover} !important;
    }}
    html body [data-testid="stPopoverBody"] * {{
        color: {text_primary} !important;
    }}

    /* ── Contenedores de Citas Editoriales (Blockquotes) ── */
    blockquote, .editorial-quote {{
        font-family: 'Merriweather', Georgia, serif !important;
        font-size: 1.14rem !important;
        font-style: italic !important;
        line-height: 1.7 !important;
        color: {quote_text} !important;
        background-color: {quote_bg} !important;
        border-left: 4px solid {quote_border} !important;
        padding: 1.1rem 1.35rem !important;
        margin: 0.9rem 0 !important;
        border-radius: 0 10px 10px 0 !important;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }}
    blockquote strong, .editorial-quote strong, .quote-highlight {{
        font-family: inherit !important;
        font-weight: 700 !important;
        color: {quote_highlight_text} !important;
        background-color: {quote_highlight_bg} !important;
        padding: 1px 6px !important;
        border-radius: 4px !important;
        font-style: normal !important;
    }}
    .quote-author {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        color: {quote_border} !important;
        font-style: normal !important;
        margin-top: 0.65rem !important;
        display: block !important;
        letter-spacing: 0.02em !important;
    }}

    /* ── Metadatos y Badges en Tarjetas ── */
    .card-meta-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        padding-bottom: 0.55rem;
        border-bottom: 1.5px solid {border_subtle};
    }}
    .card-author-title {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.98rem;
        font-weight: 700;
        color: {text_primary} !important;
        letter-spacing: -0.01em;
    }}
    .meta-pill {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        background-color: {badge_bg} !important;
        color: {badge_text} !important;
        border: 1px solid {badge_border} !important;
    }}
    .meta-date {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.75rem;
        color: {text_muted} !important;
        font-weight: 500;
    }}

    /* ── Encabezados de Columna con Conteo ── */
    .col-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid {border_card};
    }}
    .col-header h3 {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.18rem !important;
        font-weight: 700 !important;
        color: {text_primary} !important;
        margin: 0 !important;
    }}
    .count-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: {badge_bg} !important;
        color: {badge_text} !important;
        border: 1px solid {badge_border} !important;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 0.18rem 0.65rem;
    }}
    .count-badge-green {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: rgba(5, 150, 105, 0.16) !important;
        color: #059669 !important;
        border: 1px solid rgba(5, 150, 105, 0.35) !important;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 0.18rem 0.65rem;
    }}

    /* ── Acordeón / Expander (Solución definitiva para modo oscuro y claro) ── */
    html body .stApp [data-testid="stExpander"],
    html body .stApp details {{
        border: 1.5px solid {border_card} !important;
        background-color: {expander_bg} !important;
        background: {expander_bg} !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        margin-top: 0.6rem !important;
        margin-bottom: 0.6rem !important;
        overflow: hidden !important;
    }}
    html body .stApp [data-testid="stExpander"] summary,
    html body .stApp details summary,
    html body .stApp [data-testid="stExpander"] summary > div,
    html body .stApp details summary > div {{
        background-color: {expander_bg} !important;
        background: {expander_bg} !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: {text_primary} !important;
        padding: 0.65rem 1rem !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }}
    html body .stApp [data-testid="stExpander"] summary:hover,
    html body .stApp details summary:hover {{
        color: {brand_primary} !important;
        background-color: {brand_tint} !important;
        background: {brand_tint} !important;
    }}
    html body .stApp [data-testid="stExpander"] summary p,
    html body .stApp [data-testid="stExpander"] summary span,
    html body .stApp details summary p,
    html body .stApp details summary span {{
        color: inherit !important;
    }}
    html body .stApp [data-testid="stExpander"] summary svg,
    html body .stApp details summary svg {{
        fill: {brand_primary} !important;
    }}
    html body .stApp [data-testid="stExpanderDetails"],
    html body .stApp details > div:last-child {{
        background-color: {expander_bg} !important;
        background: {expander_bg} !important;
        color: {text_secondary} !important;
        padding: 0.75rem 1rem !important;
    }}

    /* Placeholders */
    ::placeholder {{
        color: {text_muted} !important;
        opacity: 0.85 !important;
    }}

    /* Separadores */
    hr, [data-testid="stDivider"] {{
        border-color: {border_card} !important;
        opacity: 0.7;
    }}

    /* ═══════════════════════════════════════════════════════════════════════════════
       4. REGLAS RESPONSIVAS COMPLETAS PARA MÓVILES (@media (max-width: 768px))
       ═══════════════════════════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {{
        /* 4.1. Reducción de márgenes laterales para maximizar pantalla */
        .block-container {{
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            padding-top: 0.85rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 100% !important;
        }}

        /* 4.2. Header Institucional y Selector de Tema en Móvil */
        html body .stApp [data-testid="stHorizontalBlock"]:has(.brand-header-box) {{
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 0.65rem !important;
            margin-bottom: 0.5rem !important;
        }}

        html body .stApp [data-testid="stHorizontalBlock"]:has(.brand-header-box) > [data-testid="stColumn"] {{
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}

        .brand-header-box {{
            padding: 0.85rem 1rem !important;
            gap: 12px !important;
            border-radius: 12px !important;
            flex-wrap: wrap !important;
            box-sizing: border-box !important;
            width: 100% !important;
        }}

        .brand-logo-icon {{
            width: 38px !important;
            height: 38px !important;
            border-radius: 10px !important;
            flex-shrink: 0 !important;
        }}

        .brand-logo-icon .material-symbols-rounded {{
            font-size: 22px !important;
        }}

        .brand-logo-icon svg {{
            width: 22px !important;
            height: 22px !important;
        }}

        .brand-title-group {{
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }}

        .brand-title-group h1 {{
            font-size: 1.18rem !important;
            line-height: 1.22 !important;
            word-break: break-word !important;
        }}

        .brand-title-group p {{
            font-size: 0.76rem !important;
            line-height: 1.3 !important;
            margin-top: 0.15rem !important;
        }}

        /* Selector de tema en móvil: 100% ancho con split 50/50 táctil */
        html body .stApp [class*="theme_mode_selector"],
        html body .stApp [data-testid="stSegmentedControl"],
        html body .stApp [data-testid="stButtonGroup"] {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}

        html body .stApp [data-testid="stSegmentedControl"] [data-baseweb="button-group"],
        html body .stApp [data-testid="stButtonGroup"] > div,
        html body .stApp .stButtonGroup > div {{
            width: 100% !important;
            display: flex !important;
        }}

        html body .stApp [data-testid="stSegmentedControl"] button,
        html body .stApp [data-testid="stButtonGroup"] button[data-variant="segmented_control"] {{
            flex: 1 1 50% !important;
            justify-content: center !important;
            padding: 0.45rem 0.6rem !important;
            font-size: 0.8rem !important;
            min-height: 40px !important;
        }}

        /* 4.3. Pestañas de Navegación con Scroll Horizontal Táctil */
        html body .stApp .stTabs [data-baseweb="tab-list"] {{
            overflow-x: auto !important;
            overflow-y: hidden !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            white-space: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
            gap: 6px !important;
            padding-bottom: 4px !important;
            padding-left: 2px !important;
            padding-right: 2px !important;
            border-bottom: 1.5px solid {border_card} !important;
        }}

        html body .stApp .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }}

        html body .stApp .stTabs [data-baseweb="tab"] {{
            font-size: 0.83rem !important;
            padding: 0.55rem 0.85rem !important;
            flex-shrink: 0 !important;
            white-space: nowrap !important;
            border-radius: 8px 8px 0 0 !important;
        }}

        /* Ocultar botones de flecha/chevron de scroll en pestañas móviles */
        html body .stApp .stTabs button[data-baseweb="button"],
        html body .stApp .stTabs [data-baseweb="tab-list"] ~ button,
        html body .stApp .stTabs [data-baseweb="tab-list"] + button,
        html body .stApp .stTabs button:not([role="tab"]) {{
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
            width: 0 !important;
            height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            background-color: transparent !important;
        }}

        /* 4.4. Columnas y Botones de Acción en Móvil */
        html body .stApp [data-testid="stHorizontalBlock"] {{
            flex-direction: column !important;
            flex-wrap: wrap !important;
            gap: 0.75rem !important;
        }}

        html body .stApp [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}

        /* Botones táctiles cómodos a ancho completo */
        html body .stApp .stButton button {{
            width: 100% !important;
            min-height: 44px !important;
            padding: 0.65rem 1rem !important;
            font-size: 0.92rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }}

        /* Tarjetas con paddings optimizados */
        html body .stApp [class*="st-key-card_"],
        html body .stApp [data-testid="stVerticalBlockBorderWrapper"],
        html body .stApp [data-testid="stColumn"] [data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] {{
            padding: 1rem 0.85rem !important;
            border-radius: 12px !important;
        }}

        /* Citas editoriales compactas en pantalla pequeña */
        blockquote, .editorial-quote {{
            padding: 0.85rem 1rem !important;
            font-size: 1.02rem !important;
            margin: 0.6rem 0 !important;
            line-height: 1.55 !important;
        }}

        .card-meta-header {{
            flex-wrap: wrap !important;
            gap: 8px !important;
        }}
    }}
</style>
"""
