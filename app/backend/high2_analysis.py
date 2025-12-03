import app.backend.getData as getData

def analyzing(student, school, major, jungsi_scores): # jungsi_scores 안써도 일단 받아둠
    
    susicut_df = getData.susicut_df
    
    # [수정 3] IndexError 해결 로직
    # 학교 이름으로 필터링한 데이터프레임 가져오기
    target_df = susicut_df[susicut_df["학교"] == school]
    
    if target_df.empty:
        print(f"오류: {school} 데이터를 찾을 수 없습니다.")
        return {"error": "학교 정보를 찾을 수 없습니다."}

    # DataFrame의 첫 번째 행(row)을 가져와서 numpy 배열로 변환
    # .iloc[0]을 써야 1차원 배열(리스트 형태)이 됩니다.
    target_row = target_df.iloc[0].to_numpy() 
    
    # 이제 target_row[1], target_row[2] 접근 가능
    # (주의: 데이터 파일의 컬럼 순서가 [학교명, 50컷, 70컷...] 순서라고 가정)
    try:
        cut_50 = float(target_row[1])
        cut_70 = float(target_row[2])
        basis = (cut_50 + cut_70) / 2
    except (ValueError, IndexError):
        basis = 3.0 # 데이터 오류 시 기본값 설정 등 안전장치
        print("컷트라인 계산 중 오류 발생, 기본값 사용")

    # [수정 4] .mean() 괄호 추가 및 데이터 없는 경우 처리
    if not student.grades.empty and 'grade' in student.grades.columns:
        currentAchieve = student.grades["grade"].mean() # 괄호 필수!
    else:
        currentAchieve = 9.0 # 성적 없음

    currentAble = False
    
    # 내신은 숫자가 작을수록 좋으므로 (1등급 > 9등급)
    # basis(평균컷)보다 내 점수가 작거나 같아야 합격 가능
    if currentAchieve <= basis:
        currentAble = True
    else:
        currentAble = False
    
    print(f"분석 결과: 학생({currentAchieve}) vs 컷({basis}) -> 가능? {currentAble}")

    result = {
        "studentName": student.name,
        "content" : student.creative_activities , 
        "schoolName": school,
        "majorName": major,
        "avgGrade": round(currentAchieve, 2),
        "cutLine": round(basis, 2),
        "isPossible": currentAble
    }
    
    return result