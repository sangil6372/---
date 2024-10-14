import os
import subprocess
from tkinter import Tk, filedialog


# 폴더 선택 대화 상자를 띄워서 선택된 폴더를 반환
def select_folder():
    root = Tk()
    root.withdraw()  # GUI 창을 숨김
    folder_path = filedialog.askdirectory()  # 폴더 선택 대화 상자 열기
    return folder_path


# 폴더 선택
selected_folder = select_folder()

if selected_folder:
    # 선택된 폴더의 하위 폴더를 모두 확인
    for folder_name in os.listdir(selected_folder):
        full_folder_path = os.path.join(selected_folder, folder_name)
        if os.path.isdir(full_folder_path):  # 폴더인 경우만 처리
            s3_path = f"s3://project-24-pd-020/project1529/storage/{folder_name}_bbox/"

            # aws s3 sync 명령어 구성
            command = [
                'aws', 's3', 'sync', s3_path, full_folder_path,
                '--exclude', '*.json'
            ]

            # 명령어 실행
            try:
                subprocess.run(command, check=True)
                print(f"Synced {s3_path} to {full_folder_path} (excluding .json files)")
            except subprocess.CalledProcessError as e:
                print(f"Error syncing {s3_path}: {e}")
else:
    print("폴더가 선택되지 않았습니다.")
