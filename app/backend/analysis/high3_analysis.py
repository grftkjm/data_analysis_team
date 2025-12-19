import os
import pandas as pd

# --------------------------------------------------
# 유틸
# --------------------------------------------------
def parse_num(x):
    return float(str(x).replace("(임의)", "").strip())


# --------------------------------------------------
# 학생 내신 평균
# --------------------------------------------------
def get_student_susi_avg(student):
    df = student.grades.copy()
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    df = df.dropna(subset=["rank"])
    return round(df["rank"].mean(), 2)


# --------------------------------------------------
# 메인 분석
# --------------------------------------------------
def analyzing(student, school, major, susi_df, jungsi_df):

    # ======================
    # 입력 성적
    # ======================
    susi_avg = get_student_susi_avg(student)
    jungsi_scores = student.jungsi_scores

    # ======================
    # 수시 분석 (보수적)
    # ======================
    expected_susi_avg = round(susi_avg + 0.1, 2)

    susi_possible = []
    for _, row in susi_df.iterrows():
        try:
            cut = parse_num(row["cut50"])
            if expected_susi_avg <= cut:
                susi_possible.append({
                    "university": row["university"],
                    "major": row["major"],
                    "cut50": cut
                })
        except:
            continue

    # ======================
    # 정시 분석 (현재 성적 기준 ONLY)
    # ======================
    jungsi_possible = []

    kor = jungsi_scores["kor"]
    math = jungsi_scores["math"]
    eng = jungsi_scores["eng"]
    sci_avg = (jungsi_scores["inq1"] + jungsi_scores["inq2"]) / 2

    for _, row in jungsi_df.iterrows():
        try:
            if (
                kor >= parse_num(row["korean70"]) and
                math >= parse_num(row["math70"]) and
                eng >= parse_num(row["english70"]) and
                sci_avg >= parse_num(row["science70"])
            ):
                jungsi_possible.append({
                    "university": row["university"],
                    "major": row["major"]
                })
        except:
            continue

    # ======================
    # 수시 vs 정시 판단
    # ======================
    if len(jungsi_possible) > len(susi_possible):
        pick = "정시"
        reasons = [
            "현재 정시 성적으로 지원 가능한 대학 수가 더 많음",
            "고3 시점에서 내신 상승 여지가 제한적"
        ]
    else:
        pick = "수시"
        reasons = [
            "내신 기반으로 안정적인 지원 가능",
            "정시에서 뚜렷한 상향 이점이 없음"
        ]

    # ======================
    # 결과 반환
    # ======================
    return {
        "susi": {
            "naesin_avg": susi_avg,
            "expected_avg": expected_susi_avg,
            "possible_list": susi_possible
        },
        "jungsi": {
            "scores_keep": jungsi_scores,
            "possible_list": jungsi_possible
        },
        "recommendation": {
            "pick": pick,
            "reasons": reasons
        }
    }
