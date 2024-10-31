import os
import json
import tkinter as tk
from tkinter import filedialog
import pandas as pd


def count_labels_in_folder(input_folder):
    # 결과를 저장할 리스트 초기화
    results = []

    # 폴더 내의 하위 폴더들을 순회
    for folder_name in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder_name)

        # 폴더가 실제 디렉토리인지 확인
        if os.path.isdir(folder_path):
            formula_count = 0
            table_count = 0

            # 하위 폴더 내의 파일들을 순회
            for filename in os.listdir(folder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(folder_path, filename)

                    # JSON 파일 열기
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            # FORMULA와 TABLE 레이블 개수 확인
                            for shape in data.get('shapes', []):
                                if shape.get('label') == 'FORMULA':
                                    formula_count += 1
                                elif shape.get('label') == 'TABLE':
                                    table_count += 1

                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {file_path}")
                # 결과 출력
            print(f"Folder: {folder_name}")
            print(f" - FORMULA count: {formula_count}")
            print(f" - TABLE count: {table_count}")
            print()
            # 결과를 리스트에 추가
            results.append({"폴더명": folder_name, "FORMULA": formula_count, "TABLE": table_count})

    return results


if __name__ == "__main__":
    # tkinter 기본 창 숨기기
    root = tk.Tk()
    root.withdraw()  # 기본 창을 숨김

    # input 폴더 선택
    input_folder = filedialog.askdirectory(title="Select the input folder")
    if not input_folder:
        print("No input folder selected. Exiting...")
    else:
        # 폴더 내 FORMULA와 TABLE 개수 카운트
        results = count_labels_in_folder(input_folder)

        # 결과를 DataFrame으로 변환하여 Excel로 저장
        df = pd.DataFrame(results, columns=["폴더명", "FORMULA", "TABLE"])
        output_file = "LATEX완료_ocr.xlsx"
        df.to_excel(output_file, index=False)

        print(f"Results saved to {output_file}")
