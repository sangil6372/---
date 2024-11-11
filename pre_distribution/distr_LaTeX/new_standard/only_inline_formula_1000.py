import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog

import openpyxl
import pandas as pd


# Excel 파일을 불러옵니다. 파일 경로를 알맞게 수정하세요.
file_path = r"C:\Users\USER\Downloads\북센 도서 메타데이터.xlsx"

wb = openpyxl.load_workbook(file_path)
ws = wb.active

df = pd.read_excel(file_path)


def is_inline_formula(shape, text_bboxes):
    x1, y1 = shape["points"][0]
    x2, y2 = shape["points"][1]
    cx = (x1 + x2) / 2  # 수식의 x 중심 좌표
    cy = (y1 + y2) / 2  # 수식의 y 중심 좌표

    # 수식 중심이 텍스트 박스 내에 포함되는지 확인
    for tx1, ty1, tx2, ty2 in text_bboxes:
        # 항상 좌상단과 우하단을 올바르게 정하도록 min, max 사용
        left = min(tx1, tx2)
        right = max(tx1, tx2)
        top = min(ty1, ty2)
        bottom = max(ty1, ty2)

        if left <= cx <= right and top <= cy <= bottom: # 특정 수식박스가 텍스트 박스 내부에 들어가면 내부 수식
            return True

    return False


def check_and_save_json_files(folder_list, output_base_folder):
    file_count = 0
    group_number = 1

    output_folder = os.path.join(output_base_folder, f"inline_{group_number}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for folder in folder_list:
        folder_name = os.path.basename(folder)
        print(folder_name)

        matching_rows = [(row['시작번호(pdf)'], row['끝번호(pdf)']) for _, row in df.iterrows() if str(row['파일명']) in folder_name]
        start_page, end_page = matching_rows[0]

        print("folder_name : " + folder_name + ",  start_page : " + str(start_page) + ",  end_page : " + str(end_page))

        for root, dirs, files in os.walk(folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                if os.path.getsize(file_path) == 0:
                    print(f"Empty file detected: {file_path}")
                    continue

                if filename.endswith(".json"):
                    parts = filename.split("_")
                    if len(parts) > 1:
                        page_number_str = parts[-1].replace(".json", "")
                        page_number = int(page_number_str)

                        if page_number < start_page or page_number > end_page:
                            continue

                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)

                        text_bboxes = [
                            (text_shape["points"][0][0], text_shape["points"][0][1],
                             text_shape["points"][1][0], text_shape["points"][1][1])
                            for text_shape in data["shapes"]
                            if text_shape["label"] in ["TEXT", "FOOTNOTE", "REFERENCE"]
                        ]

                        found_table = any(shape['label'] == 'TABLE' for shape in data['shapes'])
                        found_formula = False
                        for shape in data['shapes'] :
                            if shape['label'] == "FORMULA":
                                if is_inline_formula(shape, text_bboxes):
                                    found_formula = True
                                else:
                                    found_formula = False
                                    break

                        if not found_table and found_formula:
                            shutil.copy(file_path, os.path.join(output_folder, filename))
                            file_count += 1

                            image_name = os.path.splitext(filename)[0] + '.png'
                            image_path = os.path.join(root, image_name)
                            if os.path.exists(image_path):
                                shutil.copy(image_path, os.path.join(output_folder, image_name))
                                file_count += 1

                            if file_count >= 2000:
                                group_number += 1
                                output_folder = os.path.join(output_base_folder, f"inline_{group_number}")
                                if not os.path.exists(output_folder):
                                    os.makedirs(output_folder)
                                file_count = 0


def group_folders_and_process(input_folder, output_base_folder):

    ocr_folders = [folder for folder in os.listdir(input_folder)]

    folder_paths = [os.path.join(input_folder, folder) for folder in ocr_folders]
    check_and_save_json_files(folder_paths, output_base_folder)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    input_folder = filedialog.askdirectory(title="Select the input folder")
    if not input_folder:
        print("No input folder selected. Exiting...")
        exit()

    output_base_folder = os.path.join(os.getcwd(), './수식1000개씩')
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)

    group_folders_and_process(input_folder, output_base_folder)
