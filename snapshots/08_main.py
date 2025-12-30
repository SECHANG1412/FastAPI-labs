import time                                            # 요청 처리 시간 측정을 위해 time 모듈 가져오기
from fastapi import FastAPI, Request                   # Request 객체를 사용하기 위해 가져오기
from fastapi.middleware.cors import CORSMiddleware     # CORS 미들웨어 가져오기

app = FastAPI()

#################################################################################################################

# --- CORS 미들웨어 설정 ---
# 웹 브라우저에서 실행되는 프론트엔드 Javascript 코드로부터의 요청을 허용하기 위함

# 허용할 출처(origin) 목록 - 실제 환경에서는 '*' 대신 구체적인 도메인 명시 권장
origins = [
    "<http://localhost>",                    # 예: 로컬 개발 환경
    "<http://localhost:3000>",               # 예: React 개발 서버 포트
    "<http://localhost:8080>",               # 예: Vue 개발 서버 포트
    # "<https://your-frontend-domain.com>",  # 예: 실제 서비스 도메인 추가
]

# app.add_middleware를 사용하여 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # origins 목록에 있는 출처의 요청만 허용
    allow_cledentials=True,  # 요청 시 쿠키/인증 정보 포함 허용 여부
    allow_methods=["*"],     # 허용할 HTTP 메서드 (GET, POST, PUT 등 모두 허용)
    allow_headers=["*"],     # 허용할 HTTP 요청 헤더 (모든 헤더 허용) 
)

#################################################################################################################

# --- 커스텀 미들웨어 정의 ---
# 모든 HTTP 요청에 대해 처리 시간을 측정하고 응답 헤더에 추가하는 미들웨어

# HTTP 요청/응답 사이클에 적용될 미들웨어임을 명시
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # 1. 요청 처리 전 로직 (선택 사항)
    start_time = time.time()
    print(f"Request received: {request.method} {request.url.path}")

    # 2. 다음 미들웨어 또는 경로 작동 함수 호출 (필수!)
    # call_next 함수는 다음 처리 단계(다른 미들웨어 또는 실제 엔드포인트 함수)로 요청을 전달하고, 그 결과를 (Response 객체) 받아옵니다. 반드시 await 해주어야 합니다.
    response = await call_next(request)

    # 3. 응답 처리 후 로직 (선택 사항)
    process_time = time.time() - start_time

    # 응답 헤더에 'X-Process-Time'이라는 커스텀 헤더 추가
    # 소수점 4자리까지
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    print(f"Response sent. Process time: {process_time:.4f} sec")

    # 4. 최종 응답 반환 (필수!)
    return response

#################################################################################################################

# --- 간단한 API 엔드포인트 정의 ---

# 미들웨어가 이 함수 실행 전후로 작동합니다.
# CORS 설정에 따라 다른 출처의 프론트엔드에서 호출 가능합니다.
@app.get("/")
async def read_root():
    return {"message": "Hello World with Middleware and CORS!"}


# 간단한 health check 또는 테스트용 엔드포인트
# 역시 미들웨어외 CORS의 영향을 받습니다.
# 잠시 지연을 주어 처리 시간 헤더 확인 (예시)
@app.get("/ping")
async def ping():
    await asyncio.sleep(0.1)    # 비동기 sleep 사용 (asyncio import 필요)
    return {"message": "pong"}

# 비동기 sleep을 사용하기 위해 asyncio import
import asyncio