import os
import json

# JSON 파일들이 포함된 상위 폴더 경로
parent_folder_path = r"C:\Users\USER\Desktop\웅진_북센\booxen-refine-python\GPT\GPT_UPDATED\gpt_in_out_updated"

# 조건에 맞는 label 값 목록
target_labels = {"FORMULA", "ALIGN", "ALIGN*", "EQUATION", "MULTLINE", "OUTLINE", "GATHER"}

# 모든 하위 폴더와 JSON 파일 순회
for root, _, files in os.walk(parent_folder_path):
    for file_name in files:
        if file_name.endswith(".json"):
            json_path = os.path.join(root, file_name)

            # JSON 파일 읽기
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 조건에 맞는 label의 latex 문자열에서 'latex' 단어 삭제 후 strip
            for shape in data.get("shapes", []):
                if shape.get("label") in target_labels:
                    latex_string = shape.get("latex", "")
                    shape["latex"] = latex_string.replace("latex", "").strip()

            # 수정된 JSON 파일 저장
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

print("모든 JSON 파일이 수정되었습니다.")
