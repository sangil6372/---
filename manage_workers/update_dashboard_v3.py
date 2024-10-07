import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import boto3
from datetime import datetime

from env import settings


def count_files_in_folder(bucket_name, folder_path):
    # S3 클라이언트 생성
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_CONFIG['aws_access_key_id'],
                      aws_secret_access_key=settings.AWS_CONFIG['aws_secret_access_key'],
                      region_name=settings.AWS_CONFIG['region'])

    # 파일 개수 카운팅 초기화
    file_count = 0
    continuation_token = None

    while True:
        if continuation_token:
            result = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path, ContinuationToken=continuation_token)
        else:
            result = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)

        # JSON 파일 개수 카운팅
        if 'Contents' in result:
            file_count += len([j for j in result['Contents'] if j['Key'].endswith('.json')])

        # 더 많은 객체가 있으면 계속 요청
        if result.get('IsTruncated'):
            continuation_token = result.get('NextContinuationToken')
        else:
            break

    return file_count


def count_files_in_folder_paper(bucket_name, folder_path, step):
    # S3 클라이언트 생성
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_CONFIG['aws_access_key_id'],
                      aws_secret_access_key=settings.AWS_CONFIG['aws_secret_access_key'],
                      region_name=settings.AWS_CONFIG['region'])

    # 파일 개수 카운팅 초기화
    base_count = 0
    step_count = 0
    continuation_token = None

    while True:
        if continuation_token:
            result_step = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path + step,
                                             ContinuationToken=continuation_token)
        else:
            result_step = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path + step)

            # JSON 파일 개수 카운팅
        if 'Contents' in result_step:
            step_count += len([j for j in result_step['Contents'] if j['Key'].endswith('.json')])

        # 더 많은 객체가 있으면 계속 요청
        if result_step.get('IsTruncated'):
            continuation_token = result_step.get('NextContinuationToken')
        else:
            break

    continuation_token = None
    while True:
        if continuation_token:
            result_base = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path,
                                             ContinuationToken=continuation_token)

        else:
            result_base = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)

            # JSON 파일 개수 카운팅
        if 'Contents' in result_base:
            base_count += len([j for j in result_base['Contents'] if j['Key'].endswith('.png')])

        # 더 많은 객체가 있으면 계속 요청
        if result_base.get('IsTruncated'):
            continuation_token = result_base.get('NextContinuationToken')
        else:
            break

    return [base_count, step_count]


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# 개인에 따라 수정 필요 - 다운로드 받았던 키 값 경로
json_key_path = r"C:/Users/PC/Downloads/fiery-catwalk-434403-c2-89fd46213af3.json"

credential = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, scope)
gc = gspread.authorize(credential)

# 개인에 따라 수정 필요 - 스프레드시트 url 가져오기
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1aKpkoXNAYkweCS_EFbYcjgCS47y85XLeO-Ge7mDeeuU/edit?gid=0#gid=0"

doc = gc.open_by_url(spreadsheet_url)

# 개인에 따라 수정 필요 - 시트 선택하기 (시트명을 그대로 입력해주면 된다.)
sheet = doc.worksheet("작업 현황")

# 데이터 프레임 생성하기
df = pd.DataFrame(sheet.get_all_values())

# 불러온 데이터 프레임 정리
df.rename(columns=df.iloc[0], inplace=True)
df.drop(df.index[0], inplace=True)

df.to_excel(f"C:/Users/PC/Desktop/2024/24-ds-111_웅진북센/6. 작업진행률 로그/{datetime.now().strftime('%Y_%m_%d_%H_%M')}.xlsx")

processed_datas = []
for i, row in df.iterrows():
    if row['작업 중 폴더명'] == "#N/A":
        processed_datas.append(0)
    else:
        if row['작업 단계'] == 'B-BOX':
            step = '_bbox'
        elif row['작업 단계'] == 'OCR':
            step = '_ocr'
        elif row['작업 단계'] == 'Latex':
            step = '_latex'

        if int(row['작업 중 폴더명'].split('_')[0]) <= 107:
            bucket_name = 'project-24-pd-020'
            base_path = 'project1527/storage/'
            folder_path = base_path + row['작업 중 폴더명'] + step
            processed_datas.append(count_files_in_folder(bucket_name, folder_path))
        elif int(row['작업 중 폴더명'].split('_')[0]) > 107:
            bucket_name = 'project-24-pd-020'
            base_path = 'project1529/storage/'
            folder_path = base_path + row['작업 중 폴더명']
            processed_datas.append(count_files_in_folder_paper(bucket_name, folder_path, step))

update_F = []
update_G = []
for i, data in enumerate(processed_datas):
    if type(data) == int:
        update_G.append(data)
        update_F.append(f"=INDEX('관리자용'!B:B, MATCH(1, ('관리자용'!F:F = B{2 + i}) * ('관리자용'!H:H = \"진행 중\"), 0))")
        # if data == df.loc[1+i, '작업 수량']:
        # continue
        # else:
        # sheet.update_acell(f"G{2+i}", data)
        # print(f"G{2+i}셀을 업데이트 했습니다.")
        # sheet.update_acell(f"F{2+i}", f"=INDEX('관리자용'!B:B, MATCH(1, ('관리자용'!F:F = B{2+i}) * ('관리자용'!H:H = \"진행 중\"), 0))")
        # print(f"F{2+i}셀을 업데이트 했습니다.")

    elif type(data) == list:
        update_G.append(data[1])
        update_F.append(data[0])
        """if (data[1] == df.loc[1+i, '작업 수량']) and (data[0] == df.loc[1+i, '전체 페이지']):
            print(f"{2+i}행은 업데이트 할 내용이 없습니다.")
            continue
        else:
            if data[1] == df.loc[1+i, '작업 수량']:
                continue
            else:
                sheet.update_acell(f"G{2+i}", data[1])
                print(f"G{2+i}셀을 업데이트 했습니다.")
            if data[0] == df.loc[1+i, '전체 페이지']:
                continue
            else:
                sheet.update_acell(f"F{2+i}", data[0])
                print(f"F{2+i}셀을 업데이트 했습니다.")"""

cell_range = f'G2:{len(update_G) + 1}'
sheet.update([[val] for val in update_G], cell_range)
# cell_range = f'F2:G{len(update_F)+1}'
# sheet.update([[val] for val in update_F], cell_range)

now = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"{now} 업데이트 완료")
sheet.update_acell("I2", now)