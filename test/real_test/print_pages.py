import os
import pandas as pd

base_path = r"C:\Users\USER\Desktop\웅진_북센\booxen-refine-python\test\LATEX현황체크\LaTeX_분류완료"

a_dict = {}
for folder in os.listdir(base_path):
    a_dict[folder] = {}
    a_dict[folder]['json'] = len([file for file in os.listdir(os.path.join(base_path, folder)) if file.endswith('json')])

pd.DataFrame(a_dict).T.to_excel(os.path.join(base_path, "./abc.xlsx"))