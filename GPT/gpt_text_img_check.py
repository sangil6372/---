import os
import tkinter as tk
from tkinter import filedialog
import json
import base64
from openai import OpenAI
from PIL import Image
import re
import time

from env import settings


MODEL: str = 'gpt-4o'
client: OpenAI = OpenAI(api_key=settings.GPT_CONFIG['GPT_API_KEY'])


# 파일 탐색기를 사용하여 디렉토리를 선택하는 함수
def select_directory(dialog_title):
    root = tk.Tk()
    root.withdraw()  # Tkinter 윈도우를 숨김
    directory_path = filedialog.askdirectory(title=dialog_title)
    return directory_path

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

# 이미지 파일을 base64로 인코딩하는 함수
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


# 이미지를 잘라내는 함수
def crop_image(image_path, coordinates, cropped_folder_path, block_index, page_number):
    try:
        img = Image.open(image_path)
        img_width, img_height = img.size

        # 좌표를 픽셀 단위로 변환
        x1 = int(coordinates["x1"] * img_width)
        y1 = int(coordinates["y1"] * img_height)
        x2 = int(coordinates["x2"] * img_width)
        y2 = int(coordinates["y2"] * img_height)

        # 좌표가 이미지 경계를 벗어나면 None 리턴
        if x1 < 0 or y1 < 0 or x2 > img_width or y2 > img_height:
            print(f"Block {block_index} on page {page_number} is out of bounds. Skipping this block.")
            return None

        # 크롭할 영역이 유효한지 확인 (너비 또는 높이가 0인 경우 처리)
        if x2 <= x1 or y2 <= y1:
            print(f"Invalid crop area for block {block_index} on page {page_number}. Skipping this block.")
            return None

        # 이미지를 잘라냄
        cropped_img = img.crop((x1, y1, x2, y2))

        # 너비와 높이에 따라 크기 조정
        if cropped_img.width < 800:
            max_width = 512
        else:
            max_width = 1024

        if cropped_img.height < 800:
            max_height = 512
        else:
            max_height = 1024

        # 비율을 유지하며 크기 조정
        cropped_img.thumbnail((max_width, max_height))

        # 페이지별 폴더 생성
        page_folder_path = os.path.join(cropped_folder_path, f"page_{page_number}")
        os.makedirs(page_folder_path, exist_ok=True)

        # 크롭된 이미지를 페이지별 폴더에 저장
        cropped_img_file_name = f"cropped_{page_number}_{block_index}.png"
        cropped_img_path = os.path.join(page_folder_path, cropped_img_file_name)
        cropped_img.save(cropped_img_path)

        return cropped_img_path

    except Exception as e:
        print(f"Error cropping image for block {block_index} on page {page_number}: {e}")
        return None


# 이미지 파일의 해상도를 JSON 데이터에서 0일 경우 대체하는 함수
def get_image_resolution_if_needed(image_path, extracted_data):
    try:
        if extracted_data["imageWidth"] == 0 or extracted_data["imageHeight"] == 0:
            img = Image.open(image_path)
            img_width, img_height = img.size

            # JSON 데이터에 이미지 해상도가 없을 경우 대체
            if extracted_data["imageWidth"] == 0:
                extracted_data["imageWidth"] = img_width
            if extracted_data["imageHeight"] == 0:
                extracted_data["imageHeight"] = img_height

    except Exception as e:
        print(f"Error getting image resolution for {image_path}: {e}")

# GPT API를 사용한 오타 검증 함수
def check_image_and_text_with_gpt(cropped_image_path, text):
    try:
        image_base64 = encode_image(cropped_image_path)

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 이미지에서 추출한 한국어 텍스트가 객관적으로 추출되었는지 검수하는 도우미입니다."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "1. 첨부된 이미지는 연구 논문이나 기술 문서의 이미지입니다. "
                                    "2. 이미지에서 텍스트를 읽고서 OCR로 추출된 텍스트가 제대로 추출되었는지 교차로 검수해주세요. "
                                    "3. 텍스트 추출에 오류가 있는 경우, 이미지 내용과 다르게 맞춤법이 틀렸을 경우 수정해 주세요. "
                                    "4. 다만 이미지에 없는 내용을 생성하지 말고 객관적으로 텍스트 추출을 검수해주세요. "
                                    "5. 수식은 별도의 LaTeX 처리 없이 순수 문자열을 그대로 출력해줘. 만약 그대로 출력 불가능할 경우 백슬래쉬를 이용하지 말고 그냥 출력 해당 문자를 생략해줘"
                                    "6. 만약 이미지에서 텍스트 인식이 불가능할 경우 원래 텍스트를 그대로 건네주세요."
                                    "7. 답변은 부가 정보 없이 수정된 텍스트 그대로 건네주세요"
                                    "다음은 추출된 텍스트입니다: \n\n{text}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=3000
        )

        corrected_text = response.choices[0].message.content.strip()

        # 사용된 토큰 수 추출 및 반환
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_used_tokens = response.usage.total_tokens

        return corrected_text, prompt_tokens, completion_tokens, total_used_tokens

    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return None, 0, 0, 0


# 페이지 번호를 파일 이름에서 추출하는 함수
def extract_page_number(file_name):
    match = re.search(r'_(\d+)\.', file_name)
    return int(match.group(1)) if match else None


# 디렉토리 선택
image_folder_path = select_directory("이미지 폴더를 선택하세요")
json_folder_path = select_directory("OCR 텍스트가 저장된 JSON 파일들이 있는 폴더를 선택하세요")

# /cropped 폴더 생성
cropped_folder_path = os.path.join(image_folder_path, 'cropped')
os.makedirs(cropped_folder_path, exist_ok=True)

# /updated 폴더 생성
updated_folder_path = os.path.join(json_folder_path, 'updated')
os.makedirs(updated_folder_path, exist_ok=True)

# 전체 폴더에서 사용된 토큰을 저장할 변수들
total_prompt_tokens_all_files = 0
total_completion_tokens_all_files = 0
total_tokens_all_files = 0

start_time = time.time()  # 시작 시간 기록
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

        # 이미지 파일 경로 생성
        image_file_name = f"{os.path.splitext(json_filename)[0]}.png"  # JSON 파일과 같은 이름의 이미지 파일
        image_path = os.path.join(image_folder_path, image_file_name)

        # 이미지 폴더 순회 및 오타 검증
        try:
            block_index = 0  # 블록 인덱스 초기화
            page_prompt_tokens = 0
            page_completion_tokens = 0
            page_total_tokens = 0

            # JSON 파일의 해상도 값이 0일 경우 이미지 파일에서 대체하는 함수 호출
            get_image_resolution_if_needed(image_path, extracted_data)

            #그 전에 일단 정렬
            extracted_data["shapes"] = custom_sort(extracted_data["shapes"])
            # shapes 리스트에서 label이 "TEXT", "FOOTNOTE", "REFERENCE" 인 블록만 처리
            for shape in extracted_data["shapes"]:
                if shape["label"] == "TEXT" or shape["label"] == "FOOTNOTE" or shape["label"] == "REFERENCE":
                    text = shape["latex"]  # latex 필드에 텍스트가 있음
                    coordinates = {
                        "x1": shape["points"][0][0] / extracted_data["imageWidth"],
                        "y1": shape["points"][0][1] / extracted_data["imageHeight"],
                        "x2": shape["points"][1][0] / extracted_data["imageWidth"],
                        "y2": shape["points"][1][1] / extracted_data["imageHeight"]
                    }  # points에서 좌표 추출 및 정규화

                    # 텍스트 블록별로 이미지 크롭
                    cropped_image_path = crop_image(image_path, coordinates, cropped_folder_path, block_index,
                                                    page_number)

                    # 유효한 크롭 이미지가 없으면 해당 블록 건너뛰기
                    if not cropped_image_path:
                        block_index += 1
                        continue

                    # GPT API로 크롭된 이미지와 텍스트 검증
                    corrected_text, prompt_tokens, completion_tokens, total_used_tokens = check_image_and_text_with_gpt(
                        cropped_image_path, text)

                    # 페이지별 토큰 수 합산
                    page_prompt_tokens += prompt_tokens
                    page_completion_tokens += completion_tokens
                    page_total_tokens += total_used_tokens

                    # 결과를 업데이트
                    if corrected_text:
                        shape["latex"] = corrected_text

                    block_index += 1  # 블록 인덱스 증가

            # 페이지별 토큰 사용량 출력
            # print(f"페이지 {page_number} - 요청에서 사용된 토큰 수: {page_prompt_tokens}")
            # print(f"페이지 {page_number} - 응답에서 사용된 토큰 수: {page_completion_tokens}")
            # print(f"페이지 {page_number} - 총 사용된 토큰 수: {page_total_tokens}")

            # 각 페이지에서 사용된 토큰을 전체 합산
            total_prompt_tokens_all_files += page_prompt_tokens
            total_completion_tokens_all_files += page_completion_tokens
            total_tokens_all_files += page_total_tokens

        except Exception as e:
            print(f"An error occurred in file {json_filename}: {e}", flush=True)

        # 수정된 데이터를 새 JSON 파일로 저장 (updated 폴더에 저장)
        output_json_file_path = os.path.join(updated_folder_path, f"{json_filename}")
        with open(output_json_file_path, 'w', encoding='utf-8') as output_json_file:
            json.dump(extracted_data, output_json_file, ensure_ascii=False, indent=4)
        print(f"오타 검증이 완료되었으며, 결과가 {output_json_file_path} 파일에 저장되었습니다.", flush=True)
end_time = time.time()  # 종료 시간 기록
elapsed_time = end_time - start_time  # 소요 시간 계산

print(f"총 소요 시간 : {elapsed_time} seconds")

# 전체 폴더에서 사용된 총 토큰 출력
print(f"요청 토큰 수: {total_prompt_tokens_all_files}")
print(f"응답 토큰 수: {total_completion_tokens_all_files}")
print(f"총 토큰 수: {total_tokens_all_files}")

