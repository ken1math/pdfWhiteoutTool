import os
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
from tkinter import filedialog, Tk
from tqdm import tqdm
from PyPDF2 import PdfReader

def process_pdf(pdf_path):
    # まずPyPDF2でPDFを読み込み、各ページのサイズ（ポイント単位）を取得
    reader = PdfReader(pdf_path)
    pages_dimensions = []
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        media_box = page.mediabox
        # 幅・高さはポイント単位（1pt = 1/72インチ）
        width_pt = float(media_box.width)
        height_pt = float(media_box.height)
        # 300dpiでのピクセル数に変換： ピクセル数 = (ポイント / 72) * 300
        width_px = int(width_pt / 72 * 300)
        height_px = int(height_pt / 72 * 300)
        pages_dimensions.append((width_px, height_px))
    
    # PDFを画像に変換
    images = convert_from_path(pdf_path, dpi=300)
    processed_images = []
    
    # tqdmで進行状況を表示
    for i, img in tqdm(enumerate(images), total=len(images), desc="ページ処理中"):
        # PIL画像をNumPy配列に変換
        img_np = np.array(img)
        
        # 各ピクセルのRGBの最大値と最小値の差を計算し、閾値より大きければ色味があると判断
        diff = np.max(img_np, axis=-1) - np.min(img_np, axis=-1)
        threshold = 30  # この閾値で色味の有無を判定
        mask = diff > threshold
        
        # 色味があると判定されたピクセルを白に置換
        img_np[mask] = [255, 255, 255]
        
        # 変換前の各ページのサイズ（ピクセル単位）を取得（ページ毎に異なる場合にも対応）
        original_size = pages_dimensions[i] if i < len(pages_dimensions) else img.size
        
        # NumPy配列からPIL画像に戻し、元のサイズにリサイズ
        processed_img = Image.fromarray(img_np)
        processed_img = processed_img.resize(original_size, Image.LANCZOS)
        
        processed_images.append(processed_img)
    
    # Tkinterダイアログで出力先PDFの保存先を指定
    output_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               filetypes=[("PDF files", "*.pdf")])
    
    if output_path:
        # PILのsave()でPDFに保存する際、dpiパラメータを指定することでDPI情報を付与
        processed_images[0].save(output_path, save_all=True,
                                  append_images=processed_images[1:], dpi=(300, 300))
        print(f"PDFが保存されました: {output_path}")
    else:
        print("保存先が指定されませんでした。")

if __name__ == "__main__":
    # Tkinterのルートウィンドウを非表示にしてファイル選択ダイアログを表示
    root = Tk()
    root.withdraw()
    pdf_path = filedialog.askopenfilename(title="PDFファイルを選択", 
                                          filetypes=[("PDF files", "*.pdf")])
    if pdf_path:
        process_pdf(pdf_path)
    else:
        print("PDFファイルが選択されませんでした。")
