# src/nmdose/config_loader/postgresql_loader.py

import logging
from pathlib import Path
from dataclasses import dataclass
import yaml

log = logging.getLogger(__name__)

# config/postgresql.yaml 경로 지정
CONFIG_FILE = Path(__file__).resolve().parents[3] / "config" / "postgresql.yaml"

@dataclass(frozen=True)
class PostgresConfig:
    host: str
    port: int
    database: str
    superuser_id: str
    user_id: str

# 모듈 수준 캐시
_postgres_config_cache: PostgresConfig | None = None

def get_postgresql_config(path: Path = CONFIG_FILE) -> PostgresConfig:
    """
    postgresql.yaml 파일을 읽어 PostgresConfig 객체로 반환합니다.
    - host: 접속할 호스트
    - port: 포트 번호
    - database: 데이터베이스 이름
    - superuser_id: 슈퍼유저 계정명
    - user_id: 일반 애플리케이션 계정명

    설정 파일이 없거나 필수 키가 누락된 경우 예외가 발생합니다.
    """
    global _postgres_config_cache
    if _postgres_config_cache is not None:
        return _postgres_config_cache

    if not path.is_file():
        log.error(f"postgresql.yaml 파일을 찾을 수 없습니다: {path}")
        raise FileNotFoundError(f"postgresql.yaml 파일이 없습니다: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    try:
        cfg = PostgresConfig(
            host=raw["host"],
            port=int(raw["port"]),
            database=raw["database"],
            superuser_id=raw["superuser_id"],
            user_id=raw["user_id"],
        )
        _postgres_config_cache = cfg
        log.info("✅ postgresql.yaml 로딩 완료")
        return cfg
    except KeyError as e:
        log.error(f"postgresql.yaml에 필수 설정이 없습니다: {e}")
        raise KeyError(f"postgresql.yaml에 설정이 없습니다: {e}")
    except (TypeError, ValueError) as e:
        log.error(f"postgresql.yaml 값 형식 오류: {e}")
        raise ValueError(f"postgresql.yaml 값 형식 오류: {e}")
