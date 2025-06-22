# src/nmdose/env/init.py

# ───── 표준 라이브러리 ─────
import os
from pathlib import Path
import logging
from typing import NamedTuple

# ───── 내부 모듈 ─────
from nmdose.config_loader.dotenv_loader import init_dotenv
from nmdose.security.vault_helper import input_passwords_for_accounts
from nmdose.security.vault_helper import debug_print_password_lengths
from nmdose.security.vault_helper import write_passwords_to_vault

from nmdose.config_loader.postgresql_loader import get_postgresql_config
from nmdose.config_loader.retrieve_options_loader import get_retrieve_config
from nmdose.config_loader.dicom_nodes_loader import get_nodes_config
from nmdose.utils.date_utils import make_batch_date_range

# ───── 로거 객체 생성 ─────
log = logging.getLogger(__name__)


class UserInfo(NamedTuple):
    """
    현재 사용자 정보를 구조화한 객체.
    이후 인증 시스템 연동 시 확장 가능.
    """
    role: str = "dev"             # 예: dev, user, superuser, keycloak
    username: str = "anonymous"   # 향후 세션 또는 토큰 기반 확장 대비
    authorized: bool = False      # user/superuser/keycloak일 때 True


def get_current_auth_mode() -> str:
    """
    현재 인증 모드(dev/user/superuser/keycloak)를 반환합니다.
    기본값은 'dev'입니다.
    """
    mode = os.getenv("NMDOSE_AUTH_MODE", "dev")
    if mode not in {"dev", "user", "superuser", "keycloak"}:
        log.warning(f"⚠️ 잘못된 NMDOSE_AUTH_MODE 값: {mode} → 'dev'로 대체")
        mode = "dev"
    log.info(f"▶ 인증 모드: {mode}")
    return mode


def get_current_user_info() -> UserInfo:
    """
    현재 사용자 정보를 반환합니다.
    추후 FastAPI Depends 등에서 사용할 수 있습니다.
    """
    role = os.getenv("NMDOSE_AUTH_MODE", "dev")
    username = os.getenv("NMDOSE_USER", "anonymous")
    authorized = role in {"user", "superuser", "keycloak"}
    return UserInfo(role=role, username=username, authorized=authorized)


def init_environment():
    """
    설정 파일을 로드하고, PACS 엔드포인트, 조회 파라미터 및 로그 디렉터리, 사용자 정보 등을 초기화합니다.

    반환:
      calling: C-FIND 요청 SCU AET/IP/Port
      called: C-FIND 대상 PACS AET/IP/Port
      modalities: 조회할 modality 리스트
      date_range: StudyDate 범위 문자열
      log_dir: 로그 파일을 저장할 디렉터리 경로
      auth_mode: 현재 인증 모드 (dev/user/superuser/keycloak)
      user_info: 사용자 정보 구조체 (UserInfo)
    """
    # .env 파일 로드 (환경변수 우선)
    init_dotenv()

    # PACS 및 retrieve 설정 로드
    db_config        = get_postgresql_config()
    log.info(f"DB 설정: {db_config}")
    
    PACS             = get_nodes_config()
    RETRIEVE_OPTIONS = get_retrieve_config()

    credentials = input_passwords_for_accounts()
    debug_print_password_lengths(credentials)
    write_passwords_to_vault(credentials)


    # PACS 엔드포인트 선택
    rm = os.getenv("ENABLE_SIMULATION")
    log.info(f"ENABLE_SIMULATION = {rm}")
    if rm == "1":
        calling, called = PACS.research, PACS.simulation
    else:
        calling, called = PACS.research, PACS.clinical

    # 조회할 modalities 및 날짜 범위
    modalities = RETRIEVE_OPTIONS.retrieve_to_research.modalities
    date_range = make_batch_date_range()
    log.info(f"조회할 Modalities: {modalities}")
    log.info(f"StudyDate 범위: {date_range}")

    # 인증 모드 및 사용자 정보 확인
    auth_mode = get_current_auth_mode()
    user_info = get_current_user_info()
    log.info(f"▶ 사용자: {user_info.username}, 권한: {user_info.role}, 인증여부: {user_info.authorized}")

    # 로그 디렉터리 생성
    log_dir = Path(r"C:\nmdose\logs\batch")
    log_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Log 디렉터리 생성됨: {log_dir}")

    return calling, called, modalities, date_range, log_dir, auth_mode, user_info
