from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

# PDFを画像に変換
images = convert_from_path("input.pdf", dpi=300)

processed_images = []
for img in images:
    # OpenCVで処理するためにPIL→NumPyへ変換
    img_np = np.array(img)

    # グレースケールに変換
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # しきい値処理（指などの濃い色部分を検出）
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    # マスク処理（色のついた部分を白に）
    result = cv2.bitwise_and(img_np, img_np, mask=binary)

    # NumPy → PILに変換
    processed_images.append(Image.fromarray(result))

# 画像をPDFに保存
processed_images[0].save("output.pdf", save_all=True, append_images=processed_images[1:])
