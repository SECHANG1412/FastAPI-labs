from fastapi import FastAPI, HTTPException, Request, status, Depends # Request, status 추가
from fastapi.responses import JSONResponse, PlainTextResponse        # 응답 객체 추가
from fastapi.exceptions import RequestValidationError                # 기본 핸들러 재정의 위해 추가
from pydantic import BaseModel, Field                                # 유효성 검사 예제 위해 추가


app = FastAPI()


# --- 가상 데이터 ---
items_db = {1: {"name": "keyboard"}, 2: {"name": "Mouse"}}


# --- 커스텀 예외 정의 ---
class UnicornException(Exception):
    def __init__(self, name: str, message: str = "A unicorn related error occurred"):
        self.name = name
        self.message = message


# --- 커스텀 예외 핸들러 등록 ---
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    # UnicornException이 발생하면 이 핸들러가 실행됨
    return JSONResponse(
        status_code=418,
        content={
            "error_type": "Unicorn Error",
            "failed_item_name": exc.name,
            "message": exc.message,
            "request_url": str(request.url) # 요청 URL 정보 추가
        },
    )



# --- 기본 RequestValidationError 핸들러 재정의 ---
# Pydantic 유효성 검사 실패 시 기본 422 응답 대신 커스텀 응답 반환
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # exc.errors()로 상세 오류 정보를 얻을 수 있음
    error_details = []
    for error in exc.errors():
        field = " -> ".join(map(str, error['loc'])) # 오류 발생 필드 위치
        message = error['msg']                      # 오류 메시지
        error_details.append(f"field '{field}':{message}")

    # 간단한 텍스트 응답 또는 커스텀 JSON 응답 반환 가능
    # return PlainTextResponse(f"Validation Error(s): {'; '.join(error_details)}", status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,    # 422 대신 400 사용
        content={
            "message": "Invalid input provided.",
            "details": exc.errors(),                # 원본 오류 상세 정보 포함
            # "simplified_details": error_details
        }
    )


# --- API 엔드포인트 정의 ---

# 1. HTTPException 사용 예제
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items_db:
        # 아이템 없으면 404 오류 발생시킴
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,              # 상태 코드 지정
            detail=f"Item with ID {item_id} not found.",        # 오류 메시지 지정
            headers={"X-Error-Source": "Read Item Endpoint"},   # 커스텀 헤더 (선택)
        )
    return items_db[item_id]


# 2. 커스텀 예외 발생 예제
@app.get("/unicorns/{name}")
async def generate_unicorn_error(name: str):
    if name == "sparkle":
        # 특정 조건에서 커스텀 예외 발생
        raise UnicornException(name=name, message="Sparkle caused a rainbow overload!") 
    elif name == "invalid":
        # ValueError 발생 시 기본 500 오류 발생 (핸들러 없으므로)
        # 또는 별도 핸들러 등록 가능
        raise ValueError("This is an unhandled ValueError")
    return {"unicorn_name": name, "status": "ok"}


# 3. 유효성 검사 오류 발생 예제 (RequestValidationError 재정의 테스트용)
class InputData(BaseModel):
    value: int = Field(gt=10) # value는 10보다 커야 함


@app.post("/validate")
async def validate_endpoint(data: InputData):
    # data.value <= 10 인 요청이 오면 RequestValidationError 발생 -> 커스텀 핸들러 실행됨
    return {"message": "Data is valid!", "received_value": data.value}