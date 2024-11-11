import os
import boto3

# AWS S3 세션 초기화
s3 = boto3.client('s3')

# S3 버킷 이름과 경로 설정
bucket_name = 'project-24-pd-020'
base_s3_path = 'project1529/storage'
local_path = r'C:\Users\USER\Desktop\LaTeXGPT테스트\수정'

# 로컬 경로에서 JSON 파일을 읽어와 폴더 이름 생성
for local_file in os.listdir(local_path):
    if local_file.endswith('.json'):
        # JSON 파일 이름에서 쪽수를 제거하여 폴더 이름 생성
        base_name_with_page = os.path.splitext(local_file)[0]
        base_name = '_'.join(base_name_with_page.split('_')[:-1])
        folder_name = f"{base_name}_bbox"

        # S3에서 다운로드할 PNG 파일 경로 생성
        s3_file_path = f"{base_s3_path}/{folder_name}/{base_name_with_page}.png"
        local_file_path = os.path.join(local_path, f"{base_name_with_page}.png")

        # S3에서 해당 PNG 파일 다운로드
        download_command = f'aws s3 cp s3://{bucket_name}/{s3_file_path} {local_file_path}'
        os.system(download_command)

        print(f"Downloaded PNG: {base_name_with_page}.png from s3://{bucket_name}/{s3_file_path}")
