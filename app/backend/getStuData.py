import os
import time
import json
import re
import pandas as pd
<<<<<<< HEAD
from google import genai
from google.genai import types
import tempfile

# 1. 클라이언트 설정 (새로운 SDK 방식)
# API 키는 보안을 위해 환경변수 사용을 권장하지만, 일단 기존 코드를 유지합니다.
API_KEY = "AIzaSyB5tYf8qa4_yPim42h-vcSklSHtV5w57QQ"
client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1alpha'})
=======
import google.generativeai as genai
import tempfile

#변수 설정
API_KEY =  os.getenv("AI_API_KEY") # 본인 키 사용
genai.configure(api_key="AIzaSyBAT1nIrO8gE-IGjjcCOLD5btDax5d1lNU", transport='rest')
MODEL_NAME = "gemini-2.5-flash" 
>>>>>>> 94b73ffc2d18ab57b629d3b30f2f35b1af141a1a

MODEL_NAME = "gemini-2.0-flash" 

# Student 클래스 정의
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
                if 'grade' in self.grades.columns:
                    self.grades['grade'] = pd.to_numeric(self.grades['grade'], errors='coerce')
                
                cols = ['grade', 'semester', 'subject', 'rank']
                existing_cols = [c for c in cols if c in self.grades.columns]
                self.grades = self.grades[existing_cols]
        else:
            self.grades = pd.DataFrame() 

        # 3. 창체
        self.creative_activities = pd.DataFrame(json_data.get("creative_activities", []))
        # 4. 세특
        self.detailed_abilities = pd.DataFrame(json_data.get("detailed_abilities", []))
        # 5. 행특
        self.behavioral_characteristics = pd.DataFrame(json_data.get("behavioral_characteristics", []))

        # 6. 모의고사/수능 점수
        self.jungsi_grade = scores if scores else {"국어": 0, "수학": 0, "영어": 0, "한국사": 0, "탐구": 0}

    def __repr__(self):
        return f"<Student: {self.name} ({self.school_name})>"

# 데이터 정제 함수
def clean_json_response(text):
    try:
        # JSON 블록만 추출하는 정규식
        match = re.search(r"(\{.*?\})", text, re.DOTALL)
        return match.group(1) if match else text
    except:
        return text

# Gemini 처리 및 Student 객체 생성
def create_student_from_pdf(file_storage, scores=None):
    original_filename = file_storage.filename
    print(f"\n▶ 분석 시작: {original_filename}")

    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        file_storage.save(temp_file.name)
        temp_path = temp_file.name

    try:
        print(f" -> Gemini 서버로 업로드 중...")
        # 새 SDK 방식의 파일 업로드 (client.files.upload)
        with open(temp_path, "rb") as f:
            uploaded_file = client.files.upload(file=f)
        
        # 파일 처리 상태 확인 루프
        while uploaded_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(1)
            uploaded_file = client.files.get(name=uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            print(" -> [실패] 파일 처리 실패")
            return None

        # 시스템 프롬프트 설정
        system_instruction = """
        너는 입시 데이터 전문가다. PDF에서 학생 정보를 추출하여 순수한 JSON 형식으로 출력하라.
        
        [추출 형식]
        {
          "student_info": {"name": "이름", "school_name": "학교명"},
          "grades": [{"grade": 1, "semester": 1, "subject": "과목명", "rank": 1}],
          "creative_activities": [{"grade": 1, "type": "자율/동아리/진로/봉사", "content": "내용"}],
          "detailed_abilities": [{"grade": 1, "semester": 1, "subject": "과목명", "content": "세특내용"}],
          "behavioral_characteristics": [{"grade": 1, "content": "행특내용"}]
        }
        """

        # 컨텐츠 생성 (client.models.generate_content)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded_file, "이 PDF 내용을 분석해서 JSON으로 변환해줘."],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )

        # JSON 파싱 및 객체 생성
        json_data = json.loads(response.text)
        student = Student(json_data, scores=scores)
        print(f" -> 분석 및 생성 완료: {student.name}")
        
        return student

    except Exception as e:
        print(f" -> [에러 발생] {e}")
        return None

    finally:
        # 파일 삭제 등 정리
        if os.path.exists(temp_path):
            os.remove(temp_path)