import os
import pdfplumber


def count_pdf_pages_in_folder(folder_path):
    # 폴더 내의 모든 파일을 순회
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):  # PDF 파일만 처리
            file_path = os.path.join(folder_path, filename)

            # PDF 파일 읽기
            with pdfplumber.open(file_path) as pdf:
                num_pages = len(pdf.pages)
                print(f"{filename} : {num_pages}")


# 예시 폴더 경로를 입력받아 페이지 수 출력
folder_path = input("PDF가 있는 폴더 경로를 입력하세요: ")
count_pdf_pages_in_folder(folder_path)
