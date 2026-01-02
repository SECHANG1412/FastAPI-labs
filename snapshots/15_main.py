import os
import mimetypes
# 파일 확장자 (.txt, .jpg 등)를 보고 "이 파일이 어떤 타입인지(MIME 타입)" 추측하는 라이브러리
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI()

DOWNLOAD_DIR = "./downloadables/"
# 다운로드할 파일들이 들어 있는 폴더 경로
# "./"는 서버를 실행한 위치 기준
# 즉, main.py 옆에 downloadables/ 폴더가 있어야 함

##############################################################################################

# --- 기본 파일 다운로드 엔드포인트 ---

@app.get("/download/basic/{file_name}")
async def download_basic(file_name: str):
    '''
    가장 기본적인 파일 다운로드 : 지정된 이름의 파일을 찾아 FileResponse로 반환합니다.
    브라우저는 파일 유형에 따라 다르게 동작할 수 있습니다.
    (예: 이미지는 화면에 표시, PDF는 표시 또는 다운로드)
    '''
    # file_name:
    # URL 경로에서 사용자가 보낸 파일 이름 문자열

    # 보안: 실제 경로 생성 전 파일 이름 검증/새니타이징 필수!
    # 사용자가 "../" 같은 값을 넣으면 서버의 다른 파일을 몰래 가져갈 수 있기 때문

    safe_base_filename = os.path.basename(file_name)
    # os.path.basename : 
    # "../secret.txt" -> "secret.txt"
    # 즉, 폴더 경로를 제거하고 "파일 이름만" 남김 -> 경로 조작(Path Traversal) 1차 방어

    file_path = os.path.join(DOWNLOAD_DIR, safe_base_filename)
    # DOWNLOAD_DIR 와 파일 이름 합쳐 실제 파일 경로 생성
    # 예: "./downloadables/test.pdf"

    # 파일 존재 여부 확인
    if not os.path.isfile(file_path):                   # 해당 경로에 파일이 실제로 없으면
        print(f"Error: File not found at {file_path}")  # 서버 콘솔에 에러 로그 출력

        # 클라이언트에게 404 에러 응답 반환
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="File not found"
        )
        
    
    # 파일 경로가 의도한 디렉토리 내에 있는지 확인 (경로 조작 방어)
    # 만약 downloadables 폴더 밖의 파일이라면 접근 시도 자체를 차단
    if not file_path.startswith(os.path.abspath(DOWNLOAD_DIR)):
        print(f"Error: Access denied to path {file_path}")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied"
        )
    

    print(f"Serving file: {file_path}")
    # 서버가 어떤 파일을 내려주는지 로그 출력

    return FileResponse(path=file_path)
    # FileResponse:
    # 서버에 있는 파일을 그대로 HTTP 응답으로 전송
    # 브라우저는 파일 종류에 따라
    # -바로 열거나
    # -다운로드 창을 띄움


##############################################################################################

# --- 파일 다운로드 응답 커스터마이징 엔드포인트 ---

@app.get("/download/custom/{file_name}")
async def download_custom(file_name: str):
    '''
    파일 다운로드 시 media_type 과 filename(Content-Disposition)을 지정합니다.
    브라우저는 이 정보를 바탕으로 파일을 즉시 다운로드하도록 유도할 수 있습니다.
    '''

    # 파일 이름 안전 처리 (기본 다운로드와 동일)
    safe_base_filename = os.path.basename(file_name)
    file_path = os.path.join(DOWNLOAD_DIR, safe_base_filename)


    # 파일이 없으면 404 에러
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="File not found"
        )
    
    # downloadables 폴더 밖 접근 시도 차단
    if not file_path.startswith(os.path.abspath(DOWNLOAD_DIR)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # 파일 확장자로부터 MIME 타입 추측 (더 정확한 방법 사용 가능)
    # 예: ("application/pdf", None)
    media_type, _ = mimetypes.guess_type(file_path) 

    if media_type is None:
        # 확장자로 타입을 알 수 없는 경우
        media_type = 'application/octet-stream'
        # 가장 기본적인 "이진 파일" 타입
        # -> 브라우저가 안전하게 다운로드 처리


    # 다운로드될 때 사용자에게 보여줄 파일 이름 설정
    # 실제 서버 파일 이름과 달라도 상관없음
    download_filename = f"download_{safe_base_filename}"


    print(f"Serving file: {file_path} as {download_filename} with type {media_type}")


    return FileResponse(
        path=file_path,
        filename=download_filename, # Content-Disposition 헤더 설정 (다운로드 파일명 제안)
        media_type=media_type       # Content-Type 헤더 설정 (파일 종류 명시)
    )
    # 이 설정 덕분에 브라우저는 "이 파일은 다운로드해야 한다"고 판단함


##############################################################################################

# --- (참고) StreamingResponse 사용 예시 (개념) ---

# 이 예시는 실제 파일을 읽는 대신, 서버가 텍스트를 하나씩 만들어서 스트리밍하는 예제

async def fake_data_streamer():
    """간단한 비동기 제너레이터: 여러 줄의 텍스트를 생성합니다."""
    for i in range(10):
        # 10번 반복
        yield f"Line {i+1}: Some data chunk\\n"
        # yield :
        # 데이터를 한 번에 보내지 않고, 한 줄씩 조금씩 클라이언트로 보냄 -> 대용량 데이터에 매우 유리


async def download_stream():
    """
    StreamingResponse 를 사용하여 동적으로 생성된 데이터를 스트리밍합니다.
    대용량 파일 또는 실시간 데이터 스트리밍에 유용합니다.
    """
    stream = fake_data_streamer()   # 데이터 생성기 준비

    return StreamingResponse(
        content=stream,             # 스트리밍할 데이터 흐름
        media_type="text/plain",    # 텍스트 파일임을 브라우저에 알림
        headers={"Content-Disposition": "attachment; filename=streamed_data.txt"}   # 강제로 다운로드하도록 지시
    )