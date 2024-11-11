import os
import shutil
import pandas as pd

base_path = r"C:\Users\USER\Desktop\변경된 수식미션"
excel_path = r"C:\Users\USER\Downloads\도서 정제  관리 시트.xlsx"
out_base = r"./LaTeX_분류완료"

df = pd.read_excel(excel_path, sheet_name="총괄")

filenames = {name.split('_', 1)[1] : name.split('_', 1)[0] for name in df["분류.1"]}

for base, dirs, files in os.walk(base_path):
    for file in files:
        if len(file.split('_')[0]) == 4:
            if len(file.split('_')) == 3:
                key = file.split('_')[1]
                out_folder = filenames[key]+"_"+key
                out_path = os.path.join(out_base, out_folder)
                os.makedirs(out_path, exist_ok=True)

                shutil.copy(os.path.join(base, file), os.path.join(out_path, file))
            elif len(file.split('_')) == 4:
                key = "_".join(file.split('_')[1:3])
                out_folder = filenames[key]+"_"+key
                out_path = os.path.join(out_base, out_folder)
                os.makedirs(out_path, exist_ok=True)
                
                shutil.copy(os.path.join(base, file), os.path.join(out_path, file))
            else:
                print('파일명에 이상이 있습니다.',file)
        else:
            if len(file.split('_')) == 2:
                key = file.split('_')[0]
                out_folder = filenames[key]+"_"+key
                out_path = os.path.join(out_base, out_folder)
                os.makedirs(out_path, exist_ok=True)
                
                shutil.copy(os.path.join(base, file), os.path.join(out_path, file))
            elif len(file.split('_')) == 3:
                key = "_".join(file.split('_')[0:2])
                out_folder = filenames[key]+"_"+key
                out_path = os.path.join(out_base, out_folder)
                os.makedirs(out_path, exist_ok=True)
                
                shutil.copy(os.path.join(base, file), os.path.join(out_path, file))
            else:
                print('파일명에 이상이 있습니다.',file)