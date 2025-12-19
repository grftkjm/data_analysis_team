from flask import Blueprint, render_template, request
from app.backend.analysis import getData
from app.backend.getStuData import create_student_from_pdf
from app.backend.analysis.high3_analysis import analyzing

high3_bp = Blueprint("high3", __name__)

# -----------------------------
# 고3 입력 페이지
# -----------------------------
@high3_bp.route('/high3')
def high3():
    return render_template(
        'high3/high3.html',
        schools=list(getData.school_major_map.keys()),
        major_map=getData.school_major_map
    )


# -----------------------------
# 고3 결과 페이지
# -----------------------------
@high3_bp.route('/high3_result', methods=['POST'])
def high3_result():
    school = request.form.get("school")
    major = request.form.get("major")

    try:
        # =============================
        # 1. 등급 입력
        # =============================
        grades = {
            "kor": int(request.form.get("kor_grade")),
            "math": int(request.form.get("math_grade")),
            "eng": int(request.form.get("eng_grade")),
            "inq1": int(request.form.get("inq1_grade")),
            "inq2": int(request.form.get("inq2_grade")),
        }

        # =============================
        # 2. 백분위 입력
        # =============================
        percents = {
            "kor": int(request.form.get("kor_percent")),
            "math": int(request.form.get("math_percent")),
            "eng": int(request.form.get("eng_percent")),
            "inq1": int(request.form.get("inq1_percent")),
            "inq2": int(request.form.get("inq2_percent")),
        }

    except (ValueError, TypeError):
        return "성적(등급/백분위)을 올바르게 입력해주세요.", 400

    # =============================
    # 3. 생기부 PDF 처리
    # =============================
    uploaded_file = request.files.get('pdf_file')
    if not uploaded_file:
        return "생기부 PDF가 업로드되지 않았습니다.", 400

    student = create_student_from_pdf(uploaded_file)
    susi_row = getData.hakjong_df[(getData.hakjong_df["university"] == school) & (getData.hakjong_df["major"] == major)]
    jungsi_row = getData.jungsi_df[(getData.jungsi_df["university"] == school) & (getData.jungsi_df["major"] == major)]
    result_data = analyzing(student=student, school=school, major=major, jungsi_scores=scores)
    return render_template('high3/high3_result.html', data=result_data)

    # =============================
    # 4. 대학 입결 데이터
    # =============================
    susi_row = getData.hakjong_df[
        (getData.hakjong_df["university"] == school) &
        (getData.hakjong_df["major"] == major)
    ]

    jungsi_row = getData.jungsi_df[
        (getData.jungsi_df["university"] == school) &
        (getData.jungsi_df["major"] == major)
    ]

    # =============================
    # 5. 분석 실행
    # =============================
    result_data = analyzing(
        student=student,
        school=school,
        major=major,
        grades=grades,
        percents=percents,
        susi_row=susi_row,
        jungsi_row=jungsi_row
    )

    return render_template(
        'high3/high3_result.html',
        result=result_data,
        school=school,
        major=major
    )
