import os
import json
import shutil
from pathlib import Path

def copy_files_with_outside_formulas(input_folder, output_folder):
    # output 폴더 생성
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # 하위 폴더 검사
    for folder_name in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder_name)

        if os.path.isdir(folder_path):
            print(f"Checking folder: {folder_name}")

            # 각 하위 폴더 내부의 JSON 파일 검사
            for filename in os.listdir(folder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(folder_path, filename)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                            # 텍스트 박스 영역 (TEXT, FOOTNOTE, REFERENCE 레이블 포함) 추출
                            text_bboxes = [
                                shape.get('points', []) for shape in data.get('shapes', [])
                                if shape.get('label') in ['TEXT', 'FOOTNOTE', 'REFERENCE']
                            ]

                            # 외부 수식 카운트 초기화
                            outside_formula_count = 0

                            # FORMULA 레이블을 확인하여 외부 수식 개수 계산
                            for shape in data.get('shapes', []):
                                if shape.get('label') == 'FORMULA':
                                    points = shape.get('points', [])
                                    if len(points) == 2:
                                        cx = (points[0][0] + points[1][0]) / 2
                                        cy = (points[0][1] + points[1][1]) / 2

                                        # 텍스트 박스 외부에 위치한 수식인지 확인
                                        outside_text = not any(
                                            tx1 <= cx <= tx2 and ty1 <= cy <= ty2
                                            for (tx1, ty1), (tx2, ty2) in text_bboxes
                                        )

                                        if outside_text:
                                            outside_formula_count += 1

                            # 외부 수식이 2개 이상인 경우, 파일을 output 폴더로 복사
                            if outside_formula_count >= 6:
                                destination_path = os.path.join(output_folder, f"{filename}")
                                shutil.copy(file_path, destination_path)
                                print(f"Copied: {file_path} to {destination_path}")

                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {file_path}")

# 실행 예시
input_folder = r"C:\Users\USER\Desktop\LaTeXGPT테스트"  # 입력 폴더 경로
output_folder = "./output"  # 출력 폴더 경로

copy_files_with_outside_formulas(input_folder, output_folder)
