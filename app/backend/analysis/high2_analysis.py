import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
from app.backend.analysis.RankAnalysisFunc import clearRanks, getRate
import app.backend.analysis.getData as getData
from scipy import stats # 통계 분석용
import matplotlib.pyplot as plt
import io
import base64
from scipy.stats import norm
from matplotlib import font_manager, rc
import platform

# 한글 폰트 설정
if platform.system() == 'Windows':
    # 윈도우의 경우 맑은 고딕 사용
    font_path = "C:/Windows/Fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)
else:
    # Mac이나 리눅스(Docker) 환경일 경우 (필요 시)
    rc('font', family='AppleGothic')

# 마이너스 기호 깨짐 방지
matplotlib.rcParams['axes.unicode_minus'] = False

def analyze_student_volatility(student_ranks):
    """성적 변동성 분석: 표준편차를 통해 성적의 안정성을 평가"""

    ranks = np.array(student_ranks)
    ranks = ranks[ranks > 0]
    if len(ranks) < 2: return "데이터 부족"
    
    std_dev = np.std(ranks)
    if std_dev < 0.5:
        return "매우 안정적"
    elif std_dev < 1.0:
        return "보통"
    else:
        return "변동성 높음 (취약 과목 점검 필요)"

def get_percentile_rank(student_avg, population_data):
    """
    합격자 집단 내 백분위 계산
    student_avg: 학생 평균 등급
    population_data: 비교 대상(합격자들)의 평균 등급 배열
    """
    # 등급은 낮을수록 좋으므로 'weak' 옵션 사용
    percentile = stats.percentileofscore(population_data, student_avg, kind='weak')
    return 100 - percentile # 상위 %로 변환

def get_weighted_total_rank(df):
    """
    학년별 가중치가 반영된 최종 수시 등급 계산
    (예: 1학년 20%, 2학년 30%, 3학년 50%)
    """
    grades_mean = {}
    for g in [1, 2, 3]:
        g_data = df[df['grade'] == g]['rank'].replace('A', 1).replace('B', 2).to_numpy()
        grades_mean[g] = np.mean(g_data) if len(g_data) > 0 else np.nan
    
    # 가중 합산 (데이터가 없는 학년 예외처리 필요)
    weighted_rank = (grades_mean.get(1, 0) * 0.2) + \
                    (grades_mean.get(2, 0) * 0.3) + \
                    (grades_mean.get(3, 0) * 0.5)
    return weighted_rank

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


def whereCanIGO(student, school, major):
    """학생이 지원 가능한 대학 리스트 반환"""
    getData.susicut_df['total'] = getData.susicut_df['교과 50%']*0.2\
                                 + getData.susicut_df['교과 70%']*0.3\
                                 + getData.susicut_df['학종 50%']*0.2\
                                + getData.susicut_df['학종 70%']*0.3
    possible_schools = []
    student_total_rank = getRankWithSubject(student.grades, 'total')*getRate(2,2,3,2, 'total')
    for i in range(len(getData.susicut_df.loc.to_numpy())):
        if getData.susicut_df.iloc[i]['total'] >= student_total_rank:
            possible_schools.append(getData.susicut_df.iloc[i]['학교'])
    return possible_schools


def calculate_pass_probability(student_rank, cut_50, cut_70):
    """
    합격 확률 계산 함수
    student_rank: 학생의 가중 평균 등급
    cut_50: 해당 학과 합격자 50% 컷 (평균)
    cut_70: 해당 학과 합격자 70% 컷
    """
    # 1. 평균 설정
    mu = cut_50
    
    # 2. 표준편차(sigma) 역산 
    # 등급 데이터이므로 (70%컷 - 50%컷)은 양수여야 함
    diff = cut_70 - cut_50
    if diff <= 0: # 데이터 오류 또는 극도로 촘촘한 분포인 경우 예외처리
        sigma = 0.1
    else:
        sigma = diff / 0.524 

    # 3. 누적분포함수(CDF)를 이용한 확률 계산
    # 등급은 숫자가 작을수록 우수하므로, student_rank가 mu보다 작을 때 확률이 높게 나옴
    # norm.cdf는 특정 값 이하일 확률을 구함
    z_score = (student_rank - mu) / sigma
    prob = 1 - norm.cdf(z_score)
    
    return round(prob * 100, 2)


def plot_pass_simulation(student_rank, cut_50, cut_70):
    """50%, 70% 컷 기반 합격 확률 시뮬레이션 그래프 생성"""
    mu = cut_50
    sigma = (cut_70 - cut_50) / 0.524
    
    x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
    y = norm.pdf(x, mu, sigma)
    
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, label='Acceptance Distribution', color='black')
    plt.fill_between(x, y, where=(x >= student_rank), color='green', alpha=0.3, label='Potential Pass Area')
    
    plt.axvline(student_rank, color='red', linestyle='--', label=f'My Rank ({student_rank})')
    plt.axvline(cut_50, color='blue', label='50% Cut (Avg)')
    
    plt.title("University Admission Probability Simulation")
    plt.xlabel("Grade (Rank)")
    plt.ylabel("Density")
    plt.gca().invert_xaxis() # 등급이 낮을수록 우측(높음)에 위치하도록 반전
    plt.legend()



def get_plot_base64():
    """그래프를 시각화하여 base64 문자열로 변환 (HTML 전송용)"""
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

def plot_all_subjects_trend(student):
    """
    국/수/영/과/기타/전체 성적의 학기별 변화를 하나의 그래프로 시각화
    """
    # 1. 분석할 과목군 정의
    subjects = ["국어", "수학", "영어", "탐구"]
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'] # 과목별 색상
    
    plt.figure(figsize=(12, 7))
    df = student.grades.copy()
    
    # 학기 타임라인 생성 (1-1: 1, 1-2: 2, 2-1: 3, 2-2: 4)
    df['timeline'] = (df['grade'] - 1) * 2 + df['semester']
    timelines = sorted(df['timeline'].unique())
    labels = [f"{((t-1)//2)+1}-{(t-1)%2+1}" for t in timelines] # 1-1, 1-2 등 라벨

    for idx, sub in enumerate(subjects):
        # 과목별 데이터 필터링 (기존 getRankWithSubject 로직 응용)
        if sub == "국어":
            sub_df = df[df['subject'].str.contains('국어', na=False)]
        elif sub == "수학":
            math_k = ['수학', '미적분', '확률', '통계', '확률과 통계', '기하']
            sub_df = df[df['subject'].str.contains('|'.join(math_k), na=False)]
        elif sub == "영어":
            sub_df = df[df['subject'].str.contains('영어', na=False)]
        elif sub == "탐구":
            sci_k = ['과학', '물리', '화학', '생명', '지구']
            sub_df = df[df['subject'].str.contains('|'.join(sci_k), na=False)]

        # 학기별 평균 계산
        means = []
        for t in timelines:
            # 해당 학기의 등급 추출 및 수치화
            ranks = sub_df[sub_df['timeline'] == t]['rank'].to_numpy()
            clean_ranks = clearRanks(ranks)
            valid_ranks = [r for r in clean_ranks if r > 0]
            means.append(np.mean(valid_ranks) if valid_ranks else np.nan)

        # 그래프 그리기 (total은 굵게 표시)
        linewidth = 4 if sub == "total" else 2
        alpha = 1.0 if sub == "total" else 0.7
        plt.plot(timelines, means, marker='o', label=sub, color=colors[idx], linewidth=linewidth, alpha=alpha)

    # 그래프 스타일 설정
    plt.title(f"{student.name} 학생 전과목 성적 추세 분석", fontsize=15, pad=20)
    plt.xlabel("학년-학기", fontsize=12)
    plt.ylabel("등급 (Rank)", fontsize=12)
    plt.xticks(timelines, labels)
    plt.ylim(9, 1) # 등급은 낮을수록 좋으므로 역전
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    
    return get_plot_base64()

def analyzing(student, school, major, jungsi_scores):
    """
    수시/정시 통합 분석 및 다중 그래프 생성 함수
    """
    # 0. 대학 데이터 기반 설정 (CSV 데이터 활용)
    # getData.susicut_df에서 학교 정보를 찾아 50%, 70% 컷 산출
    school_row = getData.susicut_df[getData.susicut_df['학교'] == school]
    
    if not school_row.empty:
        # 교과와 학종 컷의 평균을 분석 기준으로 설정
        target_cut_50 = (school_row['교과 50%'].values[0] + school_row['학종 50%'].values[0]) / 2
        target_cut_70 = (school_row['교과 70%'].values[0] + school_row['학종 70%'].values[0]) / 2
    else:
        # 데이터가 없을 경우 기본값 (사용자 알림용)
        target_cut_50, target_cut_70 = 2.0, 3.0

    # 1. 수시 성적 분석
    current_ranks = getRankWithSubject(student.grades, 'total')
    avg_susi_rank = np.mean(current_ranks) if len(current_ranks) > 0 else 0
    volatility = analyze_student_volatility(current_ranks)
    
    # 2. 정시 성적 분석 (전달받은 scores 활용)
    # scores = {'kor': 3, 'math': 2, 'eng': 2, 'inq': 3.5} 형태
    jungsi_values = [v for v in jungsi_scores.values() if v > 0]
    avg_jungsi_rank = np.mean(jungsi_values) if jungsi_values else 0
    
    # 3. 그래프 1: 합격 확률 시뮬레이션 생성
    plt.clf()  # 이전 그래프 잔상 제거
    plot_pass_simulation(avg_susi_rank, target_cut_50, target_cut_70)
    pass_graph_base64 = get_plot_base64()  # 첫 번째 버퍼 작업 완료
    
    # 4. 그래프 2: 전과목 성적 추세 생성
    plt.clf()  # 캔버스 초기화
    trend_graph_base64 = plot_all_subjects_trend(student) # 내부에서 get_plot_base64 호출
    
    # 5. 수시 vs 정시 전략 피드백
    diff = avg_jungsi_rank - avg_susi_rank
    if avg_jungsi_rank == 0:
        strategy = "정시 데이터가 부족하여 수시 위주로 분석되었습니다."
    elif diff > 0.5:
        strategy = f"내신({avg_susi_rank:.2f})이 정시({avg_jungsi_rank:.2f})보다 우수하여 수시 집중 전략이 필요합니다."
    elif diff < -0.5:
        strategy = f"정시({avg_jungsi_rank:.2f}) 경쟁력이 내신보다 높습니다. 수시는 상향 지원을 추천합니다."
    else:
        strategy = "수시와 정시 성적이 균형적입니다. 최저학력기준 충족 여부가 관건입니다."

    # 6. 최종 결과 딕셔너리 구성
    analysis_result = {
        "student_info": {
            "name": student.name,
            "school": student.school_name,
            "major": major
        },
        "score_analysis": {
            "average_rank": round(avg_susi_rank, 2),
            "jungsi_avg": round(avg_jungsi_rank, 2),
            "volatility": volatility,
            "pass_probability": calculate_pass_probability(avg_susi_rank, target_cut_50, target_cut_70)
        },
        "visual_data": {
            "pass_graph": pass_graph_base64,    # 첫 번째 그래프 데이터
            "trend_graph": trend_graph_base64  # 두 번째 그래프 데이터
        },
        "feedback": strategy
    }
    
    return analysis_result
