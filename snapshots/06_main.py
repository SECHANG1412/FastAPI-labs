from fastapi import FastAPI, HTTPException              # HTTPException 추가
from pydantic import BaseModel, Field, field_validator  # Field, field_validator 추가
from typing import Optional, List


# --- Pydantic 모델 정의 (고급 유효성 검사 추가) ---
class Item(BaseModel):
    # Field를 사용하여 추가 제약 조건 설정
    name: str = Field(  
        min_length=3,                                               # 최소 길이 3
        max_length=50,                                              # 최대 길이 500
        title="Item Name",                                          # 문서화를 위한 제목
        description="The name of the item (3 to 50 characters).",   # 문서화를 위한 설명
        examples=["Gaming Keyboard"]                                # 문서화를 위한 예시
    )
    description: Optional[str] = Field(
        default=None,    # 기본값 설정
        max_length=300,  # 최대 길이 300
        title="Item Description",
        description="Optional description of the item (max 300 characters)."
    )
    price: float = Field(
        gt=0,           # 0보다 커야 함 (greater than 0)
        le=100000.0,    # 100,000 보다 작거나 같아야 함 (less than or equal to 100,000)
        title="Price",
        description="The price of the item (must be positive and <= 100,000)."
    )
    tax: Optional[float] = Field(
        default=None,
        gt=0,           # 0보다 커야 함
        title="Tax",
        description="Optional tax amount (must be positive)."
    )
    tag: List[str] = Field(
        default=[],     # 기본값 빈 리스트
        min_length=1,   # 최소 1개의 태그 필요
        max_length=5,   # 최대 5개의 태그 가능
        title="Tags",
        description="List of tags for the item (1 to 5 tags)."
    )


    # --- 커스텀 유효성 검사기 ---
    # @field_validator를 사용하여 특정 필드에 대한 커스텀 검증 로직 추가 (Pydantic V2 방식)
    # 클래스 메서드로 정의해야 합니다.
    @field_validator('name')
    @classmethod
    def name_must_not_be_admin(cls, v: str):                        # 'v'는 검증할 필드의 값입니다.
        if "admin" in v.lower():
            raise ValueError("Item name cannot contain 'admin'")    # 유효성 검사 실패 시 ValueError 발생
        return v.title()
        # 유효성 검사 통과 시 값을 그대로 또는 수정하여 반환
        # 이름을 Title Case로 변환하여 반환
    

# --- FastAPI 애플리케이션 인스턴스 생성 ---
app = FastAPI()

# 임시 데이터 저장소 (간단한 딕셔너리 사용)
items_db = {}


# 성공 시 201 Created 상태 코드 반환
@app.post("/items/", status_code=201)
async def create_item(item: Item):
    # Pydantic 모델을 통과했다는 것은 데이터가 유효하다는 의미!
    item_id = len(items_db) + 1
    items_db[item_id] = item.model_dump()                               # Pydantic 모델을 dict로 변환하여 저장
    print(f"아이템 생성 완료: ID={item_id}, Data={items_db[item_id]}")
    return {"item_id": item_id, **items_db[item_id]}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")   # 아이템이 없으면 404 Not Found 오류 발생
    return {"item_id": item_id, **items_db[item_id]}