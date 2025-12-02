
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

os.path.join(DATA_FOLDER)
#생기부 데이터 로드 
df_StudentInfo = pd.read_csv(os.path.join(DATA_FOLDER, "학생정보.csv"))
df_behaviorCharacteristics = pd.read_csv(os.path.join(DATA_FOLDER, "행동특성.csv"))
df_detailedCharacteristics = pd.read_csv(os.path.join(DATA_FOLDER, "세부능력 종합 특기사항.csv"))
df_creativeActivities = pd.read_csv(os.path.join(DATA_FOLDER, "창의적체험활동.csv"))
df_1_1_grade = pd.read_csv(os.path.join(DATA_FOLDER, "1학년 1학기 성적.csv"))
df_1_2_grade = pd.read_csv(os.path.join(DATA_FOLDER, "1학년 2학기 성적.csv"))
df_2_1_grade = pd.read_csv(os.path.join(DATA_FOLDER, "2학년 1학기 성적.csv"))
df_2_2_grade = pd.read_csv(os.path.join(DATA_FOLDER, "2학년 2학기 성적.csv"))
df_3_1_grade = pd.read_csv(os.path.join(DATA_FOLDER, "3학년 1학기 성적.csv"))
df_3_2_grade = pd.read_csv(os.path.join(DATA_FOLDER, "3학년 2학기 성적.csv"))
# 정시 / 수시 CSV
jungsi_df = pd.read_csv(os.path.join(DATA_FOLDER, "jungsi_realistic.csv"))
hakjong_df = pd.read_csv(os.path.join(DATA_FOLDER, "hakjong_realistic.csv"))

# 생기부 CSV
setuk_df = pd.read_csv(os.path.join(DATA_FOLDER, "세부능력 종합 특기사항.csv"))
changche_df = pd.read_csv(os.path.join(DATA_FOLDER, "창의적체험활동.csv"))
haengteuk_df = pd.read_csv(os.path.join(DATA_FOLDER, "행동특성.csv"))

#수시 컷
susicut_df = pd.read_csv(os.path.join(DATA_FOLDER, "susicut.csv"))
susicut_df_preprocessed = susicut_df

# 학교 → 학과 매핑
school_major_map = {}
for uni in jungsi_df["university"].unique():
    majors = jungsi_df[jungsi_df["university"] == uni]["major"].unique().tolist()
    school_major_map[uni] = majors