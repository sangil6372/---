import os
import shutil

def copy_matching_pdfs(pdf_folder, subfolder_container):
    # 새로운 저장 폴더 경로 설정
    output_folder = f"./{os.path.basename(subfolder_container)}_pdf"
    os.makedirs(output_folder, exist_ok=True)

    # 하위 폴더들의 이름을 가져오기
    subfolder_names = [folder for folder in os.listdir(subfolder_container) if os.path.isdir(os.path.join(subfolder_container, folder))]

    # PDF 폴더에서 파일 이름과 하위 폴더 이름을 비교하여 일치하면 복사
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            pdf_name = os.path.splitext(pdf_file)[0]  # 확장자를 제외한 파일 이름
            if pdf_name in subfolder_names:
                source_path = os.path.join(pdf_folder, pdf_file)
                destination_path = os.path.join(output_folder, pdf_file)
                shutil.copy2(source_path, destination_path)
                print(f"복사됨: {pdf_file} -> {destination_path}")

# 사용 예시
pdf_folder = r"C:\Users\USER\Desktop\웅진 북센\종이책_pdf\0925dla"  # 첫 번째 입력 폴더 (PDF 파일들이 있는 폴더 경로)
subfolder_container = r"C:\Users\USER\Desktop\웅진 북센\booxen-refine-python\pre_distribution\distr_OCR\1004_ai_ocr"  # 두 번째 입력 폴더 (하위 폴더들이 있는 폴더 경로)

copy_matching_pdfs(pdf_folder, subfolder_container)
