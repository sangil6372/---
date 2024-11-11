

import os
import shutil

def copy_matching_png_files(first_folder, second_folder):
    # 첫 번째 폴더의 하위 폴더들을 순회하며 JSON 파일 확인
    for root, dirs, files in os.walk(first_folder):
        for file in files:
            if file.endswith('.json'):
                # 전체 이름 (쪽수 포함) 추출 (예: 123456_1.json -> 123456_1)
                full_name = file.rsplit('.', 1)[0]
                png_file = f"{full_name}.png"

                # 두 번째 폴더에서 해당 이름의 PNG 파일을 찾기
                for root2, dirs2, files2 in os.walk(second_folder):
                    if png_file in files2:
                        # JSON 파일이 있는 첫 번째 폴더에 PNG 파일 복사
                        png_src = os.path.join(root2, png_file)
                        png_dest = os.path.join(root, png_file)
                        shutil.copy2(png_src, png_dest)
                        break  # PNG 파일을 찾았으면 더 이상 찾을 필요 없음

# 사용 예시
first_folder = r"C:\Users\USER\Desktop\새 폴더 (2)"
second_folder = r"C:\Users\USER\Desktop\_out 전체\redundancy_out2"
copy_matching_png_files(first_folder, second_folder)
