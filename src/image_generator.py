import os
import re
import io
import textwrap
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_REGULAR_PATH = os.path.join(FONTS_DIR, "Roboto-Regular.ttf")
FONT_BOLD_PATH = os.path.join(FONTS_DIR, "Roboto-Bold.ttf")

def clean_emojis(text):
    if not text:
        return ""
    emoji_pattern = re.compile(
        r'[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002300-\U000023FF\U00002B50-\U00002B55\U0000FE00-\U0000FE0F]+'
    )
    return emoji_pattern.sub('', str(text)).strip()

def _load_fonts(quote_size=52, author_size=40):
    """Carga fuentes Open Source empaquetadas (Roboto) compatibles con Linux y Windows."""
    try:
        if os.path.exists(FONT_REGULAR_PATH) and os.path.exists(FONT_BOLD_PATH):
            font_quote = ImageFont.truetype(FONT_REGULAR_PATH, quote_size)
            font_author = ImageFont.truetype(FONT_BOLD_PATH, author_size)
            return font_quote, font_author
    except Exception:
        pass

    # Fallbacks del sistema operativo
    system_fallbacks = ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    for fb in system_fallbacks:
        try:
            return ImageFont.truetype(fb, quote_size), ImageFont.truetype(fb, author_size)
        except IOError:
            continue

    return ImageFont.load_default(), ImageFont.load_default()

def generate_social_media_image(quote_text, author_text, output_path=None):
    """
    Genera una placa gráfica editorial cuadrada (1080x1080) para redes sociales.
    Retorna bytes de la imagen en formato PNG (en memoria) y opcionalmente guarda en output_path.
    """
    clean_quote = clean_emojis(quote_text).strip('"“«”»')
    clean_author = clean_emojis(author_text).strip('—-– ')
    
    img_width, img_height = 1080, 1080
    bg_color = (18, 24, 38)        # Deep Slate Navy
    text_color = (248, 249, 250)    # Blanco editorial
    author_color = (232, 93, 4)     # Naranja institucional CDL (#E85D04)
    frame_color = (36, 48, 74)      # Borde sutil

    img = Image.new('RGB', (img_width, img_height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Marco editorial sutil
    margin = 50
    draw.rectangle(
        [(margin, margin), (img_width - margin, img_height - margin)],
        outline=frame_color,
        width=2
    )

    # Ajuste dinámico de tamaño de fuente según longitud de cita
    quote_len = len(clean_quote)
    if quote_len > 300:
        quote_size = 36
        author_size = 30
        wrap_width = 46
    elif quote_len > 180:
        quote_size = 44
        author_size = 34
        wrap_width = 38
    else:
        quote_size = 54
        author_size = 38
        wrap_width = 32

    font_quote, font_author = _load_fonts(quote_size=quote_size, author_size=author_size)

    # Envolver texto
    wrapped_quote = f"“{textwrap.fill(clean_quote, width=wrap_width)}”"
    author_display = f"— {clean_author.upper()} —" if clean_author else "— CLUB DE LA LIBERTAD —"

    # Medición de dimensiones
    quote_bbox = draw.multiline_textbbox((0, 0), wrapped_quote, font=font_quote, align="center")
    quote_w = quote_bbox[2] - quote_bbox[0]
    quote_h = quote_bbox[3] - quote_bbox[1]

    author_bbox = draw.textbbox((0, 0), author_display, font=font_author)
    author_w = author_bbox[2] - author_bbox[0]
    author_h = author_bbox[3] - author_bbox[1]

    # Distribución vertical centrada
    spacing = 60
    total_h = quote_h + spacing + author_h
    start_y = max(margin + 40, (img_height - total_h) // 2)

    # Dibujar Cita
    draw.multiline_text(
        ((img_width - quote_w) // 2, start_y),
        wrapped_quote,
        font=font_quote,
        fill=text_color,
        align='center'
    )

    # Dibujar Autor con color de acento
    draw.text(
        ((img_width - author_w) // 2, start_y + quote_h + spacing),
        author_display,
        font=font_author,
        fill=author_color
    )

    # Guardar en memoria BytesIO
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", quality=95)
    img_bytes = buffer.getvalue()

    # Si se especificó output_path, guardar también en disco
    if output_path:
        with open(output_path, "wb") as f:
            f.write(img_bytes)

    return img_bytes
