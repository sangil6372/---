from tkinter import Tk, filedialog

# 파일 선택 창 열기
root = Tk()
root.withdraw()  # Tkinter 기본 창 숨기기
selected_file = filedialog.askopenfilename(title="메모장 파일을 선택하세요", filetypes=[("Text Files", "*.txt")])

# 파일 처리
if selected_file:
    try:
        with open(selected_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        # utf-16 인코딩을 시도
        with open(selected_file, "r", encoding="utf-16") as file:
            lines = file.readlines()

    # 각 줄에서 '_' 기준 좌측 내용을 제거
    modified_lines = []
    for line in lines:
        line = line.strip()  # 줄 끝의 공백 문자 제거
        if "_" in line:
            modified_lines.append(line.split("_", 1)[1])
        else:
            modified_lines.append(line)

    # 수정된 내용을 새로운 파일에 저장
    with open("수정된_파일_이름_목록.txt", "w", encoding="utf-8") as file:
        for modified_line in modified_lines:
            file.write(modified_line + "\n")

    print("수정된 파일 이름이 '수정된_파일_이름_목록.txt'에 저장되었습니다.")
else:
    print("파일이 선택되지 않았습니다.")
