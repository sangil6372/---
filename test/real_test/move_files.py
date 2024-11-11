import os
import shutil
import tkinter as tk
from tkinter import filedialog


# 폴더 선택을 위한 함수
def select_directory(dialog_title):
    root = tk.Tk()
    root.withdraw()  # Tkinter 윈도우 숨기기
    directory_path = filedialog.askdirectory(title=dialog_title)
    return directory_path


# 첫 번째 폴더의 하위 폴더와 두 번째 폴더의 하위 폴더를 비교하여 파일 이동
def move_matching_subfolder_files(source_folder, target_folder):
    # 첫 번째 폴더의 하위 폴더 이름 목록
    source_subfolders = {name: os.path.join(source_folder, name) for name in os.listdir(source_folder) if
                         os.path.isdir(os.path.join(source_folder, name))}

    # 두 번째 폴더를 순회하며 하위 폴더 이름이 첫 번째 폴더와 동일한 경우 파일 이동
    for subfolder_name in os.listdir(target_folder):
        target_subfolder_path = os.path.join(target_folder, subfolder_name)

        # 첫 번째 폴더에 동일한 이름의 하위 폴더가 있는지 확인
        if subfolder_name in source_subfolders:
            source_subfolder_path = source_subfolders[subfolder_name]

            # 파일을 이동
            for file_name in os.listdir(target_subfolder_path):
                target_file_path = os.path.join(target_subfolder_path, file_name)
                source_file_path = os.path.join(source_subfolder_path, file_name)

                # 파일 이동
                shutil.move(target_file_path, source_file_path)
                print(f"파일 이동: {target_file_path} -> {source_file_path}")
        else:
            print(f"첫 번째 폴더에 일치하는 하위 폴더가 없습니다: {subfolder_name}")


# 폴더 선택
source_folder = select_directory("첫 번째 폴더 (대상)를 선택하세요")
target_folder = select_directory("두 번째 폴더 (원본)를 선택하세요")

# 파일 이동 실행
move_matching_subfolder_files(source_folder, target_folder)
