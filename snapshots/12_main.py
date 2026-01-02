from fastapi import FastAPI, status, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


# --- 가상 데이터베이스 ---
items_db = {
    1: {"name": "Laptop", "price": 1200.0}, 
    2: {"name": "keyboard", "price": 75.0}
}
item_next_id = 3


# --- Pydantic 모델 ---
# Item이라는 "데이터 설계도"
class Item(BaseModel):
    name: str
    price: float

#########################################################################################

# --- API 엔드포인트 정의 ---

# 1. 아이템 생성 API
# POST /items/
# status_code=201 -> 정상 생성 시 "Created" 상태 코드 반환
@app.post("/items/", status_code=status.HTTP_201_CREATED, response_model=Item)
async def create_item(item: Item):
    # item : 클라이언트가 보낸 JSON 데이터
    # FastAPI가 자동으로 Item 모델로 변환 + 검증해줌
    global item_next_id                                              # 함수 안에서 전역 변수(item_next_id)를 수정하기 위해 필요
    items_db[item_next_id] = item.model_dump()                       # item.model_dump() -> Pydantic 객체(Item)을 일반 딕셔너리로 변환
    created_item_info = {"id": item_next_id, **item.model_dump()}    # 새로 생성된 아이템 정보에 ID를 추가한 딕셔너리
    item_next_id += 1                                                # 다음 아이템을 위해 ID 증가
    print(f"아이템 생성됨: {created_item_info}")

    return created_item_info
    # 성공 시 자동으로 201 상태 코드와 함께 응답 반환
    # response_model=Item 이므로 name, price만 클라이언트에 노출됨
    # 실제 서비스에서는 DB에 저장된 결과를 반환하는것이 일반적                  


# 2. 아이템 삭제 API
# DELETE /items/{item_id}
# 성공 시 204 No content (응답 본문 없음)
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    # item_id : URL 경로에서 전달받은 정수 값

    # 해당 ID의 아이템이 존재하는 경우
    if item_id in items_db:                    
        print(f"아이템 삭제됨: ID={item_id}")    # 삭제 로그 출력
        del items_db[item_id]                  # 딕셔너리에서 해당 아이템 제거

        return None
        # 204 상태 코드는 "응답 본문이 없어야 함"
        # FastAPI는 return None + 204 설정 시 자동으로 빈 응답을 보냄
        # 또는 return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        # 해당 ID가 없을 경우 -> 클라이언트에게 404 에러 JSON 응답 반환
    

# 3. 아이템 수정 API
# PUT /items/{item_id}
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    # item_id : 수정할 아이템 ID
    # item : 새로 전달받은 아이템 데이터
    
    # 해당 ID가 없으면
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item not found"
        )
    
    # 기존 데이터와 새 데이터가 같은지 비교
    if items_db[item_id] == item.model_dump():  # 변경 사항이 전혀 없는 경우
        print(f"아이템 변경 없음: ID={item_id}")

        return HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
        # 304 Not Modified 반환
        # Response 객체를 직접 반환하면 response_model은 무시됨
    
    # 실제로 변경된 경우
    else:
        items_db[item_id] = item.model_dump()   
        # 기존 데이터를 새 데이터로 덮어씀

        print(f"아이템 업데이트됨: ID={item_id}, Data={items_db[item_id]}")

        return items_db[item_id]
        # 딕셔너리를 반환하면
        # FastAPI가 자동으로 JSON 변환 + response_model 적용
    

# 4. Response 객체 직접 반환 예시
# GET /legacy-data
@app.get("/legacy-data", response_model=Item)
async def get_legacy_data():

    legacy_content = "<legacy><name>Old Data</name><price>10.0</price></legacy>" 
    # 예전 시스템에서 내려오는 XML 데이터라고 가정

    # Response를 직접 반환하면:
    # ❌ response_model 무시
    # ❌ 자동 JSON 변환 없음
    # ❌ Pydantic 검증 없음
    # ❌ Swagger 문서와도 불일치 발생 가능
    
    return Response(
        content=legacy_content, 
        media_type="application/xml", 
        status_code=200
    )