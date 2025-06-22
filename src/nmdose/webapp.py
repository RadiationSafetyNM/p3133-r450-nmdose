# src/nmdose/webapp.py

"""
FastAPI 기반 웹 애플리케이션 엔트리포인트

기능:
- '/' 라우트로 HTML 대시보드 렌더링
- '/api/start-findscu' POST 요청 시 findscu_preview.py 실행 (비동기 백그라운드)
- 권한 모드에 따라 API 접근 제어

보안 설계:
- 인증 모드는 환경변수 NMDOSE_AUTH_MODE (dev/user/superuser) 기반
- 향후 Keycloak 또는 세션 기반 인증으로 확장 가능

개선 사항:
- 앱 실행 시점에 환경 초기화하도록 lifespan 이벤트 사용
- API 엔드포인트 권한 분기를 위한 Depends 기반 더미 구조 포함
"""

# ───── 표준 라이브러리 ─────
import sys
import logging
import subprocess
import os
from pathlib import Path
from uuid import uuid4

# ───── 서드파티 라이브러리 ─────
from fastapi import FastAPI, Request, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ───── 내부 모듈 ─────
from nmdose.env.init import init_environment

# ───── 로거 설정 ─────
log = logging.getLogger(__name__)


# ▒▒ 권한 제어를 위한 의존성 (더미) ▒▒
def get_current_user_role() -> str:
    """
    현재 인증된 사용자 권한을 반환합니다. (dev/user/superuser 중 하나)
    환경변수 NMDOSE_AUTH_MODE를 사용합니다.
    """
    return os.getenv("NMDOSE_AUTH_MODE", "dev")

def require_role(*allowed_roles: str):
    """
    주어진 역할 중 하나가 아닌 경우 403 Forbidden 예외를 발생시킵니다.
    """
    def checker(role: str = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"요청 권한 부족: {role} (허용된 역할: {allowed_roles})"
            )
        return role
    return checker


# ▒▒ FastAPI 앱 객체 ▒▒
app = FastAPI()

# ▒▒ 템플릿 엔진 설정 ▒▒
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ▒▒ 환경 변수 캐시 변수 ▒▒
CALLING = CALLED = MODALITIES = DATE_RANGE = LOG_DIR = None


@app.on_event("startup")
async def startup_event():
    """
    FastAPI 서버 시작 시 호출되는 초기화 이벤트입니다.
    PACS 설정, DB 연결 정보, 날짜 범위 등을 설정합니다.
    """
    global CALLING, CALLED, MODALITIES, DATE_RANGE, LOG_DIR
    CALLING, CALLED, MODALITIES, DATE_RANGE, LOG_DIR, AUTH_MODE, AUTH_INFO = init_environment()
    log.info("✅ 웹 앱 환경 초기화 완료")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    기본 대시보드 페이지를 렌더링합니다.
    """
    log.debug("▶ 대시보드 페이지 요청됨")
    return templates.TemplateResponse("dashboard.html", {"request": request})


def run_findscu(calling, called):
    """
    findscu_preview.py 스크립트를 subprocess로 실행합니다.
    """
    log.info(f"▶ findscu_preview.py 실행 시작: calling={calling.aet}, called={called.aet}")
    project_root = Path(__file__).resolve().parents[2]
    script_path = project_root / "scripts" / "findscu_preview.py"
    subprocess.run([sys.executable, str(script_path)], check=True)
    log.info("▶ findscu_preview.py 실행 완료")


@app.post("/api/start-findscu")
async def start_findscu(
    background_tasks: BackgroundTasks,
    role: str = Depends(require_role("superuser", "dev"))  # 권한 분기용
):
    """
    findscu_preview.py 실행 요청을 처리합니다.
    백그라운드 작업으로 실행되며, 권한이 있는 사용자만 호출할 수 있습니다.

    Returns:
        JSON: {"status": "started", "task_id": "<uuid4>"}
    """
    task_id = str(uuid4())
    log.info(f"▶ /api/start-findscu 호출됨 (role={role}, task_id={task_id})")
    background_tasks.add_task(run_findscu, CALLING, CALLED)
    return {"status": "started", "task_id": task_id}
