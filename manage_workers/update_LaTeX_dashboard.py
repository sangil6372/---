import pandas as pd
import tkinter as tk
from tkinter import filedialog
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from tabulate import tabulate

pd.set_option('future.no_silent_downcasting', True)


# Google 스프레드시트에서 데이터를 가져오는 함수
def get_data_from_google_sheets(spreadsheet_url, worksheet_name):
    # Google Sheets API에 접근하기 위한 범위 설정
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # 자격 증명 파일 경로 (개인에 맞게 수정 필요)
    json_key_path = r"C:\Users\USER\PycharmProjects\pythonProject1\웅진북센\작업자관리\fiery-catwalk-434403-c2-89fd46213af3.json"

    # 자격 증명 파일을 통해 인증
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, scope)
    client = gspread.authorize(credentials)

    # 스프레드시트를 URL로 열기
    spreadsheet = client.open_by_url(spreadsheet_url)

    # 워크시트 열기
    worksheet = spreadsheet.worksheet(worksheet_name)

    # 스프레드시트의 헤더 열 정의 (고유하게)
    expected_headers = ['작업자명', '닉네임', '제출 날짜', '이미지 수량', '수식 수량', '표 수량', '금일 수식 이미지 수량', '금일 표 이미지 수량', '금일 수식 수량', '금일 표 수량', '업데이트 날짜']

    # 시트의 데이터를 모두 가져오기
    data = worksheet.get_all_records(expected_headers=expected_headers)

    # 데이터프레임으로 변환
    df = pd.DataFrame(data)

    return df, worksheet

# Google 스프레드시트에 데이터를 한 번에 업로드하는 함수
def upload_dataframe_to_google_sheets(df, worksheet):
    # 스프레드시트의 기존 데이터를 삭제
    worksheet.clear()

    # 현재 날짜와 시간 분단위까지 가져오기
    update_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 업데이트 날짜 열을 F열에 삽입하기 위해 빈 컬럼을 추가 후 순서 설정
    if '업데이트 날짜' not in df.columns:
        df['업데이트 날짜'] = ""

    # 첫 번째 행에만 업데이트 날짜를 입력
    df.loc[0, '업데이트 날짜'] = update_datetime

    # 열 순서 조정 (기존 스프레드시트 열 순서에 맞춤)
    cols = ['작업자명', '닉네임', '제출 날짜', '이미지 수량', '수식 수량', '표 수량', '금일 수식 이미지 수량', '금일 표 이미지 수량', '금일 수식 수량', '금일 표 수량', '업데이트 날짜']
    df = df[cols]

    # NaN 값을 열 데이터 유형에 맞게 변환
    float_cols = df.select_dtypes(include=['float64']).columns
    object_cols = df.select_dtypes(include=['object']).columns

    df.loc[:, float_cols] = df[float_cols].fillna(0)
    df.loc[:, object_cols] = df[object_cols].fillna("")

    # DataFrame을 리스트로 변환
    data = [df.columns.values.tolist()] + df.values.tolist()  # 헤더 포함

    # 스프레드시트 범위에 데이터를 한 번에 업로드
    worksheet.update(range_name='A1', values=data)  # A1 셀부터 데이터 전체 업로드






# Tkinter 초기화
root = tk.Tk()
root.withdraw()  # Tkinter 창 숨기기


# 첫 번째 파일 선택 창 띄우기 (엑셀 파일 선택)
file_path_1 = filedialog.askopenfilename(
    title="수식 엑셀 파일을 선택하세요",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)


# 첫 번째 엑셀 파일 불러오기 (엑셀 파일에 닉네임과 데이터가 있다고 가정)
df_new_1 = pd.read_excel(file_path_1)

# 두 번째 파일 선택 창 띄우기 (엑셀 파일 선택)
file_path_2 = filedialog.askopenfilename(
    title="표 엑셀 파일을 선택하세요",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)

# 두 번째 엑셀 파일 불러오기
df_new_2 = pd.read_excel(file_path_2)

# 'pmadmin162'와 'sangil' 코드네임 제거 (두 파일 모두 동일하게 처리)
df_new_1 = df_new_1[~df_new_1['코드네임'].isin(['pmadmin162', 'sangil'])]
df_new_2 = df_new_2[~df_new_2['코드네임'].isin(['pmadmin162', 'sangil'])]

# 컬럼명 통일
df_new_1.columns = ['닉네임', '제출 날짜', '이미지 수량', '각주 제출 수', '수식 수량', '이미지 제출 수 2', '표 수량', '텍스트 제출 수', '참고문헌 제출 수']
df_new_2.columns = ['닉네임', '제출 날짜', '이미지 수량', '각주 제출 수', '수식 수량', '이미지 제출 수 2', '표 수량', '텍스트 제출 수', '참고문헌 제출 수']

df_new_1['표 수량'] = 0

# '이미지 제출 수 2', '텍스트 제출 수', '각주 제출 수', '참고문헌 제출 수' 열 삭제
df_agg_1 = df_new_1.drop(columns=['이미지 제출 수 2', '텍스트 제출 수', '각주 제출 수', '참고문헌 제출 수'])
df_agg_2 = df_new_2.drop(columns=['이미지 제출 수 2', '텍스트 제출 수', '각주 제출 수', '참고문헌 제출 수'])

# 오늘 날짜로 데이터 필터링
today = datetime.now().strftime('%Y-%m-%d')

# 금일 작업 데이터 추출 (제출 날짜가 오늘인 데이터)
df_today_1 = df_new_1[df_new_1['제출 날짜'] == today]
df_today_2 = df_new_2[df_new_2['제출 날짜'] == today]

# 금일 작업량 계산
# 수식 엑셀 파일에서 금일 수식 이미지 수량
df_today_agg_1 = df_today_1.groupby('닉네임').agg({
    '이미지 수량': 'sum',
    '수식 수량': 'sum'
}).reset_index()
df_today_agg_1.columns = ['닉네임', '금일 수식 이미지 수량', '금일 수식 수량']

# 표 엑셀 파일에서 금일 표 이미지 수량
df_today_agg_2 = df_today_2.groupby('닉네임').agg({
    '이미지 수량': 'sum',
    '표 수량': 'sum'
}).reset_index()
df_today_agg_2.columns = ['닉네임', '금일 표 이미지 수량', '금일 표 수량']

# 금일 작업량 병합
df_today_agg = pd.merge(df_today_agg_1, df_today_agg_2, on='닉네임', how='outer')
df_today_agg = df_today_agg[['닉네임', '금일 수식 이미지 수량', '금일 표 이미지 수량', '금일 수식 수량', '금일 표 수량']]
print(tabulate(df_today_agg, headers='keys', tablefmt='pretty'))


# 두 엑셀 파일 데이터를 합치기
df_combined = pd.concat([df_agg_1, df_agg_2])

# '닉네임'으로 그룹화하고 집계 처리:
# - '이미지 수량' 등은 각각 합산
# - '제출 날짜'는 가장 최신 값 사용
df_agg = df_combined.groupby(['닉네임']).agg({
    '제출 날짜': 'max',  # 최신 날짜 사용
    '이미지 수량': 'sum',
    '수식 수량': 'sum',
    '표 수량' : 'sum'
}).reset_index()

# 기존 데이터와 금일 작업량 데이터를 병합
df_merged = pd.merge(df_agg, df_today_agg, on='닉네임', how='outer')

# 금일 작업량 컬럼에 NaN 값을 0으로 대체
df_merged.fillna({
    '금일 수식 이미지 수량': 0,
    '금일 표 이미지 수량': 0,
    '금일 수식 수량': 0,
    '금일 표 수량': 0
}, inplace=True)

# 그룹화된 데이터 출력
print(tabulate(df_merged, headers='keys', tablefmt='pretty'))

# 구글 스프레드시트에서 기존 작업자명 및 닉네임 데이터 불러오기
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1aKpkoXNAYkweCS_EFbYcjgCS47y85XLeO-Ge7mDeeuU/edit?gid=911524365'  # 스프레드시트 URL로 변경
worksheet_name = 'LaTeX 작업자 현황'  # 워크시트 이름으로 변경
df_existing, worksheet = get_data_from_google_sheets(spreadsheet_url, worksheet_name)

# '닉네임'을 기준으로 기존 데이터와 엑셀 데이터를 병합
df_merged = pd.merge(df_existing, df_merged, on='닉네임', how='left')


# 필요 없는 '_x', '_y' 컬럼 삭제 후 최종 병합된 데이터 사용
df_merged['제출 날짜'] = df_merged['제출 날짜_y']
df_merged['이미지 수량'] = df_merged['이미지 수량_y']
df_merged['수식 수량'] = df_merged['수식 수량_y']
df_merged['표 수량'] = df_merged['표 수량_y'].fillna(df_merged['표 수량_x'])
df_merged['금일 수식 이미지 수량'] = df_merged['금일 수식 이미지 수량_y']
df_merged['금일 표 이미지 수량'] = df_merged['금일 표 이미지 수량_y']
df_merged['금일 수식 수량'] = df_merged['금일 수식 수량_y']
df_merged['금일 표 수량'] = df_merged['금일 표 수량_y']


# 불필요한 컬럼 삭제
df_merged = df_merged.drop(columns=['제출 날짜_x', '이미지 수량_x', '수식 수량_x', '제출 날짜_y', '이미지 수량_y', '수식 수량_y', '금일 수식 이미지 수량_x','금일 수식 이미지 수량_y','금일 표 이미지 수량_x','금일 표 이미지 수량_y', '금일 수식 수량_x', '금일 수식 수량_y', '금일 표 수량_x', '금일 표 수량_y', '표 수량_x', '표 수량_y'])

# 병합된 데이터 출력
print(tabulate(df_merged, headers='keys', tablefmt='pretty'))


# 업데이트 여부 확인
update_confirm = input("Google 스프레드시트를 업데이트하시겠습니까? (y/n): ")

if update_confirm.lower() == 'y':
    # 병합된 데이터를 구글 스프레드시트에 업로드
    upload_dataframe_to_google_sheets(df_merged, worksheet)
    print("Google 스프레드시트가 성공적으로 업데이트되었습니다.")
else:
    print("업데이트가 취소되었습니다.")
