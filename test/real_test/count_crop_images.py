import os

def count_files_in_folder(folder_path):
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        file_count += len(files)
    return file_count

# 폴더 경로를 입력하세요
folder_path = input("폴더 경로를 입력하세요: ")
total_files = count_files_in_folder(folder_path)
print(f"폴더 '{folder_path}'의 전체 파일 개수: {total_files}")
