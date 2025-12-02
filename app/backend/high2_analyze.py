import os
import time
import json
import re
import pandas as pd
import numpy as np
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import app.backend.getData as getData
import tempfile

# ==========================================
# 1. 설정
# ==========================================
API_KEY =  os.getenv("AI_API_KEY") # 본인 키 사용
genai.configure(api_key=API_KEY, transport='rest')

MODEL_NAME = "gemini-2.5-flash" 

# ==========================================
# 2. Student 클래스 정의
# ==========================================
class Student:
    def __init__(self, json_data, scores=None):
        # 1. 기본 정보
        info = json_data.get("student_info", {})
        self.name = info.get("name", "미상")
        self.school_name = info.get("school_name", "미상")

        # 2. 성적 (내신)
        grades_list = json_data.get("grades", [])
        if grades_list:
            self.grades = pd.DataFrame(grades_list)
            if not self.grades.empty:
                # 숫자형으로 변환 가능한지 확인 및 변환 (문자열 '1' -> 숫자 1)
                if 'grade' in self.grades.columns:
                    self.grades['grade'] = pd.to_numeric(self.grades['grade'], errors='coerce')
                
                cols = ['grade', 'semester', 'subject', 'rank']
                existing_cols = [c for c in cols if c in self.grades.columns]
                self.grades = self.grades[existing_cols]
        else:
            self.grades = pd.DataFrame() 

        # 3. 창체
        creative_list = json_data.get("creative_activities", [])
        self.creative_activities = pd.DataFrame(creative_list)

        # 4. 세특
        detailed_list = json_data.get("detailed_abilities", [])
        self.detailed_abilities = pd.DataFrame(detailed_list)

        # 5. 행특
        behavior_list = json_data.get("behavioral_characteristics", [])
        self.behavioral_characteristics = pd.DataFrame(behavior_list)

        # 6. 모의고사/수능 점수 (입력받은 값)
        self.junsi_grade =  {
                "국어": 0,
                "수학": 0,
                "영어": 0,
                "한국사": 0,
                "탐구": 0
            }

    def __repr__(self):
        return f"<Student: {self.name} ({self.school_name})>"

# ==========================================
# 3. 데이터 정제 함수
# ==========================================
def clean_json_response(text):
    try:
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match: return match.group(1)
        match = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match: return match.group(1)
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1: return text[start:end+1]
        return text
    except:
        return text

# ==========================================
# 4. Gemini 처리 및 Student 객체 생성
# ==========================================
# [수정 1] scores=None 파라미터 추가 필수!
def create_student_from_pdf(file_storage, scores=None):
    
    original_filename = file_storage.filename
    print(f"\n▶ 분석 시작: {original_filename}")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        file_storage.save(temp_file.name)
        temp_path = temp_file.name

    try:
        print(f" -> Gemini 서버로 업로드 중... ({temp_path})")
        uploaded_file = genai.upload_file(path=temp_path, display_name=original_filename)
        
        while uploaded_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(1)
            uploaded_file = genai.get_file(uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            print(" -> [실패] Gemini 파일 처리 실패")
            return None

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="""
            너는 입시 데이터 전문가다. PDF에서 학생 정보를 추출하여 **순수한 JSON 형식**으로만 출력하라.
            
            [주의사항]
            1. 응답은 반드시 JSON 포맷이어야 한다.
            2. Markdown 코드 블록(```json)을 사용하지 마라.
            3. 주석(// 또는 #)을 절대 포함하지 마라.
            4. 리스트의 마지막 항목 뒤에 쉼표(,)를 붙이지 마라.
            5. 키(Key)와 문자열 값(Value)은 반드시 큰따옴표(")를 사용하라.

            [추출 형식]
            {
              "student_info": {"name": "이름", "school_name": "학교명"},
              "grades": [{"grade": 1, "semester": 1, "subject": "과목명", "rank": 1}, ...],
              "creative_activities": [{"grade": 1, "type": "자율/동아리/진로/봉사", "content": "내용"}, ...],
              "detailed_abilities": [{"grade": 1, "semester": 1, "subject": "과목명", "content": "세특내용"}, ...],
              "behavioral_characteristics": [{"grade": 1, "content": "행특내용"}, ...]
            }
            
            """
        )

        response = model.generate_content(
            [uploaded_file],
            generation_config={"response_mime_type": "application/json"}
        )

        cleaned_text = clean_json_response(response.text)
        json_data = json.loads(cleaned_text)

        # [수정 2] scores 전달
        student = Student(json_data, scores=scores)
        print(f" -> 생성 완료: {student.name}")
        
        return student

    except Exception as e:
        print(f" -> [에러 발생] {e}")
        return None

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ==========================================
# 5. 분석 함수 (IndexError 수정)
# ==========================================
def analyze(student, school, major, jungsi_scores=None): # jungsi_scores 안써도 일단 받아둠
    
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