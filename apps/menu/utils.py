import qrcode
import os
from django.conf import settings

def generate_table_qr(table_number):
    """
    Generates a table-specific QR code routing directly to the digital menu.
    Saves it to the media folder and returns the file path.
    """
    url = f"{settings.BASE_URL}/menu/?table={table_number}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', f'table_{table_number}.png')
    
    # Ensure directory structure exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path
