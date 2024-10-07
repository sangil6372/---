import os
from tkinter import Tk, filedialog

# 폴더 선택 창 열기
root = Tk()
root.withdraw()  # Tkinter 기본 창 숨기기
selected_folder = filedialog.askdirectory(title="폴더를 선택하세요")

# 파일 이름 가져오기
if selected_folder:
    file_names = os.listdir(selected_folder)

    # 파일 이름에서 '_bbox' 제거하고 메모장에 저장하기
    with open("../before_AI_request/1002_OCR_요청_목록.txt", "w", encoding="utf-8") as file:
        for name in file_names:
            modified_name = name.replace("_bbox", "")  # '_bbox' 제거
            file.write(modified_name + "\n")

    print("파일 이름이 '1002_OCR_요청목록.txt'에 저장되었습니다.")
else:
    print("폴더가 선택되지 않았습니다.")
