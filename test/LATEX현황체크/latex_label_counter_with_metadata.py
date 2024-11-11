import os
import json
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import openpyxl


import os
import json
import pandas as pd

import os
import json
import tkinter as tk
from tkinter import filedialog
import pandas as pd

def count_labels_in_folder(input_folder, df):
    results = []

    for folder_name in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder_name)

        if os.path.isdir(folder_path):
            formula_inside_count = 0
            formula_outside_count = 0
            table_count = 0
            book_page_count_with_only_formula_inside = 0
            book_page_count_without_formula = 0
            total_file_count = 0
            file_with_formula_or_table_count = 0
            book_page_count_with_table = 0
            book_page_count_with_table_no_outside_formula = 0

            # 추가된 변수들
            table_page_formula_inside_count = 0
            table_page_formula_outside_count = 0
            non_table_formula_inside_count = 0  # 테이블이 없는 페이지의 내부 수식 개수
            non_table_formula_outside_count = 0  # 테이블이 없는 페이지의 외부 수식 개수

            matching_rows = [
                (row['시작번호(pdf)'], row['끝번호(pdf)']) for _, row in df.iterrows()
                if str(row['파일명']) in folder_name
            ]

            if not matching_rows:
                print(f"No matching metadata for folder: {folder_name}")
                continue

            start_page, end_page = matching_rows[0]

            for filename in os.listdir(folder_path):
                if filename.endswith(".json"):
                    total_file_count += 1
                    file_path = os.path.join(folder_path, filename)
                    parts = filename.split("_")
                    if len(parts) > 1:
                        page_number_str = parts[-1].replace(".json", "")
                        try:
                            page_number = int(page_number_str)
                        except ValueError:
                            print(f"Invalid page number in filename: {filename}")
                            continue

                        if page_number < start_page or page_number > end_page:
                            continue

                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            text_bboxes = [
                                shape.get('points', []) for shape in data.get('shapes', [])
                                if shape.get('label') in ['TEXT', 'FOOTNOTE', 'REFERENCE']
                            ]

                            page_has_formula_outside = False
                            page_has_table = False
                            page_has_formula_inside_only = False
                            page_has_formula = False
                            has_formula_or_table = False
                            formula_inside_in_table_page = 0
                            formula_outside_in_table_page = 0

                            # 먼저 TABLE 레이블이 있는지 확인하여 page_has_table 설정
                            for shape in data.get('shapes', []):
                                if shape.get('label') == 'TABLE':
                                    table_count += 1
                                    has_formula_or_table = True
                                    page_has_table = True

                            # FORMULA 레이블 확인 및 내부, 외부 수식 카운팅
                            for shape in data.get('shapes', []):
                                if shape.get('label') == 'FORMULA':
                                    page_has_formula = True
                                    has_formula_or_table = True
                                    points = shape.get('points', [])
                                    if len(points) == 2:
                                        cx = (points[0][0] + points[1][0]) / 2
                                        cy = (points[0][1] + points[1][1]) / 2

                                        inside_text = any(
                                            tx1 <= cx <= tx2 and ty1 <= cy <= ty2
                                            for (tx1, ty1), (tx2, ty2) in text_bboxes
                                        )

                                        if inside_text:
                                            formula_inside_count += 1
                                            page_has_formula_inside_only = True
                                            if page_has_table:
                                                formula_inside_in_table_page += 1
                                            else:
                                                non_table_formula_inside_count += 1
                                        else:
                                            formula_outside_count += 1
                                            page_has_formula_outside = True
                                            if page_has_table:
                                                formula_outside_in_table_page += 1
                                            else:
                                                non_table_formula_outside_count += 1

                            # 테이블과 외부 수식 조건에 따라 페이지 수 카운팅
                            if page_has_table and not page_has_formula_outside:
                                book_page_count_with_table_no_outside_formula += 1

                            if page_has_table:
                                book_page_count_with_table += 1
                                table_page_formula_inside_count += formula_inside_in_table_page
                                table_page_formula_outside_count += formula_outside_in_table_page

                            if page_has_formula_inside_only and not page_has_formula_outside:
                                book_page_count_with_only_formula_inside += 1

                            if not page_has_formula:
                                book_page_count_without_formula += 1

                            if has_formula_or_table:
                                file_with_formula_or_table_count += 1

                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {file_path}")

            print(f"Folder: {folder_name}")
            print(f" - FORMULA inside text count: {formula_inside_count}")
            print(f" - FORMULA outside text count: {formula_outside_count}")
            print(f" - TABLE count: {table_count}")
            print(f" - Pages with only formula inside: {book_page_count_with_only_formula_inside}")
            print(f" - Pages without any formula: {book_page_count_without_formula}")
            print(f" - Pages with at least one table: {book_page_count_with_table}")
            print(f" - Pages with table but no outside formula: {book_page_count_with_table_no_outside_formula}")
            print(f" - Total files: {total_file_count}")
            print(f" - Files with formula or table: {file_with_formula_or_table_count}")
            print(f" - Table pages with inside formula: {table_page_formula_inside_count}")
            print(f" - Table pages with outside formula: {table_page_formula_outside_count}")
            print(f" - Non-table pages with inside formula: {non_table_formula_inside_count}")
            print(f" - Non-table pages with outside formula: {non_table_formula_outside_count}")
            print()

            results.append({
                "폴더명": folder_name,
                "FORMULA (내부)": formula_inside_count,
                "FORMULA (외부)": formula_outside_count,
                "TABLE": table_count,
                "내부 수식 전용 페이지 수": book_page_count_with_only_formula_inside,
                "수식이 없는 페이지 수": book_page_count_without_formula,
                "표가 하나 이상 있는 페이지 수": book_page_count_with_table,
                "표만 있고 외부 수식 없는 페이지 수": book_page_count_with_table_no_outside_formula,
                "폴더 파일 수": total_file_count,
                "FORMULA/TABLE 포함 파일 수": file_with_formula_or_table_count,
                "테이블이 있는 페이지 내부 수식": table_page_formula_inside_count,
                "테이블이 있는 페이지 외부 수식": table_page_formula_outside_count,
                "테이블 없는 페이지 내부 수식": non_table_formula_inside_count,
                "테이블 없는 페이지 외부 수식": non_table_formula_outside_count
            })

    return results


if __name__ == "__main__":
    # tkinter 기본 창 숨기기
    root = tk.Tk()
    root.withdraw()

    # input 폴더 선택
    input_folder = filedialog.askdirectory(title="Select the input folder")
    if not input_folder:
        print("No input folder selected. Exiting...")
    else:
        # 메타데이터 파일 로드
        metadata_file_path = r"C:\Users\USER\Downloads\북센 도서 메타데이터.xlsx"
        if not metadata_file_path:
            print("No metadata file selected. Exiting...")
            exit()

        df = pd.read_excel(metadata_file_path)

        # 폴더 내 FORMULA와 TABLE 개수 카운트
        results = count_labels_in_folder(input_folder, df)

        # 결과를 DataFrame으로 변환하여 Excel로 저장
        output_df = pd.DataFrame(results, columns=[
            "폴더명", "FORMULA (내부)", "FORMULA (외부)", "TABLE",
            "내부 수식 전용 페이지 수", "수식이 없는 페이지 수",
            "표가 하나 이상 있는 페이지 수", "표만 있고 외부 수식 없는 페이지 수",
            "폴더 파일 수", "FORMULA/TABLE 포함 파일 수",
            "테이블이 있는 페이지 내부 수식", "테이블이 있는 페이지 외부 수식",
            "테이블 없는 페이지 내부 수식", "테이블 없는 페이지 외부 수식"
        ])

        output_file = "355_ocr_count.xlsx"
        output_df.to_excel(output_file, index=False)

        print(f"Results saved to {output_file}")


