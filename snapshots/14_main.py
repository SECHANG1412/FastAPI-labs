import os
import shutil
import aiofiles
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, status

# --- 필수 라이브러리 설치 알림 ---
# 이 코드를 실행하기 전에 반드시 'python-multipart' 와 'aiofiles' 를 설치해야 합니다!
# python-multipart : 파일 업로드(form-data)를 처리하기 위해 필수
# aiofiles         : 비동기 파일 저장을 위해 필요
# pip install python-multipart aiofiles

app = FastAPI()

# 업로드된 파일을 저장할 디렉토리
UPLOAD_DIR = "./uploads"                # 현재 서버를 실행한 위치 기준으로 uploads 폴더를 의미
os.makedirs(UPLOAD_DIR, exist_ok=True)  # uploads 폴더가 없으면 자동 생성, exist_ok=True : 이미 있어도 에러 나지 않음

########################################################################################################################

# --- 파일 업로드 엔드포인트 정의 ---

# 1. 작은 파일 업로드 (bytes 사용 - 메모리 주의)
@app.get("/files/upload-bytes/")
async def upload_small_file(
    file: bytes = File(..., description="Upload a small file as bytes") 
    # File(...) : 이 값이 "파일"이라는 메타 정보
    # bytes     : 파일 전체를 한 번에 메모리에 올림
    # file 변수에는 파일 전체 내용이 bytes 형태로 들어 있음
):
    file_size = len(file)   # bytes 길이를 이용해 파일 크기 계산

    print(f"Received small file (bytes), size: {file_size} bytes")

    # 1MB 초과 여부 확인
    # bytes 방식은 큰 파일에 부적합
    if file_size > 1024 * 1024:                             
        print("Warning: File size is large for 'bytes' handling.")

    # bytes 데이터를 직접 처리하거나 저장할 수 있음
    # ⚠️ 실무에서는 큰 파일에 이 방식 사용 ❌

    # 아래는 bytes 파일을 저장하는 예시 (주석 처리됨)
    # async with aiofiles.open(os.path.join(UPLOAD_DIR, "uploaded_bytes.bin"), 'wb') as out_file:
    #     await out_file.write(file)


    # 파일을 잘 받았다는 응답 반환
    return {
        "file_size": file_size, 
        "message": "File received as bytes"
    }
    


# 2. 단일 파일 업로드 (uploadFile 사용 - 권장 방식)
@app.post("/files/upload-single/")
async def upload_single_file(
    file: UploadFile = File(..., description="Upload a single file using UploadFile")
    # UploadFile :
    # 파일을 스트림 방식으로 조금씩 읽을 수 있음 -> 메모리 절약 + 대용량 파일 처리 가능
):
    print(f"Received file: {file.filename}")        # file.filename     : 업로드된 파일 이름
    print(f"Content type: {file.content_type}")     # file.content_type : 파일 MIME 타입 (image/png 등)

    # ⚠️ 아래 방식은 전체 파일을 메모리에 올리므로 큰 파일에 위험
    # contents = await file.read()
    # print(f"File content length: {len(contents)}")
 
    # 파일 이름 안전 처리
    safe_filename = os.path.basename(file.filename or "upload_file")
    # os.path.basename:
    # "../hack.txt" 같은 위험한 경로 제거
    # 실제 서비스에서는 UUID 등으로 이름 변경 권장

    destination = os.path.join(UPLOAD_DIR, safe_filename)
    # 저장할 최종 파일 경로 생성

    print(f"Saving file to: {destination}")


    try:
        async with aiofiles.open(destination, 'wb') as out_file: # aiofiles로 파일을 비동기 방식으로 열기
            while content := await file.read(1024 * 1024):       # 파일을 1MB씩 잘라서 읽고 쓰기
                await out_file.write(content)

    # 저장 중 오류 발생 시
    except Exception as e:  
        print(f"file saving error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Could not dave file: {e}"
        )
    
    # UploadFile은 자동으로 닫히지만 명시적으로 닫아주는 습관이 좋음
    finally:
        pass
    
    # 저장 결과 반환
    return {
        "filename": file.filename, 
        "content_type": file.content_type, 
        "save_path": destination
    }



# 3. 다중 파일 업로드
@app.post("/files/upload-multiple/")
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="Upload multiple files")
    # 여러 파일을 리스트 형태로 받음
):
    
    saved_files = []    # 처리 결과를 담을 리스트
    

    # 업로드된 파일 하나씩 처리
    for file in files:
        print(f"Procession file: {file.filename}")

        safe_filename = os.path.basename(file.filename or f"uploaded_file_{len(saved_files)}")
        destination = os.path.join(UPLOAD_DIR, safe_filename)

        try:
            async with aiofiles.open(destination, 'wb') as out_file:
                while content := await file.read(1024 * 1024):
                    await out_file.write(content)
            saved_files.append({
                "filename": file.filename, 
                "save_path": destination}
                )

        except Exception as e:
            print(f"Error saving {file.filename}: {e}")

            # 한 파일 실패해도 전체 업로드는 계속 진행
            saved_files.append({
                "filename": file.filename, 
                "error": str(e)}
            )

        # finally: await file.close()

    # 여러 파일 처리 결과 반환
    return {
        "message": f"{len(saved_files)} files processed.", 
        "details": saved_files
    }



# 4. 파일 + 폼 데이터 함께 받기
@app.post("/files/upload-with-form/")
async def upload_file_and_form(
    file: UploadFile = File(...),   # 업로드 파일
    notes: Optional[str] = None     
    # 파일 외에 함께 전달되는 텍스트 데이터
    # 실제로는 Form(...) 사용이 더 명확함
):
    
    print(f"Received file: {file.filename}")

    if notes:
        print(f"Received notes: {notes}")   
        # 파일과 함께 전달된 설명/메모 출력

    safe_filename = os.path.basename(file.filename or "uploaded_file")
    destination = os.path.goin(UPLOAD_DIR, safe_filename)   # 실제 저장 로직은 생략

    # 파일 + 폼 데이터 처리 결과 반환
    return {
        "filename": file.filename, 
        "notes": notes, 
        "save_path": "simulated_save"
    }