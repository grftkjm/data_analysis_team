from flask import Blueprint, render_template, request, jsonify
from app.backend.analysis import getData
import re

def to_float(val):
    """문자열 등급 안에서 숫자만 추출해 float으로 변환"""
    try:
        return float(re.sub(r"[^0-9.]", "", str(val)))
    except:
        return None

high1_bp = Blueprint("high1", __name__)

# -----------------------------
# 고1 메인 페이지
# -----------------------------
@high1_bp.route('/high1')
def high1():
    return render_template(
        'high1/high1.html',
        schools=list(getData.school_major_map.keys()),
        major_map=getData.school_major_map
    )

# -----------------------------
# 고1 결과 페이지
# -----------------------------
@high1_bp.route('/result_1')
def result_1():

    school = request.args.get("school")
    major  = request.args.get("major")

    susi_row = getData.hakjong_df[
        (getData.hakjong_df["university"] == school) &
        (getData.hakjong_df["major"] == major)
    ]

    jungsi_row = getData.jungsi_df[
        (getData.jungsi_df["university"] == school) &
        (getData.jungsi_df["major"] == major)
    ]

    return render_template(
        "high1/result_1.html",
        school=school,
        major=major,
        susi=susi_row.to_dict(orient="records"),
        jungsi=jungsi_row.to_dict(orient="records")
    )

# -----------------------------
# 생기부 방향성 (모달용)
# -----------------------------
@high1_bp.route('/result_2')
def result_2():
    keywords = [
        "컴퓨터", "소프트웨어", "SW", "프로그래밍", "개발",
        "코딩", "AI", "인공지능", "데이터", "알고리즘", "정보"
    ]

    dataframes = [
        getData.setuk_df,
        getData.changche_df,
        getData.haengteuk_df
    ]

    keyword_info = {k: {"count": 0, "sentences": []} for k in keywords}

    for df in dataframes:
        for raw_text in df["content"].astype(str):
            sentences = (
                raw_text.replace("!", ".")
                        .replace("?", ".")
                        .split(".")
            )

            for sentence in sentences:
                s = sentence.strip()
                if not s:
                    continue

                for k in keywords:
                    if k in s:
                        keyword_info[k]["count"] += 1
                        if len(keyword_info[k]["sentences"]) < 3:
                            keyword_info[k]["sentences"].append(s)

    keyword_info = {
        k: v for k, v in keyword_info.items()
        if v["count"] > 0
    }

    keyword_info = dict(
        sorted(
            keyword_info.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
    )

    return render_template(
        "high1/result_2.html",
        keyword_info=keyword_info
    )

# -----------------------------
# 더 높은 학종 추천
# -----------------------------
@high1_bp.route('/recommend_hakjong')
def recommend_hakjong():
    school = request.args.get("school")
    major  = request.args.get("major")

    current_row = getData.hakjong_df[
        (getData.hakjong_df["university"].str.strip() == school.strip()) &
        (getData.hakjong_df["major"].str.strip() == major.strip())
    ]

    if current_row.empty:
        return jsonify({"status": "error"})

    current_cut = to_float(current_row.iloc[0]["cut50"])
    if current_cut is None:
        return jsonify({"status": "error"})

    higher = []

    for _, row in getData.hakjong_df.iterrows():
        cut = to_float(row["cut50"])
        if cut is None:
            continue

        if cut < current_cut:
            higher.append({
                "university": row["university"],
                "major": row["major"],
                "cut50": cut,
                "diff": round(current_cut - cut, 2)
            })

    higher.sort(key=lambda x: x["cut50"])
    bottom3 = higher[-3:]

    return jsonify({
        "status": "ok",
        "current_cut": current_cut,
        "data": bottom3
    })
