from pathlib import Path
import logging
import os
from dotenv import load_dotenv

# ───── 로거 설정 ─────
log = logging.getLogger(__name__)
log.debug(f"▶ 로거 설정: {log.name} "
          f"(raw level={log.level}, effective={logging.getLevelName(log.getEffectiveLevel())})")

def init_dotenv(env_path: Path | str = None):
    """
    프로젝트 루트의 .env 파일을 로드합니다.
    env_path 인자를 주면 해당 경로를 우선 사용합니다.
    """
    if env_path is None:
        env_path = Path(__file__).parents[3] / ".env"

    if not Path(env_path).is_file():
        log.error(f"❌ .env 파일이 존재하지 않습니다: {env_path}")
        return

    load_dotenv(dotenv_path=env_path)
    log.info(f".env 파일 로드됨: {env_path}")

    # ───── .env에서 로드된 주요 환경변수 출력 ─────
    env_vars = {
        "VAULT_ADDR": os.getenv("VAULT_ADDR"),
        "VAULT_TOKEN": os.getenv("VAULT_TOKEN"),
        "VAULT_SECRET_PATH": os.getenv("VAULT_SECRET_PATH"),
        "ENABLE_SIMULATION": os.getenv("ENABLE_SIMULATION"),
    }

    log.info(".env에서 로드된 주요 환경변수:")
    for key, val in env_vars.items():
        masked = val if (not key.endswith("TOKEN") and val is not None) else "(hidden)"
        log.info(f"  - {key} = {masked}")

    # ENABLE_SIMULATION 유효성 확인
    simulation = os.getenv("ENABLE_SIMULATION")
    if simulation not in {"0", "1"}:
        log.error(f"❌ ENABLE_SIMULATION 값이 잘못되었습니다: '{simulation}' (0 또는 1이어야 함)")
        raise ValueError("ENABLE_SIMULATION 값은 '0'(비활성화) 또는 '1'(시뮬레이션 모드)이어야 합니다.")
    else:
        sim_str = "활성화됨" if simulation == "1" else "비활성화됨"
        log.info(f"ENABLE_SIMULATION 확인됨: {simulation} ({sim_str})")

