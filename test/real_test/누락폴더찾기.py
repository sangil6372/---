# 두 개의 파일 경로를 설정합니다.
file1_path = r"C:\Users\USER\Downloads\test1.txt"
file2_path = r"C:\Users\USER\Downloads\test2.txt"
# 파일 내용을 읽고, 각 파일 이름을 집합에 저장합니다.
with open(file1_path, 'r', encoding='utf-8') as file1:
    file1_names = set(file1.read().splitlines())

with open(file2_path, 'r', encoding='utf-8') as file2:
    file2_names = set(file2.read().splitlines())

# 서로에 없는 파일명을 계산합니다.
only_in_file1 = file1_names - file2_names
only_in_file2 = file2_names - file1_names

# 결과를 출력합니다.
print("File 1에만 있는 파일들:")
for name in only_in_file1:
    print(name)

print("\nFile 2에만 있는 파일들:")
for name in only_in_file2:
    print(name)
