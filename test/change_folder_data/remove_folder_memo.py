import os
import shutil
from tkinter import Tk, filedialog

# 폴더 선택 대화 상자를 띄워서 선택된 폴더 경로 반환
def select_folder():
    root = Tk()
    root.withdraw()  # GUI 창을 숨김
    folder_path = filedialog.askdirectory(title="상위 폴더 선택")  # 폴더 선택 대화 상자 열기
    return folder_path

# 파일 선택 대화 상자를 띄워서 선택된 메모장 파일 경로 반환
def select_file():
    root = Tk()
    root.withdraw()  # GUI 창을 숨김
    file_path = filedialog.askopenfilename(title="메모장 파일 선택", filetypes=[("Text files", "*.txt")])  # 파일 선택 대화 상자 열기
    return file_path

# 상위 폴더 선택
parent_folder = select_folder()

# 메모장 파일 선택
memo_file = select_file()

if parent_folder and memo_file:
    # 메모장 파일에서 폴더명 읽기
    with open(memo_file, 'r') as file:
        folder_names_to_keep = [line.strip() for line in file if line.strip()]  # 공백 줄 제거

    # 상위 폴더 내에 있는 모든 폴더 가져오기
    all_folders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]

    # 삭제해야 하는 폴더들 확인 (메모장에 없는 폴더들)
    folders_to_delete = set(all_folders) - set(folder_names_to_keep)

    # 메모장에 있는 폴더들을 삭제할 경우
    # folders_to_delete = set(all_folders) & set(folder_names_to_keep)


    # 하위 폴더 삭제
    for folder_name in folders_to_delete:
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)  # 폴더 삭제
            print(f"Deleted folder: {folder_path}")
        else:
            print(f"Folder not found: {folder_path}")
else:
    print("상위 폴더 또는 메모장 파일이 선택되지 않았습니다.")
