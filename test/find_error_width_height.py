import os
import json
import re
from tkinter import filedialog
import tkinter as tk


def select_directory(dialog_title):
    root = tk.Tk()
    root.withdraw()  # Tkinter 윈도우를 숨김
    directory_path = filedialog.askdirectory(title=dialog_title)
    return directory_path


# 페이지 번호를 파일 이름에서 추출하는 함수
def extract_page_number(file_name):
    match = re.search(r'_(\d+)\.', file_name)
    return int(match.group(1)) if match else None


# 문제 있는 파일을 확인하는 함수
def find_files_with_zero_dimensions(json_folder_path):
    for json_filename in os.listdir(json_folder_path):
        if json_filename.endswith('.json'):
            json_file_path = os.path.join(json_folder_path, json_filename)

            # JSON 파일 읽기
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                extracted_data = json.load(json_file)

            # 파일 이름에서 페이지 번호 추출
            page_number = extract_page_number(json_filename)
            if page_number is None:
                print(f"페이지 번호를 추출할 수 없습니다: {json_filename}")
                continue

            # 이미지 크기가 0인지 확인
            if extracted_data.get("imageWidth") == 0 or extracted_data.get("imageHeight") == 0:
                print(f"이미지 크기가 0인 파일: {json_filename}")
                continue

            # shapes 리스트에서 points 값이 0인지 확인
            for shape in extracted_data.get("shapes", []):
                if shape["label"] in ["TEXT", "FOOTNOTE", "REFERENCE"]:
                    points = shape.get("points", [])
                    if len(points) == 2:
                        if points[0][0] == 0 or points[0][1] == 0 or points[1][0] == 0 or points[1][1] == 0:
                            print(f"포인트가 0인 블록이 있는 파일: {json_filename}")
                            break


# 폴더 경로 설정
json_folder_path = select_directory("OCR 텍스트가 저장된 JSON 파일들이 있는 폴더를 선택하세요")

# 문제 있는 파일 확인
find_files_with_zero_dimensions(json_folder_path)
