import pandas as pd
import ocr
import sorting
#Student 클래스 정의
class Student:
    def __init__(self, json_data, scores):
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
def getStudata(uploaded_file) :
    ocr_text = ocr.ocr(uploaded_file)
    result = sorting.parse_school_record(ocr_text, Student)
