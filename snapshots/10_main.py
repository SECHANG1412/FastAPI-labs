from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr # EmailStr 타입을 사용하기 위해 가져옵니다.
from typing import List, Optional        # List 타입을 사용하기 위해 가져옵니다.


app = FastAPI()


##########################################################################################

# --- Pydantic 모델 정의 ---

# 사용자 생성을 위한 입력 모델 (비밀번호 포함)
class UserIn(BaseModel):
    username: str
    password: str       # 입력 시에는 비밀번호가 필요
    email: EmailStr     # Pydantic의 EmailStr 타입으로 이메일 형식 검증
    full_name: Optional[str] = None

# 사용자 정보를 외부에 보여주기 위한 출력 모델 (비밀번호 제외)
class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

# 간단한 아이템 모델 (내부 데이터 표현용) 
class ItemInternal(BaseModel):
    name: str
    price: float
    owner_id: int     # 내부적으로만 사용할 소유자 ID
    secret_code: str  # 외부에 노출하고 싶지 않은 비밀 코드

# 아이템 정보를 외부에 보여주기 위한 출력 모델 (내부 정보 제외)
class ItemPublic(BaseModel):
    name: str
    price: float

##########################################################################################

# --- 가상 데이터베이스 ---
# 실제로는 DB를 사용하겠지만, 여기서는 간단한 dict와 list 사용
fake_users_db = {}  # username: UserIn 모델 객체 저장
fake_items_db = {
    1: ItemInternal(name="keyboard", price=75.0, owner_id=1, secret_code="abc"),
    2: ItemInternal(name="Mouse", price=25.5, owner_id=1, secret_code="def"),
    3: ItemInternal(name="Monitor", price=300.0, owner_id=2, secret_code="ghi")
}

##########################################################################################

# --- API 엔드포인트 정의 ---

# 1. 기본 JSON 응답 (복습) - 딕셔너리 반환
@app.get("/ping")
async def ping():
    return {"message": "pong"}  # 딕셔너리를 반환하면 자동으로 JSON 응답이 됩니다.


# 2. 사용자 생성 - 입력 모델(UserIn)과 응답 모델(UserOut) 사용
@app.post("/users/", response_model=UserOut, status_code=201)
async def create_user(user: UserIn): 
    # 입력은 UserIn 모델로 받음
    # user 객체에는 password 필드가 포함되어 있습니다.

    print(f"Creating user: {user.username}, Password: {user.password}")
    
    # 요청으로 받은 사용자 정보를 서버 메모리에 저장
    # DB에 username을 키로 해서 user 객체를 저장
    # 실제로는 비밀번호를 해싱하여 DB에 저장하는 등의 처리가 필요합니다.
    fake_users_db[user.username] = user

    # 함수는 UserIn 모델 객체(비밀번호 포함)를 반환하지만...
    # 'response_model=UserOut' 때문에 비밀번호는 최종 응답에서 자동으로 필터링됩니다.
    return user


# 3. 특정 사용자 정보 조회 - 응답 모델(UserOut) 사용
@app.get("/users/{username}", response_model=UserOut)
async def read_user(username: str):
    if username not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # DB에서 가져온 UserIn 객체 (비밀번호 포함)
    user_in_db = fake_users_db[username]

    # UserIn 객체를 반환해도 response_model=UserOut에 의해 필터링됨
    return user_in_db


# 4. 아이템 목록 조회 - 응답 모델을 리스트 형태로 사용
# List[ItemPublic] : ItemPublic 모델 객체들의 리스트 형태로 응답 스키마 정의
@app.get("/items/", response_model=List[ItemPublic])
async def read_items():

    # 실제 DB에서 가져온 ItemInternal 객체들의 리스트라고 가정
    internal_items_list = list(fake_items_db.values())

    # ItemInternal 객체 리스트를 반환하면, 각 객체가 ItemPublic 스키마에 맞춰 필터링됨
    return internal_items_list


# 5. 특정 아이템 조회 - 응답 모델(ItemPublic) 사용
@app.get("/items/{item_id}", response_model=ItemPublic)
async def read_single_item(item_id: int):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # DB에서 가져온 ItemInternal 객체 (secret_code 포함)
    internal_item = fake_items_db[item_id]

    # ItemInternal 객체를 반환해도 response_model=ItemPublic에 의해 필터링됨
    return internal_item