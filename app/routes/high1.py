from flask import Blueprint, render_template, request, jsonify
from app.backend import getData
import requests
import re
import os 

def to_float(val):
    """문자열 등급 안에서 숫자만 추출해 float으로 변환"""
    try:
        return float(re.sub(r"[^0-9.]", "", str(val)))
    except:
        return None
    
high1_bp = Blueprint("high1", __name__)


@high1_bp.route('/high1')
def high1():
    return render_template('high1/high1.html',
                           schools=list(getData.school_major_map.keys()),
                           major_map=getData.school_major_map)

@high1_bp.route('/result_1')
def result_1():
    school = request.args.get("school")
    major = request.args.get("major")

    susi_row = getData.hakjong_df[(getData.hakjong_df["university"] == school) & (getData.hakjong_df["major"] == major)]
    jungsi_row = getData.jungsi_df[(getData.jungsi_df["university"] == school) & (getData.jungsi_df["major"] == major)]

    return render_template(
        "high1/result_1.html",
        school=school,
        major=major,
        susi=susi_row.to_dict(orient="records"),
        jungsi=jungsi_row.to_dict(orient="records")
    )

# -----------------------------
#   생기부 방향성 보기 페이지
# -----------------------------
@high1_bp.route('/result_2')
def result_2():
    # 분석할 컴퓨터 관련 키워드
    keywords = ["컴퓨터", "소프트웨어", "SW", "프로그래밍", "개발",
                "코딩", "AI", "인공지능", "데이터", "알고리즘", "정보"]

    dataframes = [getData.setuk_df, getData.changche_df, getData.haengteuk_df]

    # 키워드 → {count: n, sentences: []} 저장
    keyword_info = {k: {"count": 0, "sentences": []} for k in keywords}

    # 모든 content 문장 단위로 분해 후 키워드 탐색
    for df in dataframes:
        for raw_text in df["content"].astype(str):
            # 문장 분리
            sentences = (
                raw_text.replace("!", ".")
                        .replace("?", ".")
                        .split(".")
            )

            for sentence in sentences:
                s = sentence.strip()
                if not s:
                    continue

                # 어떤 키워드가 들어있는지 확인
                for k in keywords:
                    if k in s:
                        keyword_info[k]["count"] += 1
                        # 대표 문장 3개까지만 저장
                        if len(keyword_info[k]["sentences"]) < 3:
                            keyword_info[k]["sentences"].append(s)

    # 등장하지 않은 키워드는 제거
    keyword_info = {k: v for k, v in keyword_info.items() if v["count"] > 0}

    # 등장 횟수 높은 순 정렬
    keyword_info = dict(sorted(keyword_info.items(), key=lambda x: x[1]["count"], reverse=True))

    return render_template("high1/result_2.html", keyword_info=keyword_info)





# -----------------------------
#     자격증 API 수집 페이지
# -----------------------------
@high1_bp.route('/certificates_api')
def certificates_api():
    urls = [
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey="+os.getenv("HIGH1_API_KEY")+"&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=290",
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey="+os.getenv("HIGH1_API_KEY")+"&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=570",
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey="+os.getenv("HIGH1_API_KEY")+"&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=569"
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
@high1_bp.route('/recommend_hakjong')
def recommend_hakjong():
    school = request.args.get("school")
    major = request.args.get("major")

    # 현재 row 찾기
    current_row = getData.hakjong_df[
        (getData.hakjong_df["university"].str.strip() == school.strip()) &
        (getData.hakjong_df["major"].str.strip() == major.strip())
    ]

    if current_row.empty:
        return jsonify({"status": "error", "message": "현재 학교/학과를 찾을 수 없음"})

    current_cut = to_float(current_row.iloc[0]["cut50"])
    if current_cut is None:
        return jsonify({"status": "error", "message": "현재 등급 파싱 실패"})

    # 더 높은 학교 필터링
    higher_schools = []
    for _, row in getData.hakjong_df.iterrows():
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

