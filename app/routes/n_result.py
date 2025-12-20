from flask import Blueprint, render_template, request, current_app
from app.backend.analysis import getData
from app.backend.analysis.getStuData import create_student_from_pdf
from app.backend.analysis.high3_analysis import analyzing
from app.backend.analysis import testData
n_result_bp = Blueprint("n_result", __name__)
import csv

def parse_subjects(combo):
    """과목 조합 문자열을 리스트로 변환 (예: '국수영' -> ['kor', 'math', 'eng'])"""
    s = combo.replace(" ", "")
    subs = []
    if "국" in s: subs.append("kor")
    if "수" in s: subs.append("math")
    if "영" in s: subs.append("eng")
    if "탐1" in s or "탐(1)" in s: subs.append("inq1")
    if "탐2" in s: subs.append("inq2")
    return list(dict.fromkeys(subs))

@n_result_bp.route("/n_result", methods=["POST"])
def n_result():
    # ---- 입력값 ----
    grades = {
        "kor": int(request.form["kor_grade"]),
        "math": int(request.form["math_grade"]),
        "eng": int(request.form["eng_grade"]),
        "inq1": int(request.form["inq1_grade"]),
        "inq2": int(request.form["inq2_grade"]),
    }
    inq1_percent = int(request.form["inq1_percent"])
    inq2_percent = int(request.form["inq2_percent"])
    eng_grade = grades['eng']
    rows = []    
    with open(getData.aca, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            subjects = parse_subjects(r["subject_combo"])
            my_sum = sum(grades[s] for s in subjects)
            passable = my_sum <= int(r["max_grade_sum"])

            status = "불가"
            if r["academy"] == "강남대성":
                if passable and r["selection_type"] == "우선선발":
                    status = "100%장학"
                elif passable and r["selection_type"] == "선착선발":
                    status = "50%장학"
            else:
                if passable:
                    status = "가능"
            rows.append({
                "academy": r["academy"],
                "branch": r["branch"],
                "selection": r["selection_type"],
                "track": "인문" if "국" in r["subject_combo"] else "자연",
                "status": status,
            })

    is_science = True  # 이후 계열 선택으로 확장 가능
    # 1. 지표 계산
    inq_avg = (inq1_percent + inq2_percent) / 2
    
    # 영어 감점 계산 (3등급부터 등급당 2점씩 감점 예시)
    eng_penalty = 0
    if eng_grade >= 3:
        eng_penalty = (eng_grade - 2) * 2

    recommends = []

    # 2. 강남대성 판단 로직 개선
    kd_score = inq_avg - eng_penalty
    if kd_score >= 90:
        recommends.append({
            "type": "강남대성 우선선발",
            "desc": f"높은 탐구 백분위({inq_avg})로 장학 혜택 및 우선 입반이 유력합니다.",
            "label": "매우 유력",
            "level": "best" # CSS의 .best 클래스와 연결
        })
    else:
        recommends.append({
            "type": "강남대성 일반선발",
            "desc": f"안정적인 합격권이나 영어 감점을 고려한 전략적 지원이 필요합니다.",
            "label": "보통",
            "level": "mid"  # CSS의 .mid 클래스와 연결
        })

    # 3. 시대인재 판단 로직 개선
    if inq_avg >= 88:
        recommends.append({
            "type": "시대인재 선착순 전형",
            "desc": "백분위 기반 선착순 전형에서 매우 유리한 위치에 있습니다.",
            "label": "추천",
            "level": "good" # CSS의 .good 클래스와 연결
        })

    # 4. 메디컬 특화 로직
    if is_science and inq_avg >= 95:
        recommends.append({
            "type": "최상위 메디컬반",
            "desc": "과탐 고득점을 바탕으로 한 의치한약수 집중 케어반 지원을 권장합니다.",
            "label": "강력 추천",
            "level": "best"
        })

    summary = f"현재 영어 {eng_grade}등급으로 인한 감점 리스크가 있으나, 탐구 평균({inq_avg:.1f})이 매우 탄탄합니다. 이를 전략적으로 활용할 수 있는 재종반 배정이 필요합니다."

    return render_template(
        "n_result.html",
        recommends=recommends,
        summary=summary,
        inq_avg=inq_avg,
        eng_grade=eng_grade,
        eng_penalty=eng_penalty,
        results = rows
    )