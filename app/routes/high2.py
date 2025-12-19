from flask import Blueprint, render_template, request, jsonify
from app.backend.analysis import getData
from app.backend.getStuData import create_student_from_pdf 
from app.backend.analysis.high2_analysis import analyzing

high2_bp = Blueprint("high2", __name__)

@high2_bp.route('/high2')
def high2():
    return render_template('high2//high2.html',
                           schools=list(getData.school_major_map.keys()),
                           major_map=getData.school_major_map)

@high2_bp.route('/high2_result', methods = ['POST'])
def high2_result():
    school = request.form.get("school")
    major = request.form.get("major")

    try:
        scores = {
            "kor": int(request.form.get("score_kor")),    # 국어
            "math": int(request.form.get("score_math")),  # 수학
            "eng": int(request.form.get("score_eng")),    # 영어
            #"hist": int(request.form.get("score_hist")),  # 한국사
            "inq": float(request.form.get("score_inq"))   # 탐구(실수형 가능)
        }
    except (ValueError, TypeError):
        return "숫자를 올바르게 입력해주세요.", 400
    

    uploaded_file = request.files['pdf_file']
    student = create_student_from_pdf(uploaded_file)
    susi_row = getData.hakjong_df[(getData.hakjong_df["university"] == school) & (getData.hakjong_df["major"] == major)]
    jungsi_row = getData.jungsi_df[(getData.jungsi_df["university"] == school) & (getData.jungsi_df["major"] == major)]
    result_data = analyzing(student=student, school=school, major=major, jungsi_scores=scores)
    return render_template('high2/high2_result.html', result=result_data)
