from fastapi import FastAPI, Response, Cookie, status
from typing import Optional

app = FastAPI()

#######################################################################################################

# --- 헤더(Header) 관리 예제 ---

# 헤더란?
# 👉 서버가 보내는 편지의 “봉투 겉면 정보”
# 👉 브라우저, 서버, 보안, 버전 정보 등을 전달할 때 사용

@app.get("/headers/set-custom")
async def set_custom_header(response: Response):
    # response: FastAPI가 자동으로 넣어주는 응답 객체

    # response.header는 딕셔너리 형태 -> 여기에 값을 넣으면 응답 헤더에 추가됨
    response.headers["X-Custom-Header-1"] = "Hello from custom header!" # X-custom-Header-1 : 내가 만든 사용자 정의 헤더
    response.headers["X-Another-Header"] = "FastAPI is awesome"         # 또 다른 사용자 정의 헤더
    response.headers["Server"] = "My Custom FastAPI Server" 
    # 기존 헤더 덮어쓰기 또는 새 헤더 추가 
    # # Server 헤더는 "이 응답을 보낸 서버 정보"

    return {
        "message": "Check the response headers in your browser's developer tools!"
    }
    # 응답 본문(body)은 JSON 형태
    # 실제 핵심은 "헤더가 추가되었다"는 점


#######################################################################################################

# --- 쿠키(Cookie) 관리 예제 ---

# 쿠키란?
# 👉 브라우저가 기억하고 있는 작은 메모지
# 👉 로그인 상태, 세션 정보 등을 저장할 때 사용


@app.post("/cookies/set-simple")
async def set_simple_cookie(response: Response):
    # response 객체를 사용해 쿠키를 심을 준비

    # 간단한 쿠키 설정
    response.set_cookie(    
        key="simple_cookie",    # 쿠키 이름
        value="hello_fastapi"   # 쿠키 값
    )
    # 옵션이 없으므로:
    # 👉 브라우저를 닫으면 사라지는 “세션 쿠키”

    return {
        "message": "Simple cookie has been set. Close your browser and see if it persists!"
    }
    # 쿠기 설정 완료 안내 메시지


# 실무에서 쓰는 “옵션이 달린 쿠키” 예제
@app.post("/cookies/set-options")
async def set_cookie_with_options(response: Response):

    # 다양한 옵션과 함께 쿠키 설정
    response.set_cookie(
        key="user_session_id",      # 쿠키 이름 (보통 로그인 세션 ID)
        value="abc123xyz789",       # 쿠키 값 (실제로는 랜덤하고 안전한 값 사용)
        max_age=60 * 60 * 24 * 7,   # 쿠키 수명 (초 단위) -> 7일 동안 유지됨
        path="/",                   # 사이트 전체에서 이 쿠키 사용 가능
        # domain=".example.com",    # 쿠키가 유효한 도메인 (실제 서비스에서 필요할 때만 사용)
        secure=True,                # True 설정 시 HTTPS를 통해서만 쿠키 전송 -> 운영 환경에서는 거의 필수
        httponly=True,              # True 설정 시 JavaScript에서 쿠키 접근 불가 -> 해킹(XSS) 방어에 매우 중요
        samesite="lax"              # 다른 사이트 요청 시 쿠키 전송 규칙
        # lax : 대부분 안전한 기본값
        # strict: 가장 엄격
        # none: 완전 허용 (secure=True 필수)
    )
    return {
        "message": "Cookie 'user_session_id' set with options!"
    }
    # 보안 옵션이 적용된 쿠키 설정 완료 안내


# 브라우저가 보내온 쿠키 읽기
@app.get("/cookies/get")
async def get_cookie_value(
    user_session_id: Optional[str] = Cookie(default=None)
    # Cookie(...) :
    # 요청에 포함된 쿠키 중에서 "user_session_id" 값을 자동으로 꺼내줌
    # 쿠키가 없으면 None
):  
    # 쿠키가 존재하는 경우
    if user_session_id:
        print(f"Received user_session_id cookie: {user_session_id}")   # 서버 콘솔에 쿠키 값 출력
        return {"cookie_value": user_session_id}                       # 클라이언트에게 쿠키 값 반환
    
    # 쿠키가 없는 경우
    else:
        print("user_session_id cookie not found.")
        return {"message":"Cookie 'user_session_id' not found in request."}
    

    
# 성공 시 204 (No content) -> 응답 본문 없음
# 쿠키 삭제는 "같은 이름 + 같은 경로 + 같은 도메인"으로 해야 함
@app.get("/cookies/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_cookie(response: Response):

    print("Deleting user_session_id cookie.")

    response.delete_cookie(
        key="user_session_id", # 삭제할 쿠키 이름
        path="/",              # 쿠키를 만들 때 사용한 path
        domain=None            # domain을 설정했었다면 동일하게 지정
    )

    # 다른 방법:
    # response.set_cookie(key="user_session_id", value="", max_age=0)

    return None
    # 204 상태 코드는 본문을 포함하지 않음