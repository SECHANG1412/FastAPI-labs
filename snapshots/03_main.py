from fastapi import FastAPI

app = FastAPI()


# --- GET 요청 처리 ---

# 1. 루트 경로 ("/") GET 요청 처리
@app.get("/")
async def read_root():
    return {"message": "Hello World from Root Path!"}


# 2. "/items" 경로 GET 요청 처리
# 아이템 목록을 조회하는 API 예시
@app.get("/items")
async def read_items():
    sample_items = ["맥북 프로", "아이폰 15", "에어팟 맥스", "매직 키보드"] # 실제로는 데이터베이스에서 가져오겠지만, 여기서는 예시 리스트를 반환
    return {"items": sample_items}


# 3. "/info" 경로 GET 요청 처리 (단순 문자열 반환 예시)
@app.get("/info")
async def get_information():
    return "이것은 FastAPI 강의 예제 API의 정보입니다."


# --- POST 요청 처리 ---

# 4. "/items" 경로 POST 요청 처리
# 새로운 아이템을 생성하는 API 예시
@app.post("/items")
async def create_item():
    return {"message": "새로운 아이템이 성공적으로 생성되었습니다."}
    # 지금은 단순히 성공 메시지만 반환
    # 실제로는 요청 본문(Body)에서 데이터를 받아 처리해야 함


# 5. "/items/update-status" 경로 PUT 요청 처리
# 아이템 상태를 업데이트하는 API 예시
@app.put("/items/update-status")
async def update_item_status():
    return {"status": "아이템 상태가 업데이트되었습니다."}
    # 지금은 단순히 업데이트되었다는 상태만 반환
    # 실제로는 어떤 아이템을 어떻게 업데이트할지 정보가 필요함


# --- DELETE 요청 처리 ---

# 6. "/items/clear-all" 경로 DELETE 요청 처리
# 모든 아이템을 삭제하는 API 예시
@app.delete("/items/clear-all")
async def delete_all_items():
    return {"message": "모든 아이템이 삭제되었습니다."}
    # 지금은 단순히 삭제되었다는 메시지만 반환