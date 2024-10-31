import os
from tkinter import filedialog, Tk


# 폴더 선택을 위한 함수
def select_folder():
    root = Tk()
    root.withdraw()  # Tkinter 창 숨기기
    folder_path = filedialog.askdirectory()  # 폴더 선택 창 열기
    return folder_path


# 하위 폴더 이름들을 메모장에 저장하는 함수
def save_subfolder_names_to_txt(folder_path):
    # 선택한 폴더의 하위 폴더들만 가져오기
    subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]

    # 메모장에 하위 폴더 이름 저장
    txt_file_path = os.path.join(folder_path, "subfolders_list.txt")
    with open(txt_file_path, "w", encoding="utf-8") as file:
        for subfolder in subfolders:
            file.write(subfolder + "\n")

    print(f"하위 폴더 목록이 {txt_file_path}에 저장되었습니다.")


if __name__ == "__main__":
    folder_path = select_folder()
    if folder_path:
        save_subfolder_names_to_txt(folder_path)
    else:
        print("폴더가 선택되지 않았습니다.")
