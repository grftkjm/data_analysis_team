import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
basedir = os.path.dirname(os.path.abspath(__file__))
studentInfo = pd.read_csv(os.path.join(basedir, "data\\student_info.csv"))
RanksDf = pd.read_csv(os.path.join(basedir, "data\\grades.csv"))

def clearRanks(ranks):
    """
    성적 배열을 수치화하는 함수
    - NaN → 0
    - A=1, B=2, C=3, D=4
    - 숫자 문자열 → int
    - 변환 불가 → 0
    """
    grade_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
    result = []

    for val in ranks:
        # NaN 처리
        if pd.isna(val):
            result.append(0)
            continue

        # 문자열 처리
        if isinstance(val, str):
            val = val.strip().upper()
            if val in grade_map:
                result.append(grade_map[val])
                continue
            try:
                result.append(int(val))
            except ValueError:
                result.append(0)
                continue

        # 숫자 처리
        try:
            result.append(int(val))
        except (TypeError, ValueError):
            result.append(0)

    return np.array(result)

def getRank(grade, semester, dataframe):
    """수시/정시 관계없어 성적 가져오는 함수"""
    ranks = dataframe.loc[(dataframe['grade'] == grade) & (dataframe['semester'] == semester), 'rank_grade'].to_numpy()
    for i in range(len(ranks)):
        if type(ranks[i]) == str:
            if ranks[i] == 'A':
                ranks[i] = 1
            elif ranks[i] == 'B':
                ranks[i] = 2
            elif ranks[i] == 'C':
                ranks[i] = 3
            elif ranks[i] == 'D':
                ranks[i] = 4
            elif ranks[i] == 'e' :
                ranks[i] = 5
            else : 
                try:
                    ranks[i] = int(ranks[i])
                except:
                    ranks[i] = 0
        if ranks[i] == np.nan:
            ranks[i] = 0
    return ranks

def getSusiRank(grade, semester, rankData, stuData, ismean=False):
    """수시 지원한 학생들의 과목별 성적 데이터를 배열로 가져오는 함수"""
    #수시 입학한 학생들의 아이디 가져오기
    susiIDs = stuData.loc[stuData['is_susi'] == '수시', 'student_id'].to_numpy()

    #과목별 키워드로 검색
    susiRanks = rankData.loc[(rankData['student_id'].isin(susiIDs)) & (rankData['grade'] == grade) & (rankData['semester'] == semester), 'rank_grade'].to_numpy()

    susiRanks_kor = rankData.loc[(rankData['subject'].str.contains('국어', na=False)) & (rankData['student_id'].isin(susiIDs)) & (rankData['grade'] == grade) & 
                                 (rankData['semester'] == semester), 'rank_grade'].to_numpy()
    
    math_keywords = ['수학', '미적분', '확률', '통계', '확률과 통계', '기하']
    susiRanks_math = rankData.loc[(rankData['subject'].str.contains('|'.join(math_keywords), na=False)) &
                                   (rankData['student_id'].isin(susiIDs)) & (rankData['grade'] == grade) & 
                                 (rankData['semester'] == semester), 'rank_grade'].to_numpy()
    

    susiRanks_eng = rankData.loc[(rankData['subject'].str.contains('영어', na=False)) & (rankData['student_id'].isin(susiIDs)) & (rankData['grade'] == grade) & 
                                 (rankData['semester'] == semester), 'rank_grade'].to_numpy()
    
    sci_keywords = ['과학', '물리', '화학', '생명', '지구']
    susiRanks_sci = rankData.loc[(rankData['subject'].str.contains('|'.join(sci_keywords), na=False)) & 
                                 (rankData['student_id'].isin(susiIDs)) & (rankData['grade'] == grade) & 
                                 (rankData['semester'] == semester), 'rank_grade'].to_numpy()
    
    susiRanks_remain = rankData.loc[(~rankData['subject'].str.contains('국어', na=False)) &
                                    (~rankData['subject'].str.contains('수학', na=False)) &
                                    (~rankData['subject'].str.contains('영어', na=False)) &
                                    (~rankData['subject'].str.contains('|'.join(sci_keywords), na=False)) &
                                (rankData['student_id'].isin(susiIDs)) & (rankData['grade'] == grade) & (rankData['semester'] == semester), 'rank_grade'].to_numpy()

    if not ismean:
        return {"kor" : clearRanks(susiRanks_kor),
                 "math" : clearRanks(susiRanks_math),
                 "eng" : clearRanks(susiRanks_eng),
                 "sci" : clearRanks(susiRanks_sci),
                 "remain" : clearRanks(susiRanks_remain),
                 "total" : clearRanks(susiRanks)
                }
    else :
        return {"kor" : np.mean(clearRanks(susiRanks_kor)),
                 "math" : np.mean(clearRanks(susiRanks_math)),
                 "eng" : np.mean(clearRanks(susiRanks_eng)),
                 "sci" : np.mean(clearRanks(susiRanks_sci)),
                 "remain" : np.mean(clearRanks(susiRanks_remain)),
                 "total" : np.mean(clearRanks(susiRanks))
                }
    
def getCumulativeRank(grade, semester, subject):
    """특정 과목에 대한 누적 성적 반환 함수"""
    ranks = []

    for g in range(1, grade + 1):
        semester_end = semester if g == grade else 2
        for s in range(1, semester_end + 1):
            data = getSusiRank(g, s, RanksDf, studentInfo)
            if subject in data:
                ranks.extend(data[subject])

    ranks = np.array(ranks)
    ranks = ranks[ranks > 0]

    return np.mean(ranks) if ranks.size > 0 else np.nan

def getRate(PreGrades, PreSemester, PosGrades, PosSemester, subject, show = False) :
    """학년/학기 간의 성적 상승 비율 연산을 쉽게!"""
    #바로 적용시키고 싶은 경우
    if not show:
        return (np.mean(getSusiRank(PosGrades, PosSemester, RanksDf, studentInfo)[subject]))/ \
            (np.mean(getSusiRank(PreGrades, PreSemester, RanksDf, studentInfo)[subject]))
    
    #상승 퍼센테이지를 보여주고 싶은 경우
    else :
        return (np.mean(getSusiRank(PreGrades, PreSemester, RanksDf, studentInfo)[subject]))/ \
            (np.mean(getSusiRank(PosGrades, PosSemester, RanksDf, studentInfo)[subject]))
    
def getDistance(PreGrades, PreSemester, PosGrades, PosSemester, subject) :
    """학년/학기 간의 성적 상승 차이 연산을 쉽게!"""
    return (np.mean(getSusiRank(PosGrades, PosSemester, RanksDf, studentInfo)[subject])) - \
        (np.mean(getSusiRank(PreGrades, PreSemester, RanksDf, studentInfo)[subject]))    

def CumulativeRankGraph(grade, semester, subject):
    """성적 누적 분포를 나타내는 그래프 그리기"""
    data = np.array(getSusiRank(grade, semester, RanksDf, studentInfo)[subject])
    data = data[data > 0]

    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot(111)

    freq, _, _ = ax.hist(data, bins=9, range=(1,10))

    ax.set_xlabel('성적(등급)')
    ax.set_ylabel('학생 수')
    ax.set_xticks(np.arange(1, 10))
    ax.set_ylim(0, freq.max() * 1.1)

    plt.show()

def susiAvgTrendGraph(start_grade, start_semester, end_grade, end_semester, subject):
    """수시 학생들의 평균 등급 변화 그래프 그리기"""

    periods = []
    means = []

    for i in range(start_grade, end_grade + 1):
        semester_start = start_semester if i == start_grade else 1
        semester_end = end_semester if i == end_grade else 2

        for k in range(semester_start, semester_end + 1):
            periods.append(f"{i}-{k}")

            ranks = getSusiRank(i, k, RanksDf, studentInfo)[subject]

            if len(ranks) == 0:
                means.append(None)
            else:
                means.append(np.mean(ranks))

    period = np.array(periods)

     # 그래프 그리기
    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot(111)

    
    ax.plot(period, means, marker='o')  # 꺾은선 그래프
    ax.set_xlabel('학년-학기')
    ax.set_ylabel('평균 등급')
    ax.set_title('수시 학생 평균 등급 변화')

    plt.show()


def getEachPersonRank(grade, semester, rankData, stuData, ismean=False):
    """각 과목별로 학생의 등급을 반환하는 함수"""
    #수시 입학한 학생들의 아이디 가져오기
    susiIDs = stuData.loc[stuData['is_susi'] == '수시', 'student_id'].to_numpy()

    dicOfRanks = {}
    for i in range(len(susiIDs)):
        eachRanks = rankData.loc[(rankData['student_id'] == susiIDs[i]) & 
                              (rankData['grade'] == grade) & 
                              (rankData['semester'] == semester), 'rank_grade'].to_numpy()
        clearRanks(eachRanks)
        if ismean:
            eachRanks = np.mean(eachRanks)
        dicOfRanks[i] = eachRanks

    return pd.DataFrame(dicOfRanks)


def get_lowest_susi_student_id(student_df, grade_df, score):
    """
    수시 전형 학생 중 평균 등급 수치가 가장 큰(성적이 가장 낮은) 학생의 ID 리턴
    """
    #수시(is_susi == '수시') 학생들만 필터링
    susi_students = student_df[student_df['is_susi'] == '수시']
    
    #성적 데이터 복사 및 전처리 (원본 데이터 보호)
    susi_grades = grade_df[grade_df['student_id'].isin(susi_students['student_id'])].copy()
    
    susi_grades['rank_grade'] = susi_grades['rank_grade'].replace({'A': 1, 'B': 2, 'C': 3})
    susi_grades['rank_grade'] = pd.to_numeric(susi_grades['rank_grade'], errors='coerce')
    
    # 학생별 평균 등급 계산 (nan 제외)
    avg_grades = susi_grades.dropna(subset=['rank_grade']).groupby('student_id')['rank_grade'].mean()
    
    #모든 데이터가 NaN이라 계산 결과가 없는 경우 예외 처리
    if avg_grades.empty:
        return None
    
    #평균 등급 수치가 가장 큰(성적이 제일 낮은) 학생의 ID 추출
    lowest_student_id = avg_grades.idxmax()
    
    return lowest_student_id

def get_susi_students_above_avg(student_df, grade_df, threshold):
    """
    수시 전형 학생 중
    평균 등급(rank_grade)이 threshold보다 큰 학생들의 student_id 리스트 반환
    """

    # 1. 수시 학생만 필터링
    susi_students = student_df[student_df['is_susi'] == '수시']

    # 2. 해당 학생들의 성적만 추출
    susi_grades = grade_df[
        grade_df['student_id'].isin(susi_students['student_id'])
    ].copy()

    # 3. 등급 문자 → 숫자 변환
    susi_grades['rank_grade'] = susi_grades['rank_grade'].replace({
        'A': 1,
        'B': 2,
        'C': 3
    })
    susi_grades['rank_grade'] = pd.to_numeric(
        susi_grades['rank_grade'], errors='coerce'
    )

    # 4. 학생별 평균 등급 계산 (NaN 제외)
    avg_grades = (
        susi_grades
        .dropna(subset=['rank_grade'])
        .groupby('student_id')['rank_grade']
        .mean()
    )

    # 5. 계산 결과가 없으면 빈 리스트 반환
    if avg_grades.empty:
        return []

    # 6. 기준값 초과 학생 필터링
    result_ids = avg_grades[avg_grades > threshold].index.tolist()

    return result_ids