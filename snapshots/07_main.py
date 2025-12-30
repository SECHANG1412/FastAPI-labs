from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional

app = FastAPI()

##############################################################################################################################################################################################

# --- 의존성 함수(Dependable) 정의 ---

# 1. 공통 쿼리 파라미터 처리를 위한 의존성 함수
async def common_parameters(
    q: Optional[str] = None,   # 검색 쿼리 (선택적)
    skip: int = 0,             # 건너뛸 항목 수 (기본값 0)
    limit: int = 100           # 가져올 최대 항목 수 (기본값 100)
):
    return {"q": q, "skip": skip, "limit": limit}   # 딕셔너리 형태로 파라미터들을 묶어서 반환



# 2. 간단한 API 키 확인을 위한 의존성 함수 (개념 예시)
# 실제로는 더 안전한 방식(예: 헤더 사용, 토큰 검증)을 사용해야 합니다!
async def verify_api_key(x_api_key: Optional[str] = None):

    # 이 예제에서는 간단히 'fakeapikey'와 일치하는지 확인
    if x_api_key != "fakeapikey":
        # 일치하지 않으면 403 Forbidden 오류 발생
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    # 유효하면 키 값을 반환 (또는 그냥 None을 반환해도 됨)    
    return x_api_key



# 3. 하위 의존성 예시: verify_api_key 의존성을 사용하는 또 다른 의존성
async def verify_admin_access(
    # verify_api_key의 반환값이 api_key 변수에 주입됩니다.
    api_key: str = Depends(verify_api_key)
):
    # 이 예제에서는 키가 유효하기만 하면 관리자 접근을 허용한다고 가정합니다.
    # 실제로는 사용자 역할 등을 확인하는 로직이 추가되어야 합니다.
    print(f"관리자 접근 확인됨 (API 키: {api_key})")

    # 관리자임을 나타내는 정보를 반환할 수 있습니다.
    return {"is_admin": True}

##############################################################################################################################################################################################

# --- API 엔드포인트 정의 (의존성 주입 사용) ---

@app.get("/items/")
async def read_items(
    commons: dict = Depends(common_parameters)  # common_parameters 함수의 반환값({q, skip, limit} 딕셔너리)이 commons 파라미터에 주입됩니다.
):
    print(f"요청 파라미터: {commons}")                                           # 이제 commons 딕셔너리를 사용하여 로직 처리
    items_data = [{"item_name": "Item 1"}, {"item_name": "Item 2"}]             # 가상 데이터
    return {"message": "Reading items", "params": commons, "data": items_data}  # 실제로는 commons['q'], commons['skip'], commons['limit'] 값을 사용하여 데이터베이스 쿼리 등을 수행할 수 있습니다.



@app.get("/users/")
async def read_users(
    commons: dict = Depends(common_parameters) # 같은 의존성 함수를 다른 엔드포인트에서도 재사용!
):
    print(f"요청 파라미터: {commons}")
    users_data = [{"user_name": "User 1"}, {"user_name": "User 2"}]             # 가상 데이터
    return {"message": "Reading users", "params": commons, "data": users_data}



# '/secure-data/' 경로는 API 키 검증이 필요하다고 가정
@app.get("/secure-data/")
async def read_secure_data(
    # verify_api_key 의존성을 주입받습니다.
    # 만약 verify_api_key에서 HTTPException이 발생하면 이 함수는 실행되지 않습니다.
    api_key: str = Depends(verify_api_key)
):
    print(f"보안 데이터 접근 허용됨 (API 키: {api_key})")
    return {"message": "This is secure data!", "requester_api_key": api_key}



# '/admin-only/' 경로는 관리자 접근 검증이 필요하다고 가정
@app.get("/admin-only/")
async def read_admin_data(
    # verify_admin_access 의존성을 주입받습니다.
    # 이 의존성은 내부적으로 verify_api_key 의존성을 사용합니다 (하위 의존성).
    admin_info: dict = Depends(verify_admin_access)
):
    print(f"관리자 데이터 접근 허용됨: {admin_info}")                   # admin_info에는 {"is_admin": True} 가 주입됩니다.
    return {"message": "Welcome, Admin!", "access_level": admin_info}