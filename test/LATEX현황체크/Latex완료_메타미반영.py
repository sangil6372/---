import os
import json
import tkinter as tk
from tkinter import filedialog
import pandas as pd


def count_labels_and_pages_by_file_base(input_folder):
    # 결과를 저장할 딕셔너리 초기화
    results = {}

    # 폴더 내의 하위 폴더들을 순회
    for folder_name in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder_name)

        # 폴더가 실제 디렉토리인지 확인
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_name}")  # 디버깅용 출력
            # 하위 폴더 내의 파일들을 순회
            for filename in os.listdir(folder_path):
                if filename.endswith(".json"):
                    # 파일명에서 기준명 추출 (페이지 번호 제외)
                    file_base = "_".join(filename.split("_")[:-1])

                    # JSON 파일 열기
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            # FORMULA와 TABLE 레이블 개수 확인
                            formula_count = sum(
                                1 for shape in data.get('shapes', []) if shape.get('label') == 'FORMULA')
                            table_count = sum(1 for shape in data.get('shapes', []) if shape.get('label') == 'TABLE')

                            # 결과 딕셔너리에 기준명 추가 또는 업데이트
                            if file_base not in results:
                                results[file_base] = {"FORMULA": 0, "TABLE": 0, "PAGE_COUNT": 0}
                            results[file_base]["FORMULA"] += formula_count
                            results[file_base]["TABLE"] += table_count
                            results[file_base]["PAGE_COUNT"] += 1  # 쪽수 카운트 증가

                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {file_path}")

    # 결과를 리스트로 변환하여 반환
    result_list = [{"폴더명": key, "전체 쪽수": value["PAGE_COUNT"], "FORMULA": value["FORMULA"], "TABLE": value["TABLE"]}
                   for key, value in results.items()]
    return result_list


if __name__ == "__main__":
    # tkinter 기본 창 숨기기
    root = tk.Tk()
    root.withdraw()  # 기본 창을 숨김

    # input 폴더 선택
    input_folder = filedialog.askdirectory(title="Select the input folder")
    if not input_folder:
        print("No input folder selected. Exiting...")
    else:
        # 폴더 내 FORMULA와 TABLE 개수 및 쪽수 카운트
        results = count_labels_and_pages_by_file_base(input_folder)

        # 결과를 DataFrame으로 변환하여 Excel로 저장
        output_df = pd.DataFrame(results, columns=["폴더명", "전체 쪽수", "FORMULA", "TABLE"])
        output_file = "Latex완료_메타미반영.xlsx"
        output_df.to_excel(output_file, index=False)

        print(f"Results saved to {output_file}")
