from flask import Blueprint, render_template, jsonify
import requests

certificates_bp = Blueprint("certificates", __name__)




# -----------------------------
#     자격증 API 수집 페이지
# -----------------------------

@certificates_bp.route('/certificates')
def certificates():
    urls = [
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=290",
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=570",
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=569"
    ]

    cert_list = set()

    for url in urls:
        try:
            data = requests.get(url).json()
            items = data.get("dataSearch", {}).get("content", [])

            for item in items:
                q = item.get("qualifications", "")
                if q:
                    parts = q.replace("\n", ",").split(",")
                    for c in parts:
                        c = c.strip()
                        if len(c) > 1:
                            cert_list.add(c)

        except:
            continue

    # 정렬
    cert_list = sorted(list(cert_list))

    return jsonify({"status": "ok", "data": cert_list})
"""
@certificates_bp.route('/certificates')
def certificates():
    urls = [
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=290",
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=570",
        "https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey=1655dc06aef84ff0c1cc03b0153a1474&svcType=api&svcCode=MAJOR_VIEW&contentType=json&gubun=univ_list&univSe=univ&subject=100394&perPage=500&majorSeq=569"
    ]

    cert_list = set()

    for url in urls:
        try:
            data = requests.get(url).json()
            items = data.get("dataSearch", {}).get("content", [])

            for item in items:
                q = item.get("qualifications", "")
                if q:
                    parts = q.replace("\n", ",").split(",")
                    for c in parts:
                        c = c.strip()
                        if len(c) > 1:
                            cert_list.add(c)

        except:
            continue

    cert_list = sorted(list(cert_list))

    return render_template("/certificates.html", result={"status":"ok","data":cert_list})
"""