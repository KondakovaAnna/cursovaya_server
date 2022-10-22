from PIL import Image
import io

def read_image(image_data):
    return Image.open(io.BytesIO(image_data))