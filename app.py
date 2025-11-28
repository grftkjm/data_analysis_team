from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import re
import requests

app = Flask(__name__)

DATA_FOLDER = "data"

# -------- CSV 로드 --------
jungsi_df = pd.read_csv(os.path.join(DATA_FOLDER, "jungsi_realistic.csv"))
hakjong_df = pd.read_csv(os.path.join(DATA_FOLDER, "hakjong_realistic.csv"))

setuk_df = pd.read_csv(os.path.join(DATA_FOLDER, "세부능력 종합 특기사항.csv"))
changche_df = pd.read_csv(os.path.join(DATA_FOLDER, "창의적체험활동.csv"))
haengteuk_df = pd.read_csv(os.path.join(DATA_FOLDER, "행동특성.csv"))

# --- 학교 → 학과 매핑 ---
school_major_map = {}
for uni in jungsi_df["university"].unique():
    majors = jungsi_df[jungsi_df["university"] == uni]["major"].unique().tolist()
    school_major_map[uni] = majors


def to_float(val):
    """문자열 등급 안에서 숫자만 추출해 float으로 변환"""
    try:
        return float(re.sub(r"[^0-9.]", "", str(val)))
    except:
        return None


# -----------------------------
#            INDEX
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -----------------------------
#         입시 분석 선택
# -----------------------------
@app.route('/analysis')
def analysis():
    return render_template('analysis.html')


# -----------------------------
#        고1 선택 페이지
# -----------------------------
@app.route('/high1')
def high1():
    return render_template(
        'high1.html',
        schools=list(school_major_map.keys()),
        major_map=school_major_map
    )


# -----------------------------
#         고1 결과 페이지
# -----------------------------
@app.route('/result_1')
def result_1():
    school = request.args.get("school")
    major = request.args.get("major")

    susi_row = hakjong_df[(hakjong_df["university"] == school) &
                          (hakjong_df["major"] == major)]
    jungsi_row = jungsi_df[(jungsi_df["university"] == school) &
                           (jungsi_df["major"] == major)]

    return render_template(
        "result_1.html",
        school=school,
        major=major,
        susi=susi_row.to_dict(orient="records"),
        jungsi=jungsi_row.to_dict(orient="records")
    )


# -----------------------------
#      생기부 방향성 페이지
# -----------------------------
@app.route('/result_2')
def result_2():
    keywords = ["컴퓨터", "소프트웨어", "SW", "프로그래밍", "개발",
                "코딩", "AI", "인공지능", "데이터", "알고리즘", "정보"]

    dataframes = [setuk_df, changche_df, haengteuk_df]

    keyword_info = {k: {"count": 0, "sentences": []} for k in keywords}

    for df in dataframes:
        for raw in df["content"].astype(str):
            sentences = (
                raw.replace("!", ".")
                   .replace("?", ".")
                   .split(".")
            )
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                for k in keywords:
                    if k in s:
                        keyword_info[k]["count"] += 1
                        if len(keyword_info[k]["sentences"]) < 3:
                            keyword_info[k]["sentences"].append(s)

    keyword_info = {k: v for k, v in keyword_info.items() if v["count"] > 0}
    keyword_info = dict(sorted(keyword_info.items(),
                               key=lambda x: x[1]["count"], reverse=True))

    return render_template("result_2.html", keyword_info=keyword_info)


# -----------------------------
#     자격증 API 수집 페이지
# -----------------------------
@app.route('/certificates_api')
def certificates_api():
    urls = [
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=290",
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=570",
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=569"
    ]

    cert_list = set()

    for url in urls:
        try:
            data = requests.get(url).json()
            items = data.get("dataSearch", {}).get("content", [])

            for item in items:
                q = item.get("qualifications", "")
                if q:
                    parts = q.replace("\n", ",").split(",")
                    for c in parts:
                        c = c.strip()
                        if len(c) > 1:
                            cert_list.add(c)

        except:
            continue

    # 정렬
    cert_list = sorted(list(cert_list))

    return jsonify({"status": "ok", "data": cert_list})


# -----------------------------
#     더 높은 학종 입결 추천 (상위 3개)
# -----------------------------
@app.route('/recommend_hakjong')
def recommend_hakjong():
    school = request.args.get("school")
    major = request.args.get("major")

    # 현재 row 찾기
    current_row = hakjong_df[
        (hakjong_df["university"].str.strip() == school.strip()) &
        (hakjong_df["major"].str.strip() == major.strip())
    ]

    if current_row.empty:
        return jsonify({"status": "error", "message": "현재 학교/학과를 찾을 수 없음"})

    current_cut = to_float(current_row.iloc[0]["cut50"])
    if current_cut is None:
        return jsonify({"status": "error", "message": "현재 등급 파싱 실패"})

    # 더 높은 학교 필터링
    higher_schools = []
    for _, row in hakjong_df.iterrows():
        cut = to_float(row["cut50"])
        if cut is None:
            continue
        
        if cut < current_cut:  # 더 높은 입결
            higher_schools.append({
                "university": row["university"],
                "major": row["major"],
                "cut50": cut,
                "diff": round(current_cut - cut, 2)
            })

    # cut50 오름차순 정렬
    higher_schools.sort(key=lambda x: x["cut50"])

    # 뒤에서 3개
    bottom3 = higher_schools[-3:]

    return jsonify({
        "status": "ok",
        "current_cut": current_cut,
        "data": bottom3
    })



# -----------------------------
#             RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
