import tkinter as tk
from tkinter import filedialog, scrolledtext
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import numpy as np
import tempfile
import pandas as pd
import re
from pathlib import Path

# EasyOCR Reader (한국어 + 영어)
reader = easyocr.Reader(['ko', 'en'])

def pdf_to_images(pdf_path):
    """PDF 페이지들을 이미지(PIL) 리스트로 변환"""
    doc = fitz.open(pdf_path)
    images = []

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(dpi=200)

        # PyMuPDF pixmap → PIL 이미지로 변환
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    return images


def ocr(file_storage):

    original_filename = file_storage.filename
    print(f"\n▶ 분석 시작: {original_filename}")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        file_storage.save(temp_file.name)
        temp_path = temp_file.name

    if not temp_path:
        return False

    try:
        pages = pdf_to_images(temp_file)

        final_text = ""

        for i, img in enumerate(pages):
            print(tk.END, f"\n--- {i+1}  페이지 OCR 중... ---\n")

            # EasyOCR 실행
            result = reader.readtext(np.array(img), detail=0)

            final_text += f"\n\n==== PAGE {i+1} ====\n"
            final_text += "\n".join(result)

        print("\n\n=== OCR 완료 ===\n")
        print(final_text)
        return final_text

    except Exception as e:
        print(f" -> 에러 발생 {e}")
        return None

def processing(text) :

    # === 2. 블록 분리 함수 ===
    def extract_block(pattern, text, flags=re.DOTALL):
        m = re.search(pattern, text, flags)
        return m.group(1).strip() if m else ""

    blocks = {
        "student": extract_block(r"인적.*?\n(.*?)\n창의적 체험활동상황", text),
        "창체": extract_block(r"창의적 체험활동상황(.*?)행동특성 및 종합의견", text),
        "행특": extract_block(r"행동특성 및 종합의견(.*?)세부능력", text),
        "세특": extract_block(r"세부능력 및 특기사항(.*?)봉 사 활 동 실 적", text),
    }

    # === 3. 6학기 성적 블록 추출 ===
    # 학기별 과목/점수가 나오는 구간 반복 추출
    semester_blocks = re.findall(r"\[([1-3])학년\]\s*?(1|2)학기(.*?)(?=\n\[|\Z)", text, re.DOTALL)
    semesters = []
    for year, sem, content in semester_blocks:
        semesters.append({"year": int(year), "semester": int(sem), "content": content.strip()})

    # === 4. 과목 성적 파싱 ===
    # "과목: 85/76.0(17.3) (359)" 또는 "과목 75/68.4(18.2)" 같은 패턴 탐지
    score_pattern = re.compile(
        r"(?P<subject>[가-힣A-Za-z\sⅠIVX]+?)[:：]?\s*?"
        r"(?P<score>\d{1,3})/(?P<avg>\d{1,3}\.?\d*)?\s*"
        r"(?:\((?P<std>[\d\.]+)\))?\s*"
        r"(?:[A-C])?(?P<grade>A|B|C)?",
    )

    records = []
    for s in semesters:
        for line in s["content"].split("\n"):
            line = line.strip()
            if "/" in line:
                m = score_pattern.finditer(line)
                for item in m:
                    d = item.groupdict()
                    records.append({
                        "학년": s["year"],
                        "학기": s["semester"],
                        "과목": d["subject"].strip(),
                        "원점수": int(d["score"]),
                        "과목평균": float(d["avg"]) if d["avg"] else None,
                        "표준편차": float(d["std"]) if d["std"] else None,
                        "성취도": d["grade"] if d["grade"] else d["grade"],
                    })

    def student_rows(block_text):
        fixed_rows = []
        for line in block_text.split("\n"):
            if "|" in line:
                cols = [c.strip() for c in line.split("|")]
                # 2열을 넘으면 1열 + (나머지 모두 합쳐서 2열)
                if len(cols) > 2:
                    fixed_rows.append([cols[0], " ".join(cols[1:])])
                # 1열만 나오면 빈칸 패딩
                elif len(cols) == 1:
                    fixed_rows.append([cols[0], ""])
                # 2열이면 그대로
                else:
                    fixed_rows.append(cols[:2])
        return fixed_rows

    df_scores = pd.DataFrame(records)


    # === 5. 학생 정보 인덱스 테이블 구성 ===
    df_student = pd.DataFrame(
        student_rows(blocks["student"]),
        columns=["항목","값"]
    )

    # === 6. 창체, 행특, 세특 라인 처리 ===
    df_creativeActivities = pd.DataFrame(
        student_rows(blocks["창체"]),
        #[x.split("|") for x in blocks["창체"].split("\n") if "|" in x],
        columns=["학년","영역","시간","특기사항"]
    )
    df_behaviorCharacteristics = pd.DataFrame(
        student_rows(blocks["행특"]),
        #[x.split("|") for x in blocks["행특"].split("\n") if "|" in x],
        columns=["학년","종합의견"]
    )
    df_detailedCharacteristics = pd.DataFrame(
        [[line] for line in blocks["세특"].split("\n") if line],
        columns=["세특"]
    )

    # === 7. 과목별 성적 분리 저장 (6개 CSV) ===
    subjects = df_scores["과목"].unique()
    subject_dfs = {}
    for i, sub in enumerate(subjects, start=1):
        subject_dfs[f"sub{i}"] = df_scores[df_scores["과목"] == sub].drop(columns=["과목"])

    # === 8. 총 10개 CSV 저장 ===
    outdir = Path("/mnt/data/student_csvs")
    outdir.mkdir(exist_ok=True)

    df_student.to_csv(outdir/"student_index.csv", index=False)
    df_creativeActivities.to_csv(outdir/"창의체험.csv", index=False)
    df_behaviorCharacteristics.to_csv(outdir/"행동특성.csv", index=False)
    df_detailedCharacteristics.to_csv(outdir/"세부능력특기.csv", index=False)

    # 과목별 6학기 성적 저장
    for name, sdf in subject_dfs.items():
        sdf.to_csv(outdir/f"{name}.csv", index=False)

    print("✅ 10개의 CSV 파일 생성 완료:", list(outdir.glob("*.csv")))

