# src/nmdose/config_loader/account_ids_loader.py

from dataclasses import dataclass
from pathlib import Path
import yaml
import logging

log = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parents[3] / "config" / "account_ids.yaml"

# ───── 데이터 구조 ─────

@dataclass(frozen=True)
class SchemaAccess:
    name: str
    privileges: list[str]

@dataclass(frozen=True)
class AppUser:
    id: str
    description: str
    database: str
    schemas: list[SchemaAccess]

@dataclass(frozen=True)
class Superuser:
    id: str
    description: str

@dataclass(frozen=True)
class AccountStructure:
    superuser: Superuser
    users: list[AppUser]

# ───── 내부 캐시 ─────
_account_struct: AccountStructure | None = None

# ───── 공통 로딩 ─────

def load_account_structures(path: Path = CONFIG_FILE) -> AccountStructure:
    global _account_struct
    if _account_struct is not None:
        return _account_struct

    if not path.is_file():
        raise FileNotFoundError(f"account_ids.yaml 파일이 없습니다: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8-sig"))

    # superuser
    su_raw = raw.get("superuser", {})
    superuser = Superuser(id=su_raw["id"], description=su_raw["description"])

    # users
    users = []
    for u in raw.get("users", []):
        schemas = [SchemaAccess(name=s["name"], privileges=s["privileges"]) for s in u.get("schemas", [])]
        users.append(AppUser(
            id=u["id"],
            description=u["description"],
            database=u["database"],
            schemas=schemas
        ))

    _account_struct = AccountStructure(superuser=superuser, users=users)
    log.info("✅ account_ids.yaml 로딩 완료")
    return _account_struct

# ───── 분리된 책임 함수 ─────

def get_auth_accounts() -> dict[str, str]:
    """
    DB 접속용 계정 ID → 역할 매핑
    ex) {'nmuser': 'user', 'nmsuper': 'superuser'}
    """
    struct = load_account_structures()
    result = {struct.superuser.id: "superuser"}
    for user in struct.users:
        result[user.id] = "user"
    return result

def get_access_control_map() -> dict[str, AppUser | Superuser]:
    """
    역할 이름 → 계정 객체
    ex) {'superuser': Superuser(...), 'nmuser': AppUser(...)}
    """
    struct = load_account_structures()
    result = {"superuser": struct.superuser}
    for user in struct.users:
        result[user.id] = user
    return result
