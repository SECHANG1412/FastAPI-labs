# status 모듈 가져오기
from fastapi import FastAPI, status 
# fastapi.responses에서 다양한 응답 클래스들을 가져옵니다.(Starlette 기반)
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    JSONResponse,
)

app = FastAPI()


# --- 다양한 Response 클래스 사용 예제 ---

# 1. HTML 응답 반환하기
# /html 주소로 오면 웹페이지(HTML)로 돌려준다
@app.get("/html", response_class=HTMLResponse)  # response_class를 HTMLResponse로 지정
async def read_html():
    html_content = """
    <html>
        <head>
            <title>FastAPI HTML Response</title>
            <style>
                body { font-family: sans-serif; }
                h1 { color: green; }
            </style>
        </head>
        <body>
            <h1>Hello from FastAPI! 👋</h1>
            <p>This is an HTML response.</p>
        </body>
    </html>
    """
    # HTML 문자열을 직접 반환하면 response_class에 의해 HTMLResponse로 변환됨
    return html_content


# 2. PlainText 응답 반환하기
# /text 주소로 오면 꾸밈없는 글자만 보내줌
@app.get("/text")
async def read_text():
    return PlainTextResponse(content="This is a plain text response from FastAPI.", status_code=200)
    # PlainTextResponse 객체를 직접 생성하여 반환


# 3. Redirect 응답 반환하기
# /redirect/docs로 오면 자동으로 /docs로 이동
@app.get("/redirect/docs")
async def redirect_to_docs():
    return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    # /docs 경로로 리디렉션 (307 Temporary Redirect)

 
# 외부 사이트로 이동
@app.get("/redirect/external")
async def redirect_external():
    return RedirectResponse(url="<https://fastapi.tiangolo.com/>", status_code=status.HTTP_302_FOUND)
    # 외부 URL로 리디렉션 (302 Found - 임시 리디렉션의 일반적인 코드)


# 4. JSONResponse 명시적 사용 (기본 동작과 유사하지만, 직접 제어 가능)
@app.get("/json/custom", response_class=JSONResponse)
async def read_custom_json():
    return {"message": "This is a custom JSON response using response_class"}
    # 딕셔너리를 반환하면 response_class에 의해 JSONResponse로 변환됨


# 직접 JSONResponse 생성
@app.get("/json/created", status_code=status.HTTP_201_CREATED)
async def create_resource():
    # JSONResponse를 직접 반환하여 상태 코드 등을 명시적으로 제어
    # 상태 코드, 헤더, 쿠키 등 응답을 세밀하게 통제하고 싶을 때 사용
    return JSONResponse(
        content={"resource_id": 123, "status": "created"},
        status_code=status.HTTP_201_CREATED # 여기서 다시 지정할 수도 있음
    )


# 5. response_class와 Response 객체 직접 반환 혼용 시
# 기본은 PlainText
@app.get("/mixed-response", response_class=PlainTextResponse)
async def mixed_response(return_html: bool = False):
    if return_html:
        # HTMLResponse 객체를 직접 반환하면 response_class보다 우선함
        return HTMLResponse("<h1>This is HTML overriding PlainText</h1>")
    else: 
        # 문자열만 반환하면 response_class(PlainTextResponse)가 적용됨
        return "This is the default PlainText response."