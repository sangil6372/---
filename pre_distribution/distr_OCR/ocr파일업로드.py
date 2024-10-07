import os
import boto3
from botocore.exceptions import NoCredentialsError

from env import settings

# AWS S3 설정
s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_CONFIG['aws_access_key_id'],
                      aws_secret_access_key=settings.AWS_CONFIG['aws_secret_access_key'],
                      region_name=settings.AWS_CONFIG['region'])
bucket_name = 'project-24-pd-020'
base_s3_path = 'project1529/storage/'
# 베이스 폴더 경로 주의


def upload_folder_and_move_png(local_folder_path):
    # 폴더 이름 추출 (예: '0000_0000000')
    folder_name = local_folder_path.replace('\\', '/').split('/')[-1]

    # S3의 업로드 대상 경로 설정
    s3_folder_path = os.path.join(base_s3_path, folder_name)

    # 해당 폴더를 S3에 업로드
    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            local_file_path = os.path.join(root, file).replace('\\', '/')
            s3_file_path = os.path.join(s3_folder_path, file).replace('\\', '/')
            try:
                # 파일 업로드
                s3.upload_file(local_file_path, bucket_name, s3_file_path)
                print(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_file_path}")
            except FileNotFoundError:
                print(f"File not found: {local_file_path}")
            except NoCredentialsError:
                print("AWS credentials not available")

    # _bbox 폴더의 PNG 파일을 '0000_0000000'로 옮기기
    bbox_folder_name = f"{folder_name}_bbox"
    bbox_s3_folder_path = os.path.join(base_s3_path, bbox_folder_name)

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=bbox_s3_folder_path)

    if 'Contents' in response:
        for obj in response['Contents']:
            file_key = obj['Key']
            if file_key.endswith('.png'):
                # _bbox 폴더에 있는 PNG 파일을 기존 폴더로 복사
                new_file_key = file_key.replace(f"{bbox_s3_folder_path}/", f"{s3_folder_path}/")
                try:
                    s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_key},
                                   Key=new_file_key)
                    print(f"Moved PNG file: {file_key} to {new_file_key}")

                    # 원래의 _bbox 폴더의 PNG 파일 삭제
                    s3.delete_object(Bucket=bucket_name, Key=file_key)
                    # print(f"Deleted original PNG file: {file_key}")
                except Exception as e:
                    print(f"Error moving PNG file: {e}")
    else:
        print(f"No _bbox folder found for {folder_name}")


base_path = r"C:\Users\USER\Desktop\웅진 북센\booxen-refine-python\pre_distribution\distr_OCR\OCR 추론"
folder_list = os.listdir(base_path)

for folder in folder_list:
    local_folder_path = os.path.join(base_path, folder)
    upload_folder_and_move_png(local_folder_path)
