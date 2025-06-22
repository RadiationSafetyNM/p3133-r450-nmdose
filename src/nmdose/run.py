# ───── 표준 라이브러리 ─────
import argparse
import logging
import os
from pathlib import Path

# ───── 서드파티 라이브러리 ─────
import uvicorn

# ───── 로컬 라이브러리 ─────
from nmdose.security.keycloak_config import get_keycloak_settings

# ───── 로거 객체 생성 ─────
log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="nmdose FastAPI 서버 실행")
    parser.add_argument("--loglevel", default="info", choices=["debug", "info", "warning", "error", "critical"])
    parser.add_argument("--running-mode", default="dev", choices=["dev", "test", "prod"],
                        help="실행 환경 모드 지정")
    parser.add_argument("--auth-mode", default="dev", choices=["dev", "user", "superuser", "keycloak"],
                        help="인증 모드 지정")
    return parser.parse_args()

def configure_logging(loglevel: str):
    logging.basicConfig(
        level=loglevel.upper(),
        format="%(asctime)s [%(levelname)s] %(name)s ▶ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.getLogger("uvicorn").setLevel(loglevel.upper())
    logging.getLogger("uvicorn.error").setLevel(loglevel.upper())
    logging.getLogger("uvicorn.access").setLevel(loglevel.upper())

def set_environment(args):
    os.environ["NMDOSE_LOGLEVEL"] = args.loglevel
    os.environ["NMDOSE_RUNNING_MODE"] = args.running_mode
    os.environ["NMDOSE_AUTH_MODE"] = args.auth_mode

def load_keycloak():
    kc = get_keycloak_settings()
    log.info(f"Keycloak 설정: {'활성화됨' if kc['enabled'] else '비활성화됨'}")
    return kc

def prepare_ssl(running_mode: str):
    if running_mode != "prod":
        log.info("HTTPS 비활성화: HTTP로 실행됩니다")
        return None, None

    cert_dir = Path(__file__).resolve().parents[2] / "certs"
    ssl_certfile = cert_dir / "server.crt"
    ssl_keyfile = cert_dir / "server.key"

    if not ssl_certfile.is_file() or not ssl_keyfile.is_file():
        log.error("❌ 실행 모드 'prod'이지만 인증서 파일이 없습니다.")
        log.error(f"  → {ssl_certfile}")
        log.error(f"  → {ssl_keyfile}")
        raise FileNotFoundError("SSL 인증서가 필요합니다.")

    log.info("✅ HTTPS 활성화: 인증서 적용됨")
    return ssl_certfile, ssl_keyfile

def start_uvicorn_server(args, ssl_certfile, ssl_keyfile):
    uvicorn.run(
        "nmdose.webapp:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level=args.loglevel,
        ssl_certfile=str(ssl_certfile) if ssl_certfile else None,
        ssl_keyfile=str(ssl_keyfile) if ssl_keyfile else None
    )


# ✅ 권한 분기를 위한 추후 의존함수 (더미)
def get_current_user_role() -> str:
    """
    현재 인증된 사용자 권한을 반환합니다.
    추후 FastAPI Depends() 등에서 사용될 수 있습니다.
    예: "superuser", "user", "dev"
    """
    return os.getenv("NMDOSE_AUTH_MODE", "dev")


def main():
    args = parse_args()
    configure_logging(args.loglevel)
    set_environment(args)

    log.info(f"NMDOSE_LOGLEVEL = {os.environ['NMDOSE_LOGLEVEL']}")
    log.info(f"NMDOSE_RUNNING_MODE = {os.environ['NMDOSE_RUNNING_MODE']}")
    log.info(f"NMDOSE_AUTH_MODE = {os.environ['NMDOSE_AUTH_MODE']}")

    load_keycloak()
    ssl_certfile, ssl_keyfile = prepare_ssl(args.running_mode)
    start_uvicorn_server(args, ssl_certfile, ssl_keyfile)


if __name__ == "__main__":
    main()
