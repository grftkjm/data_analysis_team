import pandas as pd

# =========================================================
# 1. Student 클래스 정의 (데이터 담을 그릇)
# =========================================================
class Student:
    def __init__(self):
        self.info = pd.DataFrame()
        self.creative_activities = pd.DataFrame()
        self.detailed_abilities = pd.DataFrame()
        self.behavioral_characteristics = pd.DataFrame()

# =========================================================
# 2. 정규식 없는 안전한 파서 함수 (오류 원인 제거됨)
# =========================================================
def parse_without_regex(text):
    
    # --- [내부함수] 아주 단순한 청소기 ---
    def simple_clean(line):
        # 1. 태그 제거 로직
        # 정규식(re) 대신 단순 문자열 찾기로 처리하여 오류 방지
        if "":
            end_idx = line.find("]")
            if end_idx != -1:
                line = line[end_idx+1:]
        
        # 2. 페이지 정보나 정부24 같은 헤더 제거
        if "--- Page" in line or "정부24" in line or "본 " in line:
            return "" # 그냥 내용을 비워버림
            
        return line.strip()

    # --- 메인 로직 시작 ---
    lines = text.split('\n')
    
    # 데이터를 담을 바구니들
    buffers = {'info': [], 'creative': [], 'seteuk': [], 'behavior': []}
    current_state = 'info' # 시작은 학생정보로 가정

    for line in lines:
        # 1. 한 줄 청소
        clean_line = simple_clean(line)
        if not clean_line: continue # 빈 줄이면 건너뜀

        # 2. 어디 구역인지 감지
        # 글자가 깨져도(띄어쓰기 등) 핵심 단어만 있으면 찾아냄
        
        # [창의적 체험활동] -> "창" 과 "체험" 이 있으면 진입
        if "창" in clean_line and "체험" in clean_line:
            current_state = 'creative'
            continue
            
        # [교과학습발달상황] -> "교과" 와 "학습" 이 있으면 -> 성적표니까 무시 모드
        elif "교과" in clean_line and "학습" in clean_line:
            current_state = 'skipping' # 성적표 건너뛰기
            continue
            
        # [세부능력및특기사항] -> "세부" 와 "능력" 이 있으면 -> 세특 모드
        elif "세부" in clean_line and "능력" in clean_line:
            current_state = 'seteuk'
            continue
            
        # [행동특성및종합의견] -> "행동" 과 "특성" 이 있으면 -> 행발 모드
        elif "행동" in clean_line and "특성" in clean_line:
            current_state = 'behavior'
            continue

        # 3. 상태에 따라 데이터 담기
        if current_state == 'info':
            buffers['info'].append(clean_line)
            
        elif current_state == 'creative':
            # 헤더 같은 내용("영역", "특기사항")은 빼고 담기
            if "영역" not in clean_line and "특기사항" not in clean_line:
                buffers['creative'].append(clean_line)
                
        elif current_state == 'seteuk':
            buffers['seteuk'].append(clean_line)
            
        elif current_state == 'behavior':
            buffers['behavior'].append(clean_line)
            
        elif current_state == 'skipping':
            pass # 성적표 점수들은 저장 안 함

    # =========================================================
    # 3. 데이터프레임 변환
    # =========================================================
    
    student = Student()
    
    # (1) 정보
    student.info = pd.DataFrame({'Raw_Info': [" ".join(buffers['info'])]})
    
    # (2) 창체 (단순 키워드 분리)
    cre_data = []
    curr_area = "활동"
    keywords = ["자율활동", "동아리", "진로활동", "봉사활동"]
    
    for line in buffers['creative']:
        # 줄 맨 앞에 키워드가 있거나 앞부분에 포함되어 있으면 영역 갱신
        for kw in keywords:
            if line.startswith(kw) or (kw in line[:10]):
                curr_area = kw
                line = line.replace(kw, "").strip() # 키워드 글자는 제거
                break
        cre_data.append({'Area': curr_area, 'Content': line})
        
    student.creative_activities = pd.DataFrame(cre_data)
    
    # (3) 세특 (콜론 ':' 기준으로 과목 분리)
    set_data = []
    curr_subj = "과목미상"
    curr_text = []
    
    for line in buffers['seteuk']:
        # "국어 :" 처럼 콜론이 있고 앞부분이 짧으면 과목명으로 간주
        if ":" in line and len(line.split(":")[0]) < 20:
            parts = line.split(":", 1)
            # 이전에 모아둔 내용이 있으면 저장
            if curr_text:
                set_data.append({'Subject': curr_subj, 'Content': " ".join(curr_text)})
            
            curr_subj = parts[0].strip()
            content = parts[1].strip()
            curr_text = [content] if content else []
        else:
            # 내용 이어 붙이기 (성적표 찌꺼기인 '원점수', '석차' 등은 제외)
            if "원점수" not in line and "석차" not in line:
                curr_text.append(line)
                
    # 마지막 남은 과목 저장
    if curr_text:
        set_data.append({'Subject': curr_subj, 'Content': " ".join(curr_text)})
        
    student.detailed_abilities = pd.DataFrame(set_data)
    
    # (4) 행발
    student.behavioral_characteristics = pd.DataFrame({'Content': [" ".join(buffers['behavior'])]})

    return student

# =========================================================
# 실행 부분 (파일 경로만 본인 것에 맞게 수정하세요)
# =========================================================

# 주의: 윈도우 경로이므로 문자열 앞에 r을 붙여줍니다.
file_path = r"G:\내 드라이브\2025\2학기\통계적 분석\생기부_censored_txt\생기부_censored_txt\201611091_4학년_컴퓨터과학과_이동재_정시_censored.txt"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 파싱 실행
    student_obj = parse_without_regex(text)

    # 결과 출력
    print("\n=== [1] 세특 데이터 (상위 5줄) ===")
    print(student_obj.detailed_abilities.head(5))

    print("\n=== [2] 창체 데이터 (상위 5줄) ===")
    print(student_obj.creative_activities.head(5))

    print("\n=== [3] 행발 데이터 ===")
    print(student_obj.behavioral_characteristics)

except FileNotFoundError:
    print(f"파일을 찾을 수 없습니다: {file_path}")
    print("경로를 다시 확인해주세요.")
except Exception as e:
    print(f"오류 발생: {e}")