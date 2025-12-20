
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
# 정시 / 수시 CSV
jungsi_df = pd.read_csv(os.path.join(DATA_FOLDER, "jungsi_cut.csv"))
hakjong_df = pd.read_csv(os.path.join(DATA_FOLDER, "hakjong_cut.csv"))

studentInfo = pd.read_csv(os.path.join(BASE_DIR, "data\\student_info.csv"))
RanksDf = pd.read_csv(os.path.join(BASE_DIR, "data\\grades.csv"))


# 생기부 CSV
setuk_df = pd.read_csv(os.path.join(DATA_FOLDER, 'detailed_abilities.csv'))
changche_df = pd.read_csv(os.path.join(DATA_FOLDER, 'creative_activities.csv'))
haengteuk_df = pd.read_csv(os.path.join(DATA_FOLDER, 'behavioral_characteristics.csv'))

#수시 컷
susicut_df = pd.read_csv(os.path.join(DATA_FOLDER, "susicut.csv"))
susicut_df_preprocessed = susicut_df

# 학교 → 학과 매핑
school_major_map = {}
for uni in jungsi_df["university"].unique():
    majors = jungsi_df[jungsi_df["university"] == uni]["major"].unique().tolist()
    school_major_map[uni] = majors