import boto3
from tkinter import Tk, filedialog
import os

from env import settings

# S3 클라이언트 설정
s3 = boto3.client('s3',
                  aws_access_key_id=settings.AWS_CONFIG['aws_access_key_id'],
                  aws_secret_access_key=settings.AWS_CONFIG['aws_secret_access_key'],
                  region_name=settings.AWS_CONFIG['region'])

# 폴더 및 메모장 파일 선택 창 열기
root = Tk()
root.withdraw()  # Tkinter 기본 창 숨기기

# 메모장 파일 선택
selected_file = filedialog.askopenfilename(title="메모장 파일을 선택하세요", filetypes=[("Text Files", "*.txt")])
# 메모장 파일에서 다운로드할  파일 목록 읽기
if selected_file:
    try:
        with open(selected_file, "r", encoding="utf-8") as file:
            files_to_skip = {line.strip() for line in file.readlines()}
    except UnicodeDecodeError:
        # utf-16 인코딩을 시도
        with open(selected_file, "r", encoding="utf-16") as file:
            files_to_skip = {line.strip() for line in file.readlines()}
else:
    print("메모장 파일이 선택되지 않았습니다.")
    files_to_skip = set()


def download_json_from_s3(bucket_name, prefix, download_path, download_type):
    # prefix 아래에 있는 모든 파일 리스트 가져오기
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    if download_type in ["ocr", "bbox"]:
        download_type = "_" + download_type
    elif download_type == "latex":
        download_type = "_out"

    folders = set()
    bbox_folders = set()

    # 파일 목록을 탐색하며 'ㅇㅇㅇㅇ' 폴더와 'ㅇㅇㅇㅇ_bbox' 폴더 구분
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                folder_name = key.split('/')[2]  # 'ㅇㅇㅇㅇ' 폴더 이름
                if folder_name.endswith(download_type):
                    bbox_folders.add(folder_name.replace(download_type, ''))
                else:
                    folders.add(folder_name)

    # 'ㅇㅇㅇㅇ_bbox'만 존재하는 폴더 찾기
    unique_bbox_folders = bbox_folders - folders
    exist_bbox_folders = set([folder.replace(download_type, '') for folder in os.listdir(download_path)])
    unique_bbox_folders = unique_bbox_folders - exist_bbox_folders
    print(unique_bbox_folders)

    # JSON 파일만 다운로드 (폴더 구조 유지)
    for bbox_folder in unique_bbox_folders:

        # bbox_folder에 files_to_skip 중 하나라도 포함되어 있으면 다운로드
        skip_download = any(skip in bbox_folder for skip in files_to_skip)
        if skip_download:
            print(f"폴더 {bbox_folder}은 메모장 파일에 기록된 이름을 포함하고 있어 다운로드 합니다.")
            bbox_prefix = f"{prefix}{bbox_folder + download_type}/"
            bbox_pages = paginator.paginate(Bucket=bucket_name, Prefix=bbox_prefix)

            for bbox_page in bbox_pages:

                if 'Contents' in bbox_page:
                    for bbox_obj in bbox_page['Contents']:
                        if bbox_obj['Key'].endswith('.json') or bbox_obj['Key'].endswith('.png') :
                            json_file_key = bbox_obj['Key']
                            relative_path = os.path.relpath(json_file_key, prefix)
                            local_filepath = os.path.join(download_path, relative_path)

                            # 로컬 경로에 폴더가 없다면 생성
                            os.makedirs(os.path.dirname(local_filepath), exist_ok=True)

                            # 파일 다운로드
                            s3.download_file(bucket_name, json_file_key, local_filepath)
                            print(f"Downloaded {json_file_key} to {local_filepath}")



# 사용 예시 # 종이책도 다운 할 것 -> 있는 것 요청 (기존에 이미 받은 것 제외)
download_type = 'ocr'
if download_type == 'bbox':
    download_path = r'종이책_BBOX라벨링'  # 로컬에 다운로드할 경로 지정
    bucket_name = 'project-24-pd-020'
    prefix = 'project1529/storage/'
elif download_type == 'ocr':
    download_path = r'전자책_OCR라벨링'  # 로컬에 다운로드할 경로 지정
    bucket_name = 'project-24-pd-020'
    prefix = 'project1527/storage/'
elif download_type == 'latex':
    download_path = r'C:\Users\PC\Desktop\2024\24-ds-111_웅진북센\3. 데이터\9. LaTeX 라벨링'
    bucket_name = 'project-24-pd-020'
    prefix = 'project1532/storage/'
else:
    print("download_type이 잘못 입력되었습니다.")
download_json_from_s3(bucket_name, prefix, download_path, download_type)
