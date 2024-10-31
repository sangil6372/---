import os
import tkinter as tk
from tkinter import filedialog

# tkinter 초기화
root = tk.Tk()
root.withdraw()  # Tkinter 창 숨기기

# 상위 디렉토리 선택
root_directory = filedialog.askdirectory(title="Select the root directory containing subdirectories")

# 하위 폴더 이름 변경
for folder_name in os.listdir(root_directory):
    folder_path = os.path.join(root_directory, folder_name)

    # 폴더인지 확인
    if os.path.isdir(folder_path):
        # '_bbox'로 끝나는 폴더명에서 '_bbox' 제거
        if folder_name.endswith('_bbox'):
            new_folder_name = folder_name.rsplit('_', 1)[0]  # '_bbox' 제거
            new_folder_path = os.path.join(root_directory, new_folder_name)

            # 폴더 이름 변경
            os.rename(folder_path, new_folder_path)
            print(f"Renamed: {folder_name} -> {new_folder_name}")

print("All folders have been renamed.")
