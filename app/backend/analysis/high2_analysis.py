import pandas as pd
from RankAnalysisFunc import clearRanks, getCumulativeRank, getRate
import getData


def getRankWithSubject(df , subject):
    """과목별로 성적 추출해서 배열로 반환"""

    if subject == "국어":
        return clearRanks(df.loc[(df['subject'].str.contains('국어', na=False)), 'rank'].to_numpy())
    elif subject == "수학":
        math_keywords = ['수학', '미적분', '확률', '통계', '확률과 통계', '기하']
        return clearRanks(df.loc[(df['subject'].str.contains('|'.join(math_keywords), na=False)), 'rank'].to_numpy())
    elif subject == "영어":
        return clearRanks(df.loc[(df['subject'].str.contains('영어', na=False)), 'rank'].to_numpy())
    elif subject == "과학":
        sci_keywords = ['과학', '물리', '화학', '생명', '지구']
        return clearRanks(df.loc[(df['subject'].str.contains('|'.join(sci_keywords), na=False)), 'rank'].to_numpy())
    elif subject == "기타":
        return clearRanks(df.loc[(~df['subject'].str.contains('국어', na=False)) &
                                    (~df['subject'].str.contains('수학', na=False)) &
                                    (~df['subject'].str.contains('영어', na=False)) &
                                    (~df['subject'].str.contains('|'.join(sci_keywords), na=False)) , 'rank'].to_numpy())
    elif subject == "total":
        return clearRanks(df['rank'].to_numpy())
def susicutToNp():
    """수시컷 데이터프레임을 넘파이 배열로 변환"""
    susicut_np = getData.susicut_df.loc[:, ['school_id', 'major_id', 'subject', 'rank']].to_numpy()
    return susicut_np

def whereCanIGO(student, school, major):
    """학생이 지원 가능한 대학 리스트 반환"""
    pass
    possible_schools = []
    student_total_rank = getRankWithSubject(student.grades, 'total')*getRate(2,2,3,2, 'total')
    for i in range(len(getData.susicut_df.loc.to_numpy())):
        getData.susicut_df[]
    for sch in school:
        for mj in major:
            if mj.school_id == sch.id:
                major_total_rank = getCumulativeRank(sch.id, mj.id, 'total')
                if student_total_rank <= major_total_rank:
                    possible_schools.append((sch.name, mj.name))
    return possible_schools

def analyzing(student, school, major, jungsi_scores):
    """고2 심층 분석"""


    print(student.name)
    print(student.school_name)
    print(student.grades)
    print(student.creative_activities)
    print(student.behavioral_characteristics)
    print(student.detailed_abilities)
    print(student.jungsi_grades)

    #수시성적이 낮음
    if getCumulativeRank(2, 2, 'total') < getRankWithSubject(student.grades, 'total'):
        print("수시성적이 낮아서")
    else :
        pass
    student.jungsi_grades
    return student


