import os
import shutil

#  PDF 폴더와 다른 폴더의 하위 폴더 이름을 비교하여 같은 이름의 PDF 파일을 새로운 폴더에 복사
#  OCR 요청 시 pdf도 함께 드리기 위함

def collect_matching_pdfs(pdf_folder, other_folder, output_folder):
    # 하위 폴더 이름과 매칭하기 위해 '_bbox'를 제거한 이름 리스트 생성
    other_subfolder_names = [
        os.path.basename(folder).replace('_bbox', '')
        for folder in os.listdir(other_folder)
        if os.path.isdir(os.path.join(other_folder, folder))
    ]

    # 출력 폴더 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # PDF 폴더 내 파일들을 확인
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            # PDF 파일 이름에서 '.pdf' 제거
            pdf_name = pdf_file.replace('.pdf', '')

            # 다른 폴더의 하위 폴더 이름과 같은 경우 새 폴더에 복사
            if pdf_name in other_subfolder_names:
                source_path = os.path.join(pdf_folder, pdf_file)
                destination_path = os.path.join(output_folder, pdf_file)
                shutil.copy2(source_path, destination_path)
                print(f"복사 완료: {pdf_file}")

# 폴더 경로 설정
pdf_folder = 'path/to/pdf_folder'  # PDF 파일들이 있는 폴더 경로
other_folder = 'path/to/other_folder'  # 비교할 하위 폴더들이 있는 경로
output_folder = 'path/to/output_folder'  # 결과를 저장할 폴더 경로

# 함수 호출
collect_matching_pdfs(pdf_folder, other_folder, output_folder)
