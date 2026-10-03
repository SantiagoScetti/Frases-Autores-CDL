import os
import re
import io
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
BRANDING_DIR = os.path.join(BASE_DIR, "assets", "branding")

FONT_REGULAR = os.path.join(FONTS_DIR, "Roboto-Regular.ttf")
FONT_BOLD = os.path.join(FONTS_DIR, "Roboto-Bold.ttf")
FONT_SERIF = os.path.join(FONTS_DIR, "EBGaramond.ttf")
FONT_SCRIPT = os.path.join(FONTS_DIR, "DancingScript.ttf")

TORCH_PATH = os.path.join(BRANDING_DIR, "torch_transparente.png")

# Paletas de Color Editoriales Predefinidas
COLOR_PALETTES = {
    "Azul Institucional (Navy)": {
        "top": (11, 19, 43),       # #0B132B
        "bottom": (28, 37, 65),    # #1C2541
        "text_quote": (255, 255, 255),
        "text_sub": (200, 215, 240),
        "accent": (79, 168, 255),  # Celeste zafiro
        "corner": (232, 93, 4),    # Naranja CDL
        "frame": (255, 255, 255, 35)
    },
    "Naranja Institucional": {
        "top": (180, 65, 0),       # #B44100
        "bottom": (232, 93, 4),    # #E85D04
        "text_quote": (255, 255, 255),
        "text_sub": (255, 235, 215),
        "accent": (255, 230, 110), # Amarillo suave
        "corner": (255, 255, 255),
        "frame": (255, 255, 255, 45)
    },
    "Borgoña Clásico": {
        "top": (42, 10, 18),       # #2A0A12
        "bottom": (74, 18, 28),    # #4A121C
        "text_quote": (255, 255, 255),
        "text_sub": (240, 210, 220),
        "accent": (235, 175, 110), # Oro suave
        "corner": (232, 93, 4),
        "frame": (255, 255, 255, 35)
    },
    "Verde Botella": {
        "top": (10, 28, 20),       # #0A1C14
        "bottom": (20, 52, 38),    # #143426
        "text_quote": (255, 255, 255),
        "text_sub": (210, 235, 220),
        "accent": (110, 225, 175), # Menta suave
        "corner": (232, 93, 4),
        "frame": (255, 255, 255, 35)
    },
    "Negro Azabache": {
        "top": (14, 14, 16),       # #0E0E10
        "bottom": (26, 28, 34),    # #1A1C22
        "text_quote": (255, 255, 255),
        "text_sub": (180, 190, 205),
        "accent": (232, 93, 4),    # Naranja CDL
        "corner": (232, 93, 4),
        "frame": (255, 255, 255, 30)
    },
    "Crema Marfil (Luz)": {
        "top": (245, 240, 232),    # #F5F0E8
        "bottom": (251, 249, 245), # #FBF9F5
        "text_quote": (15, 23, 42),# Tinta oscura
        "text_sub": (71, 85, 105),
        "accent": (232, 93, 4),    # Naranja CDL
        "corner": (232, 93, 4),
        "frame": (15, 23, 42, 30)
    }
}

def clean_emojis(text):
    if not text:
        return ""
    emoji_pattern = re.compile(
        r'[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002300-\U000023FF\U00002B50-\U00002B55\U0000FE00-\U0000FE0F]+'
    )
    return emoji_pattern.sub('', str(text)).strip()

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[áàäâ]', 'a', text)
    text = re.sub(r'[éèëê]', 'e', text)
    text = re.sub(r'[íìïî]', 'i', text)
    text = re.sub(r'[óòöô]', 'o', text)
    text = re.sub(r'[úùüû]', 'u', text)
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def split_author_name(author_str):
    clean = clean_emojis(author_str).strip('—-– ')
    if not clean:
        return "", "CLUB DE LA LIBERTAD"
    if '(' in clean: clean = clean.split('(')[0].strip()
    if '-' in clean: clean = clean.split('-')[0].strip()
        
    parts = clean.split()
    if len(parts) == 1:
        return "", parts[0].upper()
    elif len(parts) == 2:
        return parts[0], parts[1].upper()
    else:
        first = " ".join(parts[:-1])
        surname = parts[-1].upper()
        return first, surname

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generate_social_media_image(
    quote_text,
    author_text="Club de la Libertad",
    header_category=None,
    color_palette="Azul Institucional (Navy)",
    custom_hex=None,
    format_type="story",
    font_style="serif",
    output_path=None
):
    """
    Genera una placa gráfica editorial limpia y elegante para redes sociales.
    - Cero fotos/recortes humanos (tipografía e isotipo oficial de la antorcha).
    - format_type: 'story' (1080x1920) o 'square' (1080x1080).
    - color_palette: Clave en COLOR_PALETTES o hex si custom_hex está definido.
    """
    clean_quote = clean_emojis(quote_text).strip('"“«”»\'')
    first_name, surname = split_author_name(author_text)
    
    if format_type == "story":
        W, H = 1080, 1920
    else:
        W, H = 1080, 1080

    # ── Paleta de Color ──
    palette = COLOR_PALETTES.get(color_palette, COLOR_PALETTES["Azul Institucional (Navy)"])
    if custom_hex:
        try:
            base_rgb = hex_to_rgb(custom_hex)
            dark_rgb = tuple(max(0, c - 30) for c in base_rgb)
            palette = {
                "top": dark_rgb,
                "bottom": base_rgb,
                "text_quote": (255, 255, 255),
                "text_sub": (220, 230, 245),
                "accent": (232, 93, 4),
                "corner": (232, 93, 4),
                "frame": (255, 255, 255, 35)
            }
        except Exception:
            pass

    # ── 1. Fondo Gradiente Suave ──
    bg_arr = np.zeros((H, W, 3), dtype=np.uint8)
    top_c = palette["top"]
    bot_c = palette["bottom"]
    for y in range(H):
        t = y / H
        r = int(top_c[0] * (1 - t) + bot_c[0] * t)
        g = int(top_c[1] * (1 - t) + bot_c[1] * t)
        b = int(top_c[2] * (1 - t) + bot_c[2] * t)
        bg_arr[y, :] = [r, g, b]

    canvas = Image.fromarray(bg_arr).convert('RGBA')
    draw = ImageDraw.Draw(canvas)

    # ── 2. Marco Editorial con Esquineros ──
    margin = 55 if format_type == "story" else 45
    draw.rectangle([(margin, margin), (W - margin, H - margin)], outline=palette["frame"], width=2)
    
    c_len = 32
    corner_col = palette["corner"]
    # 4 esquineros
    draw.line([(margin, margin), (margin + c_len, margin)], fill=corner_col, width=3)
    draw.line([(margin, margin), (margin, margin + c_len)], fill=corner_col, width=3)
    draw.line([(W - margin, margin), (W - margin - c_len, margin)], fill=corner_col, width=3)
    draw.line([(W - margin, margin), (W - margin, margin + c_len)], fill=corner_col, width=3)
    draw.line([(margin, H - margin), (margin + c_len, H - margin)], fill=corner_col, width=3)
    draw.line([(margin, H - margin), (margin, H - margin - c_len)], fill=corner_col, width=3)
    draw.line([(W - margin, H - margin), (W - margin - c_len, H - margin)], fill=corner_col, width=3)
    draw.line([(W - margin, H - margin), (W - margin, H - margin - c_len)], fill=corner_col, width=3)

    # ── 3. Tipografías ──
    if format_type == "story":
        cat_size = 28
        first_size = 56
        surname_size = 96
        header_y = 130
        foot_torch_h = 115
        foot_y = 1560
        max_q_w = 26
    else:
        cat_size = 24
        first_size = 46
        surname_size = 80
        header_y = 90
        foot_torch_h = 75
        foot_y = 810
        max_q_w = 30

    font_cat = ImageFont.truetype(FONT_REGULAR, cat_size)
    font_first = ImageFont.truetype(FONT_SERIF, first_size)
    font_surname = ImageFont.truetype(FONT_BOLD, surname_size)

    # ── 4. Encabezado / Autor ──
    cat_text = (header_category or "PENSADORES DE LA LIBERTAD").upper()
    draw.text((margin + 45, header_y), cat_text, font=font_cat, fill=palette["text_sub"])

    curr_y = header_y + int(cat_size * 1.6)
    if first_name:
        draw.text((margin + 45, curr_y), first_name, font=font_first, fill=palette["text_quote"])
        curr_y += int(first_size * 1.1)

    draw.text((margin + 45, curr_y), surname, font=font_surname, fill=palette["accent"])
    
    # Línea decorativa bajo el autor
    line_y = curr_y + surname_size + 15
    draw.line([(margin + 45, line_y), (margin + 175, line_y)], fill=palette["corner"], width=4)

    # ── 5. Cita Central ──
    q_len = len(clean_quote)
    if format_type == "story":
        if q_len > 240:
            quote_size = 50
            wrap_width = 28
            line_spacing = 20
        elif q_len > 130:
            quote_size = 58
            wrap_width = 24
            line_spacing = 22
        else:
            quote_size = 66
            wrap_width = 21
            line_spacing = 24
    else:
        if q_len > 240:
            quote_size = 38
            wrap_width = 34
            line_spacing = 14
        elif q_len > 130:
            quote_size = 44
            wrap_width = 28
            line_spacing = 16
        else:
            quote_size = 52
            wrap_width = 24
            line_spacing = 18

    # Selección de tipografía para la cita
    if font_style == "script":
        font_quote = ImageFont.truetype(FONT_SCRIPT, quote_size + 4)
    else:
        font_quote = ImageFont.truetype(FONT_SERIF, quote_size)

    wrapped_quote = f"“{textwrap.fill(clean_quote, width=wrap_width)}”"
    bbox = draw.multiline_textbbox((0, 0), wrapped_quote, font=font_quote, spacing=line_spacing, align="center")
    qw = bbox[2] - bbox[0]
    qh = bbox[3] - bbox[1]

    # Centrado vertical en el espacio disponible entre el header y el footer
    area_top = line_y + 40
    area_bottom = foot_y - 30
    quote_y = area_top + max(0, (area_bottom - area_top - qh) // 2)

    draw.multiline_text(
        ((W - qw) // 2, quote_y),
        wrapped_quote,
        font=font_quote,
        fill=palette["text_quote"],
        spacing=line_spacing,
        align="center"
    )

    # ── 6. Footer con Antorcha Oficial y Firma Institucional ──
    if os.path.exists(TORCH_PATH):
        try:
            torch_img = Image.open(TORCH_PATH).convert('RGBA')
            tw = int(torch_img.width * (foot_torch_h / torch_img.height))
            torch_img = torch_img.resize((tw, foot_torch_h), Image.Resampling.LANCZOS)
            canvas.paste(torch_img, ((W - tw) // 2, foot_y), torch_img)
        except Exception:
            pass

    font_foot_sm = ImageFont.truetype(FONT_REGULAR, 22 if format_type == "story" else 18)
    font_foot_bold = ImageFont.truetype(FONT_BOLD, 32 if format_type == "story" else 26)

    t1 = "FUNDACIÓN"
    t2 = "CLUB DE LA LIBERTAD"
    t3 = "CORRIENTES · ARGENTINA"

    b1 = draw.textbbox((0, 0), t1, font=font_foot_sm)
    b2 = draw.textbbox((0, 0), t2, font=font_foot_bold)
    b3 = draw.textbbox((0, 0), t3, font=font_foot_sm)

    base_text_y = foot_y + foot_torch_h + (18 if format_type == "story" else 12)
    draw.text(((W - (b1[2] - b1[0])) // 2, base_text_y), t1, font=font_foot_sm, fill=palette["text_sub"])
    draw.text(((W - (b2[2] - b2[0])) // 2, base_text_y + (28 if format_type == "story" else 22)), t2, font=font_foot_bold, fill=palette["text_quote"])
    draw.text(((W - (b3[2] - b3[0])) // 2, base_text_y + (68 if format_type == "story" else 52)), t3, font=font_foot_sm, fill=palette["text_sub"])

    # ── 7. Render a PNG ──
    final_img = canvas.convert('RGB')
    buffer = io.BytesIO()
    final_img.save(buffer, format="PNG", quality=95)
    img_bytes = buffer.getvalue()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(img_bytes)

    return img_bytes
