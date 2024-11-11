import os


def compare_folders(base_folder, text_file_path):
    # 폴더 내부의 하위 폴더명 가져오기
    subfolders = set(os.listdir(base_folder))

    # 메모장 파일에서 폴더명 읽기 (각 줄마다 공백 제거)
    with open(text_file_path, 'r', encoding='utf-8') as f:
        listed_folders = {line.strip() for line in f}

    # 메모장에 없는 폴더, 메모장에만 있는 폴더, 공통 폴더 계산
    missing_in_text = subfolders - listed_folders
    only_in_text = listed_folders - subfolders
    common_folders = subfolders & listed_folders

    # 결과 출력
    print("메모장에 없는 폴더명:")
    for folder in missing_in_text:
        print(folder)

    print("\n메모장에만 있는 폴더명:")
    for folder in only_in_text:
        print(folder)

    print(f"\n공통 폴더 개수: {len(common_folders)}")


# 사용 예시
base_folder = r'C:\Users\USER\Desktop\테이블 미션\gpt_inline_updated'
text_file_path = r"C:\Users\USER\Downloads\폴더생성용.txt"
compare_folders(base_folder, text_file_path)


