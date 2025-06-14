# .Rprofile

# 1) renv 활성화 (프로젝트별 패키지 격리)
source("renv/activate.R")

# 2) dotenv 로컬 .env 로드 (LOG_LEVEL 등 환경변수 세팅)
if (requireNamespace("dotenv", quietly = TRUE)) {
  dotenv::load_dot_env(".env")
}

# 3) config 파일 경로 지정
config_file <- file.path("config", "config.yml")

# 4) 설정 불러오기 (파일이 있을 때만)
if (file.exists(config_file) && requireNamespace("config", quietly = TRUE)) {
  # config 패키지 attach 없이, 네임스페이스 경유 호출
  cfg <- config::get(
    config = Sys.getenv("ENVIRONMENT", "default"),
    file   = config_file
  )$logging
  default_level <- toupper(cfg$level)
} else {
  warning("config.yml not found or config package unavailable; using INFO as default.")
  default_level <- "INFO"
}

# 5) LOG_LEVEL 환경변수로 오버라이드 (없거나 잘못된 값은 default_level 사용)
lvl <- toupper(Sys.getenv("LOG_LEVEL", default_level))
if (lvl == "WARNING") lvl <- "WARN"
valid <- c("DEBUG", "INFO", "WARN", "ERROR")
if (! lvl %in% valid) {
  warning(sprintf("Invalid LOG_LEVEL '%s'; falling back to '%s'.", lvl, default_level))
  lvl <- default_level
}

# 6) futile.logger 에 레벨 적용
if (requireNamespace("futile.logger", quietly = TRUE)) {
  futile.logger::flog.threshold(get(lvl, asNamespace("futile.logger")))
  futile.logger::flog.info(sprintf("R logger initialized at %s", lvl))
} else {
  warning("Package 'futile.logger' not found; no logging initialized.")
}
