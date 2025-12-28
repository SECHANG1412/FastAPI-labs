from fastapi import FastAPI  # 1. FastAPI 클래스를 가져옵니다.

app = FastAPI()              # 2. FastAPI 애플리케이션 인스턴스를 생성합니다.


@app.get("/")                           # 3. 경로 "/"에 대한 GET 요청을 처리하는 함수를 정의합니다.
async def read_root():                  # 4. 비동기 함수로 정의할 수 있습니다.(async def)
    return {"message": "Hello World"}   # 5. 딕셔너리를 반환하면 자동으로 JSON 응답이 됩니다.