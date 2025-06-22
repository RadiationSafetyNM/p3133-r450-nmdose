# src/nmdose/security/vault_helper.py

import os
import secrets
import logging
import traceback

import hvac

from nmdose.config_loader.account_ids_loader import load_account_structures

# ───── 로거 객체 생성 ─────
log = logging.getLogger(__name__)

  
def input_passwords_for_accounts() -> dict[str, str]:
    """
    account_ids.yaml에 정의된 계정들에 대해 비밀번호를 사용자로부터 두 번 입력받아 검증 후 저장합니다.
    비밀번호가 일치하지 않으면 재입력을 요구합니다.

    반환값:
        dict[str, str] - 계정 ID → 비밀번호
    """
    import getpass
    struct = load_account_structures()
    accounts = [struct.superuser.id] + [u.id for u in struct.users]

    result = {}
    for acc in accounts:
        while True:
            pw1 = getpass.getpass(f"🔐 비밀번호 입력 ({acc}): ")
            pw2 = getpass.getpass(f"🔁 비밀번호 재입력 ({acc}): ")

            if not pw1 or not pw2:
                print("⚠️ 비밀번호는 공백일 수 없습니다.")
                continue

            if pw1 != pw2:
                print("❌ 두 비밀번호가 일치하지 않습니다. 다시 시도하세요.")
                continue

            result[acc] = pw1
            break

    log.info("✅ 모든 계정에 대해 비밀번호 입력 및 검증 완료")
    return result


def debug_print_password_lengths(passwords: dict[str, str]):
        for acc_id, pw in passwords.items():
            log.debug(f"[입력 완료] 계정: {acc_id}, 비밀번호 길이: {len(pw)}자")


def write_passwords_to_vault(credentials: dict[str, str]) -> None:
    """
    hvac를 사용해 Vault에 비밀번호를 저장합니다.
    Vault 서버 상태 및 인증 정보를 확인하고,
    토큰 유효성 문제와 권한 부족 문제를 구분하여 로그를 출력합니다.
    """
    vault_addr = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200")
    vault_token = os.getenv("VAULT_TOKEN")

    log.debug(f"📡 VAULT_ADDR = {vault_addr}")
    log.debug(f"🔐 VAULT_TOKEN 설정됨 여부: {'✅' if vault_token else '❌'}")
    if not vault_token:
        log.error("❌ VAULT_TOKEN 환경변수가 비어 있습니다. 인증 불가능.")
        return

    try:
        client = hvac.Client(url=vault_addr, token=vault_token, verify=False)

        # Vault 연결 상태 확인
        log.debug("🔎 Vault 상태 점검 중: /v1/sys/health")
        try:
            health = client.sys.read_health_status(method="GET")
            log.debug(f"✅ Vault 상태 응답: {health}")
            server_mode = (
                "dev" if health.get("standby") is False and health.get("sealed") is False else "sealed/unknown"
            )
            log.debug(f"🛠 Vault 모드 추정: {server_mode}")
        except Exception as health_err:
            log.error("❌ Vault 서버 상태 확인 실패")
            log.debug(traceback.format_exc())
            return

        # Vault 토큰 유효성 검사 및 권한 확인
        try:
            token_info = client.auth.token.lookup_self()
            ttl = token_info['data'].get('ttl')
            policies = token_info['data'].get('policies')
            log.debug(f"✅ Vault 토큰 유효성 확인 완료: TTL={ttl}s, policies={policies}")
        except hvac.exceptions.Forbidden:
            log.error("❌ Vault 토큰은 유효하지만 lookup_self 권한이 없습니다.")
            return
        except hvac.exceptions.InvalidRequest:
            log.error("❌ Vault 토큰이 아예 유효하지 않습니다 (로그인 실패).")
            return
        except Exception as e:
            log.error(f"❌ Vault 토큰 유효성 확인 중 예외 발생: {e}")
            log.debug(traceback.format_exc())
            return

        # 비밀번호 저장 시도
        for acc_id, pw in credentials.items():
            path = f"nmdose/{acc_id}"
            try:
                log.debug(f"💾 Vault 저장 시도: 경로={path}, 비밀번호 길이={len(pw)}자")
                client.secrets.kv.v2.create_or_update_secret(
                    path=path,
                    secret={"password": pw}
                )
                log.info(f"✅ Vault 저장 성공: {path}")
            except hvac.exceptions.Forbidden:
                log.error(f"❌ Vault 저장 실패: 권한 없음 (path={path})")
            except Exception as e:
                log.error(f"❌ Vault 저장 실패: 예외 발생 - {e}")
                log.debug(traceback.format_exc())

    except Exception as e:
        log.error(f"❌ Vault 연동 전체 예외 발생: {e}")
        log.debug(traceback.format_exc())
