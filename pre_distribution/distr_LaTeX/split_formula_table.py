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


def check_and_save_json_files(folder_list, output_folder_formula, output_folder_table):
    # FORMULA와 TABLE 각각의 output_folder가 없으면 생성
    if not os.path.exists(output_folder_formula):
        os.makedirs(output_folder_formula)

    if not os.path.exists(output_folder_table):
        os.makedirs(output_folder_table)

    # 선택된 폴더 목록을 순회
    for folder in folder_list:
        folder_name = os.path.basename(folder)
        print(folder_name)

        matching_rows = [(row['시작번호(pdf)'], row['끝번호(pdf)']) for _, row in df.iterrows() if str(row['파일명']) in folder_name ]
        start_page, end_page = matching_rows[0]

        print("folder_name : " + folder_name + ",  start_page : " + str(start_page) + ",  end_page : " + str(end_page))


        for root, dirs, files in os.walk(folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                if os.path.getsize(file_path) == 0:  # 파일 크기가 0인 경우
                    print(f"Empty file detected: {file_path}")

                if filename.endswith(".json"):
                    # 파일명을 "_"를 기준으로 분리하고 마지막 부분에서 ".json"을 제거
                    parts = filename.split("_")
                    if len(parts) > 1:
                        page_number_str = parts[-1].replace(".json", "")  # 마지막 부분에서 ".json" 제거
                        page_number = int(page_number_str)  # 페이지 번호를 정수로 변환

                        # 페이지 번호가 시작 번호와 끝 번호 사이에 있지 않으면 continue
                        if page_number < start_page or page_number > end_page:
                            continue


                    file_path = os.path.join(root, filename)

                    # JSON 파일 열기
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)

                        # TABLE 레이블이 있는지 확인
                        found_table = any(shape['label'] == 'TABLE' for shape in data['shapes'])

                        # FORMULA 레이블이 있는지 확인
                        found_formula = any(shape['label'] == 'FORMULA' for shape in data['shapes'])

                        # TABLE이 있으면 파일을 output_folder_table에 저장 (FORMULA는 저장하지 않음)
                        if found_table:
                            shutil.copy(file_path, os.path.join(output_folder_table, filename))
                            # 이미지도 동일한 폴더로 복사
                            image_name = os.path.splitext(filename)[0] + '.png'  # JSON 파일명과 동일한 이름의 이미지
                            image_path = os.path.join(root, image_name)  # 각 하위 폴더 안에서 이미지 파일 찾기
                            if os.path.exists(image_path):
                                shutil.copy(image_path, os.path.join(output_folder_table, image_name))

                        # FORMULA가 있으면 파일을 output_folder_formula에 저장
                        elif found_formula:
                            shutil.copy(file_path, os.path.join(output_folder_formula, filename))
                            # 이미지도 동일한 폴더로 복사
                            image_name = os.path.splitext(filename)[0] + '.png'  # JSON 파일명과 동일한 이름의 이미지
                            image_path = os.path.join(root, image_name)  # 각 하위 폴더 안에서 이미지 파일 찾기
                            if os.path.exists(image_path):
                                shutil.copy(image_path, os.path.join(output_folder_formula, image_name))


def group_folders_and_process(input_folder, output_base_folder):

    ocr_folders = [folder for folder in os.listdir(input_folder)]   # if folder.endswith('_ocr')  _ocr로 끝나는 폴더만 찾기

    # n개씩 묶어서 처리
    for i in range(0, len(ocr_folders), 20):
        group = ocr_folders[i:i + 20]

        if len(group) == 0:
            continue

        # 출력 폴더 이름 생성 (폴더 이름에서 앞 번호 추출: _로 구분된 첫 번째 부분 사용)
        folder_numbers = [folder.split('_')[0].lstrip('0') for folder in group]
        output_folder_name = '_'.join(folder_numbers)

        # 그룹 폴더 생성 (output_base_folder 내부에 7_13_14와 같은 폴더 생성)
        output_group_folder = os.path.join(output_base_folder, output_folder_name)

        # FORMULA와 TABLE 각각의 출력 폴더 경로 설정 (그룹 폴더 내부에 formula와 table 폴더 생성)
        output_folder_formula = os.path.join(output_group_folder, f"{output_folder_name}_formula")
        output_folder_table = os.path.join(output_group_folder, f"{output_folder_name}_table")

        # 그룹 폴더 생성
        if not os.path.exists(output_group_folder):
            os.makedirs(output_group_folder)

        # 묶인 폴더들에 대해 JSON 검사 및 복사 실행
        folder_paths = [os.path.join(input_folder, folder) for folder in group]
        check_and_save_json_files(folder_paths, output_folder_formula, output_folder_table)


if __name__ == "__main__":
    # tkinter 기본 창 숨기기
    root = tk.Tk()
    root.withdraw()  # 기본 창을 숨김

    # input 폴더 선택 (OCR JSON 파일이 들어있는 폴더 선택)
    input_folder = filedialog.askdirectory(title="Select the input folder")
    if not input_folder:
        print("No input folder selected. Exiting...")
        exit()

    # output 폴더를 현재 프로젝트 내의 'output' 폴더로 설정
    output_base_folder = os.path.join(os.getcwd(), './LaTeX업로드')
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)

    # 폴더 그룹화 및 JSON과 이미지 처리 실행
    group_folders_and_process(input_folder, output_base_folder)
