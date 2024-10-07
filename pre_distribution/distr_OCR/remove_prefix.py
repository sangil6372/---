import os


def rename_files_in_subfolders(root_folder):
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            # 언더바가 두 개 이상 있는 파일에 대해 수정
            if filename.count('_') >= 2:
                # 첫 번째 언더바 이전의 내용과 그 언더바를 제거
                first_underscore_index = filename.find('_')
                new_filename = filename[first_underscore_index + 1:]

                # 파일 경로 생성
                old_path = os.path.join(foldername, filename)
                new_path = os.path.join(foldername, new_filename)

                # 파일 이름 변경
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")


# 사용할 폴더 경로
root_folder = r"C:\Users\USER\Desktop\웅진 북센\booxen-refine-python\pre_distribution\distr_OCR\1004_ai_ocr"  # 이 부분을 실제 폴더 경로로 바꾸세요.

rename_files_in_subfolders(root_folder)
