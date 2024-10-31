import os
import json

# 확인할 키워드 목록
gpt_failure_keywords = [
    "unable", "sorry", "cannot", "can't", "assist", "help", "verify", "process", "access",
    "error", "issue", "problem", "extract", "recognize", "fail", "failure", "missing",
    "unsupported", "invalid", "incorrect", "apologize", "analyze", "recognition", "read",
    "retrieve", "provide", "clarify", "understand", "interpret", "denied", "data", "result", "i'm", "correct",
    "image", "text", "extract", "processing", "recognition", "analysis", "no data", "failed", "extract", "ocr",
    "죄송", "수정", "이미지", "추출", "분석", "확인", "처리", "지원", "문제", "실패", "텍스트",
    "인식", "오류", "불가", "다음과"
]

# 상위 폴더 경로 지정
base_folder = 'your_base_folder_path'  # 상위 폴더 경로를 지정하세요

# 하위 폴더 순회 및 JSON 파일 처리
for root, dirs, files in os.walk(base_folder):
    for file in files:
        if file.endswith('.json'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                # shapes 배열에서 각 shape의 latex 속성 확인
                for shape in data.get("shapes", []):
                    latex_content = shape.get("latex", "")
                    # latex 내용에 키워드가 포함되는지 확인
                    if any(keyword in latex_content for keyword in gpt_failure_keywords):
                        print(f"GPT 오류 키워드 발견: {file_path}")
                        break  # 한 번 발견되면 해당 파일에 대해서는 더 이상 검사하지 않고 넘어감
