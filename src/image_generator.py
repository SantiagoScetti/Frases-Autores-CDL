import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

def generate_social_media_image(quote_text, author_text, output_path):
    """
    Generates a solid color image with the quote and author text centered.
    """
    # Configuracin bsica
    img_width, img_height = 1080, 1080
    bg_color = (25, 25, 112) # Midnight Blue
    text_color = (255, 255, 255)
    
    # Crear imagen
    img = Image.new('RGB', (img_width, img_height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Intentar cargar una fuente. Si no est, usar la por defecto
    try:
        # En Windows a veces arial.ttf funciona
        font_quote = ImageFont.truetype("arial.ttf", 60)
        font_author = ImageFont.truetype("arialbd.ttf", 45) # Bold para el autor
    except IOError:
        font_quote = ImageFont.load_default()
        font_author = ImageFont.load_default()

    # Envolver texto
    wrapper = textwrap.TextWrapper(width=35) # ajustar segn la fuente
    wrapped_quote = wrapper.fill(text=quote_text)
    
    # Calcular tamaos (usamos textbbox en lugar de textsize que est deprecado)
    quote_bbox = draw.textbbox((0, 0), wrapped_quote, font=font_quote)
    quote_w = quote_bbox[2] - quote_bbox[0]
    quote_h = quote_bbox[3] - quote_bbox[1]
    
    author_bbox = draw.textbbox((0, 0), f"- {author_text}", font=font_author)
    author_w = author_bbox[2] - author_bbox[0]
    author_h = author_bbox[3] - author_bbox[1]
    
    # Calcular posiciones
    total_h = quote_h + 50 + author_h
    start_y = (img_height - total_h) // 2
    
    # Dibujar Cita
    draw.multiline_text(
        ((img_width - quote_w) // 2, start_y), 
        wrapped_quote, 
        font=font_quote, 
        fill=text_color, 
        align='center'
    )
    
    # Dibujar Autor
    draw.text(
        ((img_width - author_w) // 2, start_y + quote_h + 50), 
        f"- {author_text}", 
        font=font_author, 
        fill=(200, 200, 200) # Un gris claro
    )
    
    # Guardar
    img.save(output_path)
    return output_path
