from io import BytesIO

from base64 import b64encode


def byte_img_to_html(img):
    """
    Переводит битовое изображение в тег img для html формы
    :param img:
    :return:
    """
    a = BytesIO(img.read())

    # Получаем байты из объекта BytesIO и кодируем их в base64
    img_data = a.getvalue()
    img_base64 = b64encode(img_data).decode('utf-8')

    return img_base64
