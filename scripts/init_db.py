#!/usr/bin/env python3
"""
scripts/init_db.py

이 스크립트는 PostgreSQL 데이터베이스 초기화 작업을 수행합니다:
1. config/postgresql.yaml에서 설정 로드
2. 스키마 정의(config/schema_definitions.yaml) 로드
3. superuser로 데이터베이스 생성
4. 애플리케이션 유저에 public 스키마 권한 부여
5. 애플리케이션 유저로 테이블 생성
6. Alembic 마이그레이션 적용
"""

import logging
import subprocess
from pathlib import Path
import sys
import yaml
import psycopg2
from psycopg2 import sql

# src 경로를 최상위로 설정
project_root = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(project_root))

from nmdose.config_loader.postgresql_loader import get_postgresql_config

# 로거 설정
logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_schema_definitions() -> dict:
    """config/schema_definitions.yaml에서 스키마 정의를 로드합니다."""
    schema_file = Path(__file__).parent.parent / "config" / "schema_definitions.yaml"
    if not schema_file.is_file():
        logger.error("Schema file not found: %s", schema_file)
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    content = schema_file.read_text(encoding="utf-8-sig")
    schema_data = yaml.safe_load(content) or {}
    logger.info("Loaded schema definitions from %s", schema_file)
    return schema_data


def create_database(cfg):
    """슈퍼유저로 'postgres' DB에 접속해 대상 데이터베이스를 생성합니다."""
    conn = psycopg2.connect(
        dbname='postgres',
        host=cfg.host,
        port=cfg.port,
        user=cfg.superuser_id,
        password=cfg.superuser_id,
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (cfg.database,))
        if not cur.fetchone():
            logger.info("Database '%s' not found. Creating...", cfg.database)
            cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(cfg.database)))
            logger.info("Database '%s' created.", cfg.database)
        else:
            logger.info("Database '%s' already exists.", cfg.database)
    conn.close()


def grant_schema_privileges(cfg):
    """superuser로 public 스키마에 대한 권한을 애플리케이션 유저에게 부여합니다."""
    conn = psycopg2.connect(
        dbname=cfg.database,
        host=cfg.host,
        port=cfg.port,
        user=cfg.superuser_id,
        password=cfg.superuser_id,
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        stmt = sql.SQL(
            "GRANT USAGE, CREATE ON SCHEMA public TO {}"
        ).format(sql.Identifier(cfg.user_id))
        cur.execute(stmt)
        logger.info("Granted USAGE, CREATE on schema public to %s", cfg.user_id)
    conn.close()


def create_tables(cfg, tables: dict):
    """애플리케이션 유저로 테이블을 생성합니다."""
    conn = psycopg2.connect(
        dbname=cfg.database,
        host=cfg.host,
        port=cfg.port,
        user=cfg.user_id,
        password=cfg.user_id,
    )
    with conn:
        with conn.cursor() as cur:
            for tbl_name, tbl_def in tables.items():
                cols = []
                for col in tbl_def.get("columns", []):
                    col_line = f"{col['name']} {col['type']}"
                    if col.get("primary_key"):
                        col_line += " PRIMARY KEY"
                    cols.append(col_line)

                ddl = sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {} ({});"
                ).format(
                    sql.Identifier(tbl_name),
                    sql.SQL(", ").join(sql.SQL(c) for c in cols)
                )
                logger.info("Ensuring table '%s'...", tbl_name)
                cur.execute(ddl)
                logger.info("Table '%s' OK.", tbl_name)
    conn.close()


def apply_alembic_migrations():
    """alembic 디렉토리가 있으면 마이그레이션을 적용합니다."""
    alembic_dir = Path(__file__).parent.parent / "alembic"
    if alembic_dir.is_dir():
        logger.info("Applying Alembic migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Alembic migrations applied.")
    else:
        logger.info("No 'alembic' directory found. Skipping migrations.")


def main():
    setup_logging()
    logger.info("Starting database initialization")

    cfg = get_postgresql_config()
    schema_data = load_schema_definitions()

    create_database(cfg)
    grant_schema_privileges(cfg)

    # 'tables' 키가 없으면 최상위가 테이블 맵핑이라고 가정
    tables = schema_data.get("tables", schema_data)
    create_tables(cfg, tables)
    apply_alembic_migrations()

    logger.info("Database initialization completed successfully")


if __name__ == "__main__":
    main()
