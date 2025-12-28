from fastapi import FastAPI
from typing import Optional, List

app = FastAPI()


# --- 경로 매개변수 (Path Parameters) ---

# 1. 기본적인 경로 매개변수 사용
# /items/{item_id} 형태로 요청을 받습니다. {item_id} 부분이 경로 매개변수입니다.
@app.get("/items/{item_id}")
async def read_item(item_id):               # 데코레이터의 경로 매개변수 이름과 함수 인자 이름이 같아야 합니다.
    return {"item_id_received": item_id}



# 2. 타입 힌트를 사용한 경로 매개변수
# item_id가 정수(int) 타입이어야 함을 명시합니다.
@app.get("items/typed/{item_id}")
async def read_item_typed(item_id: int):                        # 타입 힌트: int
    return {"item_id": item_id, "type": str(type(item_id))}     # FastAPI가 자동으로 문자열 경로를 정수로 변환하고, 변환 불가능하면 오류를 반환합니다.



# 3. 경로 순서의 중요성 예시
# 고정 경로가 동적 경로보다 먼저 와야 합니다.
@app.get("/users/me")
async def read_current_user():
    return {"user_id": "현재 로그인한 사용자 (me)"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}




# --- 쿼리 매개변수 (Query Parameters) ---

# 가상의 아이템 데이터베이스 (간단한 리스트)
fake_items_db = [{"item_name": "맥북 프로"}, {"item_name": "아이폰 15"}, {"item_name": "에어팟 맥스"}]


# 4. 기본적인 쿼리 매개변수 사용 (기본값 설정으로 선택적 매개변수 만들기)
# /items-query/?skip=0&limit=10 형태로 요청을 받습니다.
@app.get("/items-query/")
async def read_items_with_query(skip: int = 0, limit: int = 10):    # skip, limit은 경로에 없으므로 쿼리 매개변수가 됩니다. 기본값을 설정했습니다.
    return {
        "query_params": {"skip": skip, "limit": limit},
        "items": fake_items_db[skip: skip + limit]
    }
    # 기본값이 있으므로 클라이언트가 skip이나 limit을 제공하지 않아도 오류가 발생하지 않습니다.



# 5. 선택적(Optional) 쿼리 매개변수
# q 라는 쿼리 매개변수를 받지만, 필수는 아닙니다.
@app.get("/items-optional/")
async def read_items_optional(q: Optional[str] = None):
    results = {"items": [{"item_id": "FOO"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})    # q 가 제공되었다면 (None이 아니라면) 결과에 q를 추가합니다.
    return results



# 6. 쿼리 매개변수 타입 변환 및 필수 매개변수
# price 쿼리 매개변수는 float 타입이어야 하고, is_offer는 boolean 타입이어야 합니다.
# description은 필수 쿼리 매개변수입니다. (기본값이 없으므로)
@app.get("/items-validation/")
async def read_items_with_validation(description: str, price: float, is_offer: Optional[bool] = None):
    # FastAPI가 자동으로 타입을 검증하고 변환해줍니다.
    # description이 제공되지 않거나 price가 float으로 변환될 수 없으면 오류가 발생합니다.
    item_info = {"description": description, "price": price}
    if is_offer is not None:
        item_info.update({"is_offer": is_offer})
    return item_info



# --- 경로 매개변수와 쿼리 매개변수 함께 사용 ---

# 7. 경로 매개변수와 쿼리 매개변수 동시 사용
# /users/{user_id}/order?status=pending 형태로 요청
@app.get("/users/{user_id}/orders")
async def read_user_orders(user_id: int, status: Optional[str] = None): # user_id는 경로 매개변수, status는 쿼리 매개변수
    result = {
        "user_id": user_id, 
        "orders": [
                {"order_id": 1, "item": "Laptop"}, 
                {"order_id": 2, "item": "Mouse"}
        ]
    }
    if status:
        result.update({"filter_status": status})    # 실제로는 status 값으로 주문 목록을 필터링하는 로직이 들어갑니다.
    return result

