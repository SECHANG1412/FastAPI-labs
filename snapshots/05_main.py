from fastapi import FastAPI     
from pydantic import BaseModel  # Pydantic의 BaseModel을 가져옵니다.
from typing import Optional



# --- Pydantic 모델 정의 ---
# BaseModel을 상속받아 데이터 모델 클래스를 만듭니다.
# 이 클래스는 요청 본문의 데이터 구조(스키마)를 정의합니다.
class Item(BaseModel):
    name: str                           # 필수 필드, 문자열 타입이어야 함
    description: Optional[str] = None   # 선택적 필드(기본값 None), 문자열 또는 None 이어야 함
    price: float                        # 필수 필드, 실수 타입이어야 함
    tax: Optional[float] = None         # 선택적 필드(기본값 None), 실수 또는 None 이어야 함




# --- FastAPI 애플리케이션 인스턴스 생성 ---
app = FastAPI()



# --- 요청 본문 처리 예제 ---

# 1. POST 요청으로 Item 데이터 생성
# 함수의 파라미터 'item'에 위에서 정의한 Item 모델 타입을 지정합니다.
@app.post("/items/")
async def create_item(item: Item):              # FastAPI는 요청 본문을 읽어 Item 모델로 변환/검증합니다.
    # 함수 내부에서는 item을 Pydantic 모델 객체(파이썬 객체)로 바로 사용할 수 있습니다.
    print(f"아이템 이름: {item.name}")
    print(f"아이템 설명: {item.description}")
    print(f"아이템 가격: {item.price}")
    print(f"아이템 세금: {item.tax}")

    # Pydantic 모델 객체를 그대로 반환하면 FastAPI가 자동으로 JSON으로 변환해줍니다.
    # 예를 들어, 데이터베이스에 저장 후 저장된 객체를 반환할 수 있습니다.
    item_dict = item.model_dump()

    # 만약 세금 정보가 있다면 가격에 세금을 더해봅시다.
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    # 처리된 결과를 담은 딕셔너리 반환
    return item_dict


# 2. PUT 요청으로 Item 데이터 업데이트 (경로 매개변수 + 요청 본문)
# item_id 경로 매개변수와 item 요청 본문을 함께 받습니다.
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):    # item_id는 경로에서, item은 본문에서 옵니다.
    # 실제로는 item_id로 데이터베이스에서 기존 아이템을 찾고, 
    # 요청 본문(item)의 내용으로 업데이트하는 로직이 들어갑니다.
    print(f"업데이트 할 아이템 ID: {item_id}")
    print(f"업데이트 내용: {item.model_dump()}")

    return {"item_id": item_id, "updated_item_data": item.model_dump()}


# 3. 요청 본문 + 경로 매개변수 + 쿼리 매개변수 혼합 사용
@app.put("/items-complex/{item_id}")
async def update_item_complex(
    item_id: int,               # 경로 매개변수
    item: Item,                 # 요청 본문
    q: Optional[str] = None     # 선택적 쿼리 매개변수
):
    result = {"item_id": item_id, **item.model_dump()}  # 경로 매개변수와 본문 내용을 합침

    # 쿼리 매개변수 q가 있다면 결과에 추가
    if q:
        result.update({"query_param_q": q})

    # 여기서 item_id로 DB에서 아이템 찾고, item 내용으로 업데이트하고, q를 참고하는 등 로직 수행
    print(f"아이템 ID: {item_id}")
    print(f"업데이트 내용: {item.model_dump()}")
    print(f"쿼리 파라미터 q: {q}")

    return result