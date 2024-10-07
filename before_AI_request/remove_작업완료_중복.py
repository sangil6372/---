import os
from tkinter import Tk, filedialog

# 폴더 및 파일 선택 창 열기
root = Tk()
root.withdraw()  # Tkinter 기본 창 숨기기

# 폴더 선택
selected_folder = filedialog.askdirectory(title="폴더를 선택하세요")

# 메모장 파일 선택
selected_file = filedialog.askopenfilename(title="메모장 파일을 선택하세요", filetypes=[("Text Files", "*.txt")])

# 파일 삭제 처리
if selected_folder and selected_file:
    try:
        with open(selected_file, "r", encoding="utf-8") as file:
            file_names_to_delete = {line.strip() for line in file.readlines()}
    except UnicodeDecodeError:
        # utf-16 인코딩을 시도
        with open(selected_file, "r", encoding="utf-16") as file:
            file_names_to_delete = {line.strip() for line in file.readlines()}

    # 폴더 내부 파일들을 순회하면서 메모장에 있는 파일 이름과 일치하는 경우 파일 삭제
    for root_dir, _, files in os.walk(selected_folder):
        for file_name in files:
            if file_name in file_names_to_delete:
                file_path = os.path.join(root_dir, file_name)
                os.remove(file_path)
                print(f"파일 삭제: {file_path}")

    print("메모장에 있는 파일 이름에 해당하는 파일 삭제가 완료되었습니다.")
else:
    print("폴더 또는 파일이 선택되지 않았습니다.")
