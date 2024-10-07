import json
import os
from tkinter import Tk
from tkinter import filedialog
import shutil
import re
import pandas as pd


def is_overlapping(formula_box, text_box):
    """
    두 사각형이 실제로 겹치는지 확인하는 함수.
    formula_box는 수식의 좌표, text_box는 텍스트의 좌표.
    각 사각형은 [top_left_x, top_left_y], [bottom_right_x, bottom_right_y] 형태의 좌표 리스트.
    """

    # 수식의 좌상단 좌표
    fx0, fy0 = formula_box[0]
    # 수식의 우하단 좌표
    fx1, fy1 = formula_box[1]

    mid_fx = (fx0 + fx1) / 2
    mid_fy = (fy0 + fy1) / 2

    # 텍스트의 좌상단 좌표
    tx0, ty0 = text_box[0]
    # 텍스트의 우하단 좌표
    tx1, ty1 = text_box[1]

    # 텍스트 영역 안에 수식 박스의 중심점이 속하는지 점검 (겹치는지)
    if ( tx0 <= mid_fx <=tx1 and ty0 <= mid_fy <=ty1):
        return True  # 겹침 발생
    return False  # 겹치지 않음


def is_text_garbled(text):
    total_chars = len(text)
    if total_chars == 0:
        return False

    invalid_chars = len(re.findall(r'[^\uAC00-\uD7AF\u0020-\u007E\u4E00-\u9FFF\s.,!?()\-\"\'%&@#]', text))
    invalid_ratio = invalid_chars / total_chars

    return invalid_ratio >= 0.4

cnt_dict = {} # 예외처리용
def merge_json_files(original_folder, ocr_folder, output_folder):
    foldername = original_folder.split('/')[-1]
    update_dict = {foldername: {"notext": 0, "worngtext": 0, "diffcnt": 0}}
    # 각 폴더에서 json 파일 목록을 가져오기
    original_files = {f for f in os.listdir(original_folder) if f.endswith('.json')}
    ocr_files = {f for f in os.listdir(ocr_folder) if f.endswith('.json')}

    cnt = 0

    # 두 폴더에서 이름이 같은 파일에 대해서만 작업 진행
    common_files = original_files.intersection(ocr_files)
    for file_name in original_files:
        if file_name in common_files:
            original_file_path = os.path.join(original_folder, file_name)
            ocr_file_path = os.path.join(ocr_folder, file_name)

            # 기존 파일과 OCR 파일을 로드
            with open(original_file_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            for orig_shape in original_data['shapes']:
                orig_shape['points'] = [[min(orig_shape['points'][0][0], orig_shape['points'][1][0]),
                                         min(orig_shape['points'][0][1], orig_shape['points'][1][1])],
                                        [max(orig_shape['points'][0][0], orig_shape['points'][1][0]),
                                         max(orig_shape['points'][0][1], orig_shape['points'][1][1])]]

            with open(ocr_file_path, 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)

            # 기존 파일에서 텍스트 박스들의 좌표 가져오기 (TEXT label)
            formula_boxes = [shape['points'] for shape in original_data['shapes'] if shape['label'] == 'FORMULA']

            # OCR 파일에서 FORMULA에 해당하는 값만 처리
            for orig_shape, ocr_shape in zip(original_data["shapes"], ocr_data["shapes"]):
                ocr_shape['points'] = [[min(ocr_shape['points'][0][0], ocr_shape['points'][1][0]),
                                        min(ocr_shape['points'][0][1], ocr_shape['points'][1][1])],
                                       [max(ocr_shape['points'][0][0], ocr_shape['points'][1][0]),
                                        max(ocr_shape['points'][0][1], ocr_shape['points'][1][1])]]
                if orig_shape['label'] == 'FORMULA' and ocr_shape['label'] == 'FORMULA':
                    if orig_shape['points'] == ocr_shape['points']:
                        orig_shape['latex'] = ocr_shape['latex']
                    else:
                        print(file_name, "좌표가 다릅니다.")
                elif orig_shape['label'] == 'TEXT' and ocr_shape['label'] == 'TEXT':
                    formula_cnt = 0
                    for formula_box in formula_boxes:
                        if is_overlapping(formula_box, orig_shape['points']):
                            formula_cnt += 1
                    if orig_shape['points'] == ocr_shape['points']:
                        if is_text_garbled(orig_shape['latex']):
                            orig_shape['latex'] = ocr_shape['latex']
                        # 텍스트 길이 차이가 ocr_text 보다 10% 클 경우 대체
                        elif len(ocr_shape['latex'])*0.9 <= len(orig_shape['latex']) <= len(ocr_shape['latex'])*1.1 :
                            orig_shape['latex'] = ocr_shape['latex']


                        """if orig_shape['latex'].count('{f}') != formula_cnt:
                            if ocr_shape['latex'].count('{f}') == formula_cnt:
                                orig_shape['latex'] = ocr_shape['latex']
                                print(formula_cnt)
                                print(f"{file_name}의 latex 스크립트가 ocr 스크립트로 대체되었습니다. (f숫자 불일치)")
                            else:
                                continue"""
                        if orig_shape['latex'] == "":
                            orig_shape['latex'] = ocr_shape['latex']
                            print(f"{file_name}의 latex 스크립트가 ocr 스크립트로 대체되었습니다. (빈 텍스트)")

                elif orig_shape['label'] == 'TABLE' and ocr_shape['label'] == 'TABLE':
                    continue

                elif orig_shape['label'] == 'FOOTNOTE' and ocr_shape['label'] == 'FOOTNOTE':
                    if orig_shape['points'] == ocr_shape['points']:
                        if is_text_garbled(orig_shape['latex']):
                            orig_shape['latex'] = ocr_shape['latex']
                        """if orig_shape['latex'].count('{f}') != formula_cnt:
                            if ocr_shape['latex'].count('{f}') == formula_cnt:
                                print(formula_cnt)
                                orig_shape['latex'] = ocr_shape['latex']
                                print(f"{file_name}의 latex 스크립트가 ocr 스크립트로 대체되었습니다. (f숫자 불일치)")
                            else:
                                continue"""
                        if orig_shape['latex'] == "":
                            orig_shape['latex'] = ocr_shape['latex']

                elif orig_shape['label'] == 'REFERENCE' and ocr_shape['label'] == 'REFERENCE':
                    if orig_shape['points'] == ocr_shape['points']:
                        if orig_shape['latex'] == "":
                            orig_shape['latex'] = ocr_shape['latex']

                elif orig_shape['label'] == 'IMAGE' and ocr_shape['label'] == 'IMAGE':
                    continue

            sorted_shapes = custom_sort(sorted(original_data['shapes'], key=lambda item: item["points"][0][1]))
            original_data['shapes'] = sorted_shapes

            # 결과를 저장할 폴더가 없으면 생성
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # 변경된 내용을 새로운 JSON 파일로 저장
            output_file_path = os.path.join(output_folder, file_name)
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, ensure_ascii=False, indent=4)
        else:
            # 카운팅
            cnt+=1
            original_file_path = os.path.join(original_folder, file_name)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            output_file_path = os.path.join(output_folder, file_name)
            shutil.copy(original_file_path, output_file_path)
        print(f'Merged {len(common_files)} files.')

    # 폴더 이름을 추출하고 해당 폴더의 cnt 값을 사전에 저장
    folder_name = os.path.basename(original_folder)
    if folder_name not in cnt_dict:
        cnt_dict[folder_name] = 0
    cnt_dict[folder_name] += cnt


def select_folder(prompt):
    Tk().withdraw()  # Tkinter 윈도우 숨기기
    folder_selected = filedialog.askdirectory(title=prompt)
    return folder_selected


# 두 박스의 y 좌표가 겹치는지 확인하는 함수
def is_overlapping_y(box1, box2):
    y1_min = min(box1["points"][0][1], box1["points"][1][1])
    y1_max = max(box1["points"][0][1], box1["points"][1][1])

    y2_min = min(box2["points"][0][1], box2["points"][1][1])
    y2_max = max(box2["points"][0][1], box2["points"][1][1])

    # 겹치는 부분의 시작과 끝
    overlap_start = max(y1_min, y2_min)
    overlap_end = min(y1_max, y2_max)

    # 겹치는 길이
    overlap_length = max(0, overlap_end - overlap_start)

    # 각 박스의 높이
    height1 = y1_max - y1_min
    height2 = y2_max - y2_min

    # 겹치는 길이가 두 박스 높이의 50% 이상인지 확인
    if (overlap_length >= 0.5 * height1) or (overlap_length >= 0.5 * height2):
        return True
    return False


# 커스텀 정렬 함수 정의
def custom_sort(shapes):
    sorted_shapes = []

    while shapes:
        current = shapes.pop(0)
        overlaps = [current]
        non_overlaps = []
        # 현재 상태를 디버깅하기 위해 출력

        # 겹치는 박스를 찾기
        for other in shapes:
            if current['label'] == other['label'] and is_overlapping_y(current, other):
                overlaps.append(other)
            else:
                non_overlaps.append(other)

        # 겹치는 박스들을 x 좌표로 정렬
        overlaps_sorted = sorted(overlaps, key=lambda item: item["points"][0][0])
        sorted_shapes.extend(overlaps_sorted)

        # 남은 박스들을 다음 순서로 처리
        shapes = non_overlaps

    return sorted_shapes


original_folder_path = r"C:\Users\USER\Downloads\종이책_OCR추론요청0926_json\updated"
ocr_folder_path = r"C:\Users\USER\Desktop\웅진 북센\booxen-refine-python\pre_distribution\distr_OCR\1004_ai_ocr"
output_folder_path = r"OCR 추론"
comp_folder = r"./1004_OCR_업로드완료"

# original_folder_dict = {f.split('_')[1]: f for f in os.listdir(original_folder_path)}
original_folder_dict = {f: f for f in os.listdir(original_folder_path)}
ocr_folder_list = os.listdir(ocr_folder_path)
comp_set = {f.split('_')[1] for f in os.listdir(comp_folder)}

for ocr_f in ocr_folder_list:
    if ocr_f not in comp_set:
        original_folder = os.path.join(original_folder_path, original_folder_dict[ocr_f])
        ocr_folder = os.path.join(ocr_folder_path, ocr_f)
        output_folder = os.path.join(output_folder_path, original_folder_dict[ocr_f])

        merge_json_files(original_folder, ocr_folder, output_folder)
    else:
        print(f"{ocr_f}는 이미 처리된 폴더 입니다.")

# 폴더별 cnt 값 출력
print("폴더별 cnt 값:")
for folder, count in cnt_dict.items():
    print(f"{folder}: {count}")