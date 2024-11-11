import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def select_folder():
    root = tk.Tk()
    root.withdraw()  # Tkinter 창 숨기기
    folder_selected = filedialog.askdirectory(title="폴더 선택")
    if not folder_selected:
        messagebox.showinfo("선택 오류", "폴더를 선택하지 않았습니다.")
        return None
    return folder_selected

def select_file():
    root = tk.Tk()
    root.withdraw()  # Tkinter 창 숨기기
    file_selected = filedialog.askopenfilename(title="메모장 파일 선택", filetypes=[("텍스트 파일", "*.txt")])
    if not file_selected:
        messagebox.showinfo("선택 오류", "메모장 파일을 선택하지 않았습니다.")
        return None
    return file_selected

def create_subfolders_from_txt(folder_path, txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            subfolder_name = line.strip()
            if subfolder_name:  # 공백이 아닌 경우에만 폴더 생성
                subfolder_path = os.path.join(folder_path, subfolder_name)
                os.makedirs(subfolder_path, exist_ok=True)
                print(f"Created: {subfolder_path}")
    messagebox.showinfo("완료", "하위 폴더 생성이 완료되었습니다.")

def main():
    folder_path = select_folder()
    if not folder_path:
        return
    txt_file_path = select_file()
    if not txt_file_path:
        return
    create_subfolders_from_txt(folder_path, txt_file_path)

if __name__ == "__main__":
    main()
