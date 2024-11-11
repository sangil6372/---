import os
import shutil

def get_json_files_in_folder(folder_path):
    json_files = {}
    for root, _, files in os.walk(folder_path):
        relative_folder = os.path.relpath(root, folder_path)
        json_files[relative_folder] = set(f for f in files if f.endswith('.json'))
    return json_files

def save_files_in_structure(source_folder, destination_folder, file_structure):
    for folder, files in file_structure.items():
        for file in files:
            # 원본 파일의 전체 경로
            source_path = os.path.join(source_folder, folder, file)
            # 저장할 대상 경로
            target_path = os.path.join(destination_folder, folder)
            os.makedirs(target_path, exist_ok=True)  # 대상 폴더 구조 생성
            shutil.copy2(source_path, target_path)   # 파일 복사

def compare_and_save_folders(compare_folder, target_folder, output_compare, output_target):
    compare_files = get_json_files_in_folder(compare_folder)
    target_files = get_json_files_in_folder(target_folder)

    only_in_compare = {}
    only_in_target = {}
    total_only_in_compare = 0
    total_only_in_target = 0

    # 비교폴더에만 있는 파일 확인
    for folder, files in compare_files.items():
        if folder not in target_files:
            only_in_compare[folder] = files
            total_only_in_compare += len(files)
        else:
            unique_files = files - target_files[folder]
            if unique_files:
                only_in_compare[folder] = unique_files
                total_only_in_compare += len(unique_files)

    # 대상폴더에만 있는 파일 확인
    for folder, files in target_files.items():
        if folder not in compare_files:
            only_in_target[folder] = files
            total_only_in_target += len(files)
        else:
            unique_files = files - compare_files[folder]
            if unique_files:
                only_in_target[folder] = unique_files
                total_only_in_target += len(unique_files)

    # 차이나는 파일을 각각의 폴더 구조로 저장
    save_files_in_structure(compare_folder, output_compare, only_in_compare)
    save_files_in_structure(target_folder, output_target, only_in_target)

    return only_in_compare, only_in_target, total_only_in_compare, total_only_in_target

# 예시 실행
compare_folder = r"C:\Users\USER\Desktop\68_비교__"
target_folder = r"C:\Users\USER\Desktop\68_redundancy"
output_compare = r'C:\Users\USER\Desktop\웅진_북센\booxen-refine-python\test\표미션inline누락분석\68비교폴더에만'
output_target = r'C:\Users\USER\Desktop\웅진_북센\booxen-refine-python\test\표미션inline누락분석\68red대상폴더에만'

only_in_compare, only_in_target, total_only_in_compare, total_only_in_target = compare_and_save_folders(compare_folder, target_folder, output_compare, output_target)

# 결과 출력
print("비교폴더에만 있는 파일:")
for folder, files in only_in_compare.items():
    if files:
        print(f"{folder}에 {len(files)}개 파일: {files}")
print(f"\n비교폴더에만 있는 파일 총 개수: {total_only_in_compare}개")

print("\n대상폴더에만 있는 파일:")
for folder, files in only_in_target.items():
    if files:
        print(f"{folder}에 {len(files)}개 파일: {files}")
print(f"\n대상폴더에만 있는 파일 총 개수: {total_only_in_target}개")
