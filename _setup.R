# _setup.R
library(here); library(futile.logger); library(fs); library(purrr)

if (file.exists(here("DESCRIPTION")) && requireNamespace("pkgload", quietly=TRUE)) {
  pkgload::load_all(path = here())
  flog.info("📄 사용자 정의 함수 로드 완료 (pkgload::load_all)")
} else {
  fs::dir_ls(here("R"), glob = "*.R") %>% walk(source)
  flog.info("📄 사용자 정의 함수 로드 완료 (fs::dir_ls + source)")
}
