import os


def rename_files_in_folder(folder_path):
    # 폴더 내의 파일 목록을 가져옴
    for filename in os.listdir(folder_path):
        # 파일이 아닌 경우 건너뛰기 (디렉토리일 경우)
        if os.path.isdir(os.path.join(folder_path, filename)):
            continue

        # 파일명을 언더바("_")로 분리
        parts = filename.split('_')

        # 첫 번째 부분(번호)와 언더바를 제거한 새로운 파일명 생성
        if len(parts) > 1:
            new_filename = '_'.join(parts[1:])

            # 기존 파일 경로와 새 파일 경로
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)

            # 파일명 변경
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {filename} -> {new_filename}")


# 폴더 경로 지정 (여기에 폴더 경로를 입력하세요)
folder_path = r"C:\Users\박상일\Desktop\0207\updated"

# 파일명 변경 함수 실행
rename_files_in_folder(folder_path)
