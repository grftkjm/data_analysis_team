
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
# 정시 / 수시 CSV
jungsi_df = pd.read_csv(os.path.join(DATA_FOLDER, "jungsi_cut.csv"))
hakjong_df = pd.read_csv(os.path.join(DATA_FOLDER, "hakjong_cut.csv"))

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