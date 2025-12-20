from flask import Blueprint, render_template, request, current_app
from app.backend.analysis import getData
from app.backend.analysis.getStuData import create_student_from_pdf
from app.backend.analysis.high3_analysis import analyzing
from app.backend.analysis import testData
import pandas as pd
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
    uploaded_file = request.files.get("pdf_file")

    # 정시 성적 (폼 입력값)
    jungsi_grades = {
        "kor": int(request.form.get("kor_grade")),
        "math": int(request.form.get("math_grade")),
        "eng": int(request.form.get("eng_grade")),
        "inq1": int(request.form.get("inq1_grade")),
        "inq2": int(request.form.get("inq2_grade")),
    }
    jungsi_scores = {
        "kor": int(request.form.get("kor_percent")),
        "math": int(request.form.get("math_percent")),
        "inq1": int(request.form.get("inq1_percent")),
        "inq2": int(request.form.get("inq2_percent")),
    }
    #Gemini api 리소스 방지.. testmode 정해놓기
    if current_app.config.get('testMode'):
        student = testData.MockStudent()
    else :
        student = create_student_from_pdf(uploaded_file)
        if student is None:
            return render_template('error.html',message = "생기부 분석에 실패했습니다. 파일 형식을 확인하거나 잠시 후 다시 시도해주세요.")
    student.jungsi_scores = jungsi_scores
    student.jungsi_scores['eng'] = jungsi_grades['eng']
    #대학 입결 데이터
    susi_df = getData.hakjong_df
    jungsi_df = getData.jungsi_df
    #분석 실행
    
    #n수 분석에 전달할 데이터
    forRetry = { 'eng_val' : jungsi_grades['eng'],
                'kor_val' : jungsi_grades['kor'],
                'math_val' : jungsi_grades['math'],
                'inq1_val' : jungsi_grades['inq1'],
                'inq2_val' : jungsi_grades['inq2'],
                'inq1_val_percent' : jungsi_scores['inq1'],
                'inq2_val_percent' : jungsi_scores['inq2'] }
    result_data = analyzing(
        student=student,
        school=school,
        major=major,
        susi_df=susi_df,
        jungsi_df=jungsi_df
    )
    return render_template(
        'high3/high3_result.html',
        result=result_data,
        school=school,
        major=major,
        forRetry = forRetry,
    )

