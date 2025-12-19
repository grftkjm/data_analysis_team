from flask import Blueprint, render_template, request, current_app
from app.backend.analysis import getData
from app.backend.analysis.getStuData import create_student_from_pdf
from app.backend.analysis.high3_analysis import analyzing
from app.backend.analysis import testData
n_result_bp = Blueprint("n_result", __name__)

@n_result_bp.route("/n_result", methods=["POST"])
def n_result():
    # ---- 입력값 ----
    eng_grade = int(request.form["eng_grade"])
    inq1_percent = int(request.form["inq1_percent"])
    inq2_percent = int(request.form["inq2_percent"])

    is_science = True  # 이후 계열 선택으로 확장 가능

    # ---- 지표 계산 ----
    inq_avg = round((inq1_percent + inq2_percent) / 2, 1)

    eng_penalty = 0
    if eng_grade >= 3:
        eng_penalty = (eng_grade - 2) * 2

    kd_score = inq_avg - eng_penalty

    recommends = []

    # ---- 강남대성 ----
    if kd_score >= 90:
        recommends.append({
            "academy": "강남대성",
            "type": "우선선발",
            "label": "매우 유력",
            "level": "best",
            "desc": f"탐구 평균 {inq_avg}로 매우 상위권입니다. 영어 감점({eng_penalty})을 감안해도 우선선발 가능성이 높아요."
        })
    else:
        recommends.append({
            "academy": "강남대성",
            "type": "일반선발",
            "label": "도전",
            "level": "mid",
            "desc": "탐구는 충분하지만 영어 감점으로 우선선발은 다소 불리합니다."
        })

    # ---- 시대인재 ----
    if inq_avg >= 88:
        recommends.append({
            "academy": "시대인재",
            "type": "선착전형",
            "label": "추천",
            "level": "good",
            "desc": "탐구 백분위 기반 선착 전형에서 안정적인 위치입니다."
        })

    # ---- 메디컬 ----
    if is_science and inq_avg >= 95:
        recommends.append({
            "academy": "메디컬 특화",
            "type": "의치한 집중반",
            "label": "강력 추천",
            "level": "best",
            "desc": "과탐 최상위 점수로 메디컬 특화반 지원이 매우 유리합니다."
        })

    summary = (
        f"영어 {eng_grade}등급으로 인한 감점 리스크는 존재하지만, "
        f"탐구 평균 {inq_avg}는 이를 충분히 상쇄할 수 있는 강점입니다. "
        f"탐구 중심 선발 구조의 재종반 전략이 매우 적합합니다."
    )

    return render_template(
        "n_result.html",
        recommends=recommends,
        summary=summary,
        inq_avg=inq_avg,
        eng_grade=eng_grade,
        eng_penalty=eng_penalty
    )