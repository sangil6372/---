import pdfplumber  # PyMuPDF
import json
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image  # 이미지 크기를 가져오기 위해 Pillow 사용
from tqdm import tqdm


def convert_to_point_coords(x0, y0, x1, y1, page_width, page_height, img_width, img_height):
    """픽셀 좌표를 PDF 포인트 좌표로 변환"""
    point_x0 = x0 * page_width / img_width
    point_y0 = y0 * page_height / img_height
    point_x1 = x1 * page_width / img_width
    point_y1 = y1 * page_height / img_height
    return point_x0, point_y0, point_x1, point_y1


# tkinter 초기화
root = tk.Tk()
root.withdraw()  # Tkinter 창 숨기기

# 상위 디렉토리 선택
root_directory = filedialog.askdirectory(title="Select the root directory containing subdirectories with JSON files")

# PDF 파일들이 모여있는 디렉토리 경로 선택
pdf_directory = filedialog.askdirectory(title="Select the directory containing PDF files")

# updated 폴더 경로 생성
updated_root_directory = os.path.join(root_directory, "updated")
os.makedirs(updated_root_directory, exist_ok=True)  # 상위 updated 폴더 생성

none_count = 0  # None으로 처리된 경우를 카운트하는 변수

# 상위 폴더의 모든 하위 폴더에 대해 처리
for folder_name in os.listdir(root_directory):
    folder_path = os.path.join(root_directory, folder_name)

    if os.path.isdir(folder_path):  # 하위 폴더인 경우에만 처리
        # 하위 폴더명이 '_'를 포함하는 경우, 그 뒤의 내용만 추출
        if '_' in folder_name:
            folder_suffix = folder_name.split('_', 1)[1]
        else:
            folder_suffix = folder_name

        # PDF 파일 찾기: PDF 디렉토리 내에서 파일 이름의 접미사만 비교하여 일치하는 파일 찾기
        pdf_file_name = None
        for pdf_file in os.listdir(pdf_directory):
            if pdf_file.lower().endswith('.pdf'):  # 확장자를 대소문자 무시하고 처리
                # PDF 파일명에서 '_' 뒤의 내용 추출
                if '_' in pdf_file:
                    pdf_suffix = pdf_file.split('_', 1)[1]
                else:
                    pdf_suffix = pdf_file

                # PDF 파일명에서 추출한 접미사와 폴더명 비교
                if folder_suffix == pdf_suffix.split('.')[0]:
                    pdf_file_name = pdf_file
                    break

        if not pdf_file_name:
            print(f"Warning: No matching PDF found for folder {folder_name}")
            continue

        # PDF 파일 경로 생성 및 열기
        pdf_file_path = os.path.join(pdf_directory, pdf_file_name)
        pdf_document = pdfplumber.open(pdf_file_path)

        # 해당 하위 폴더 내의 모든 JSON 파일 목록 가져오기
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

        # updated 하위 폴더 경로 생성 (JSON 파일이 있던 폴더명으로 저장)
        updated_directory = os.path.join(updated_root_directory, folder_name)
        os.makedirs(updated_directory, exist_ok=True)  # 해당 하위 폴더에 대한 updated 폴더 생성

        for json_file in tqdm(json_files, desc=f"Processing {folder_name}"):
            # 파일명에서 페이지 번호 추출 (예: page_1.json -> 1)
            match = json_file.split('_')[1].split('.')[0]
            if match:
                page_number = int(match) - 1  # 페이지 번호는 0부터 시작하므로 -1

                # PDF 페이지 가져오기
                if page_number < len(pdf_document.pages):
                    page = pdf_document.pages[page_number]

                    # JSON 파일 열기 (인코딩 지정)
                    json_file_path = os.path.join(folder_path, json_file)
                    with open(json_file_path, 'r', encoding='utf-8') as file:
                        json_data = json.load(file)

                    # width_ratio 및 height_ratio 계산 전에 값이 0인지 확인
                    image_width = json_data.get('imageWidth', 0)
                    image_height = json_data.get('imageHeight', 0)

                    # imageWidth 또는 imageHeight가 0일 경우, 동일한 이름의 이미지 파일에서 크기 정보를 가져옴
                    image_file_name = os.path.splitext(json_file)[0] + ".png"  # 이미지 파일이 PNG라고 가정
                    image_file_path = os.path.join(folder_path, image_file_name)

                    if (image_width == 0 or image_height == 0):
                        if os.path.exists(image_file_path):
                            with Image.open(image_file_path) as img:
                                image_width, image_height = img.size  # 이미지의 크기 정보 가져오기
                            print(f"Info: Using image dimensions from {image_file_name} for page {page_number + 1}")
                        else:
                            print(f"Warning: No image found for page {page_number + 1} ({json_file})")
                            continue  # 이미지 파일이 없으면 해당 페이지는 건너뜀

                    # 이미지 크기 비율 계산
                    width_ratio = page.width / image_width
                    height_ratio = page.height / image_height

                    # JSON 객체의 shapes 처리
                    shapes = json_data["shapes"]

                    x_min, y_min, x_max, y_max = page.bbox

                    for shape in shapes:
                        if shape['label'] == 'IMAGE':
                            shape['latex'] = ""  # IMAGE 라벨의 latex 초기화
                        elif (shape['label'] == 'FORMULA') or (shape['label'] == 'TABLE'):
                            continue
                        else:
                            # BBox 좌표를 PDF 포인트 좌표로 변환하여 해당 영역의 텍스트 추출

                            x0, y0 = min(shape['points'][0][0], shape['points'][1][0]), min(shape['points'][0][1],
                                                                                            shape['points'][1][1])
                            x1, y1 = max(shape['points'][0][0], shape['points'][1][0]), max(shape['points'][0][1],
                                                                                            shape['points'][1][1])

                            # 우측 띄어쓰기 추출 필요 -> 영역 확대

                            if x_min < (x0 - 30) * width_ratio < x_max:
                                x0_points = (x0 - 30) * width_ratio
                            else:
                                x0_points = x_min
                            y0_points = y0 * height_ratio
                            if x_min < (x1 + 30) * width_ratio < x_max:
                                x1_points = (x1 + 30) * width_ratio
                            else:
                                x1_points = x_max
                            if y_min < (y1 + 5) * height_ratio < y_max:
                                y1_points = (y1 + 5) * height_ratio
                            else:
                                y1_points = y_max

                            # PDF에서 해당 영역의 텍스트를 추출하여 latex 필드에 저장
                            cropped_page = page.within_bbox((x0_points, y0_points, x1_points, y1_points))
                            text_latex = cropped_page.extract_text().strip()
                            shape['latex'] = text_latex.replace("\n", "")  # 추출한 텍스트를 latex 필드에 저장

                            #                            words_list = []

                            # TEXT 영역 안에 포함된 FORMULA 객체를 찾기
                            for inner_shape in shapes:
                                if inner_shape["label"] == "FORMULA":

                                    fx0, fy0 = min(inner_shape['points'][0][0], inner_shape['points'][1][0]), min(
                                        inner_shape['points'][0][1], inner_shape['points'][1][1])
                                    fx1, fy1 = max(inner_shape['points'][0][0], inner_shape['points'][1][0]), max(
                                        inner_shape['points'][0][1], inner_shape['points'][1][1])

                                    fx0_points = fx0 * width_ratio
                                    fy0_points = fy0 * height_ratio
                                    fx1_points = fx1 * width_ratio
                                    fy1_points = fy1 * height_ratio

                                    # 수식의 좌상단점이 텍스트 박스 안에 포함되는지 확인
                                    formula_top_left_in_textbox = (
                                            fx0_points >= x0_points and fx0_points <= x1_points and
                                            fy0_points >= y0_points and fy0_points <= y1_points)
                                    # 수식의 우하단점이 텍스트 박스 안에 포함되는지 확인
                                    formula_bottom_right_in_textbox = (
                                            fx1_points >= x0_points and fx1_points <= x1_points and
                                            fy1_points >= y0_points and fy1_points <= y1_points)

                                    # 두 조건 중 하나라도 만족하면 수식 박스가 텍스트 박스와 겹친다고 판단
                                    if formula_top_left_in_textbox or formula_bottom_right_in_textbox:
                                        # FORMULA 중심점에 위치한 단어 추출

                                        # 수식 좌표 중간 값 계산
                                        mid_x = (fx0_points + fx1_points) / 2
                                        mid_y = (fy0_points + fy1_points) / 2

                                        # text_latex의 각 단어와 그 좌표를 가져옴
                                        words = cropped_page.extract_words()

                                        closest_word = None  # 만약 None으로 남을 시 처리 필요
                                        min_distance = float('inf')  # 최소 거리를 매우 큰 값으로 초기화

                                        for word in words:
                                            word_x0 = word['x0']
                                            word_y0 = word['top']
                                            word_x1 = word['x1']
                                            word_y1 = word['bottom']
                                            word_text = word['text']

                                            # 단어의 중심 좌표 계산
                                            word_center_x = (word_x0 + word_x1) / 2
                                            word_center_y = (word_y0 + word_y1) / 2

                                            # 수식 중간 좌표와 단어 중심 좌표 사이의 거리 계산
                                            distance = ((mid_x - word_center_x) ** 2 + (
                                                    mid_y - word_center_y) ** 2) ** 0.5

                                            # 거리가 더 짧은 단어가 있으면 갱신
                                            if distance < min_distance:
                                                min_distance = distance
                                                closest_word = word_text

                                        # 가장 가까운 단어 뒤에 {f} 태그 삽입
                                        if closest_word:
                                            # closest_word 뒤에 {f}를 삽입
                                            if closest_word in text_latex:
                                                text_latex = text_latex.replace(closest_word + " ",
                                                                                f"{closest_word}{{f}}", 1)
                                        else:
                                            # closest_word가 None일 경우 기본 처리
                                            none_count += 1  # None이 발생한 경우 카운트 증가
                                            # text_latex += " {f}"  # 기본적으로 {f}를 텍스트 끝에 삽입

                                        # 이후 shape에 latex 필드 업데이트
                                        shape['latex'] = text_latex.replace("\n", "")

                            # words_list.sort(key=len, reverse=True)
                            # for word in words_list:
                            #    shape["latex"] = text_latex.replace(word, "{f}").replace("\n", "")

            # 수정된 JSON 데이터를 updated 폴더에 저장

            # 수정된 JSON 데이터를 updated 폴더에 저장
            #            sorted_shapes = custom_sort(sorted(json_data['shapes'], key=lambda item: item["points"][0][1]))
            #           json_data['shapes'] = sorted_shapes
            updated_file_path = os.path.join(updated_directory, json_file)
            with open(updated_file_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)

        # 프로그램 종료 시 None 처리 통계 출력
        print(f"총 {none_count}개의 수식이 텍스트와 겹치는 단어를 찾지 못해 기본 처리되었습니다.")

        # PDF 문서 닫기
        pdf_document.close()
