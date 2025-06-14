# 프로젝트 요약

본 프로젝트는 R과 Python을 병행하여 개발하는 환경을 제공하는 템플릿입니다. 이를 통해 프로젝트 초기 설정 과정을 간소화하며, 체계적인 관리를 지원합니다.

## 주요 특징

* R 환경 관리: `renv`
* Python 환경 관리: `venv` 및 개발자 편집모드 지원
* 로그 관리: `.env` 파일을 통해 로깅 레벨(DEBUG, INFO, WARN, ERROR)을 관리
* 데이터 관리 및 처리 효율화를 위한 폴더 구조
* 데이터베이스 연동 코드 제공(PostgreSQL)
* Quarto를 활용한 문서화 및 웹사이트 구축 지원

## 프로젝트 구조

```
p3133-r450-template/
├── R/
│   ├── utils_plot.R
│   ├── utils_db.R
│   ├── utils_analysis.R
│   └── my_functions.R
├── config/
│   ├── postgresql.yaml
│   ├── env.R
│   └── env.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── exports/
├── database/
│   ├── init_db.sql
│   ├── seed_data.sql
│   ├── db_utils.py
│   ├── db_utils.R
│   └── schema/
├── scripts/
│   ├── py/
│   │   ├── load_excel.py
│   │   └── insert_to_db.py
│   ├── r/
│   │   └── db_fetch_plot.R
│   └── shared/
│       ├── logger.py
│       └── db_config_loader.py
├── notebooks/
│   ├── r_analysis.qmd
│   ├── python_modeling.qmd
│   └── db_analysis.qmd
├── posts/
│   ├── 2025-06-insights.qmd
│   └── dashboard-overview.qmd
├── logs/
│   └── 2025-05-29-dev-log.qmd
├── styles/
│   ├── tooltip.css
│   └── nuclear-medicine-and-molecular-imaging.csl
├── scripts/tooltip.js
├── requirements.txt
├── renv.lock
├── .env
├── .Rprofile
├── README.md
└── docs/
```

---

# README.md

## p3133-r450-template

이 프로젝트는 R과 Python으로 병행하여 개발할 수 있는 표준화된 템플릿입니다. 데이터 처리, 분석 및 문서화를 효율적으로 수행하도록 돕습니다.

### 주요 기능

* **R 환경**: renv로 패키지 관리
* **Python 환경**: venv를 사용한 가상환경 및 개발자 편집모드 지원
* **로깅 관리**: `.env` 파일을 통한 로깅 수준 설정(DEBUG, INFO, WARN, ERROR)
* **데이터베이스**: PostgreSQL 연동 스크립트 포함
* **Quarto**를 이용한 웹사이트 및 문서화 지원

### 시작하기

```bash
git clone git@github.com:BenKorea/p3135-r450-template.git
cd p3135-r450-template
```

### Python 가상환경 설정

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .  # 개발자 편집모드 설치
```

### R 환경 설정

```R
source("renv/activate.R")
renv::restore()
```

### 로깅 설정

`.env` 파일에서 로깅 수준을 조정할 수 있습니다:

```bash
LOG_LEVEL=DEBUG  # INFO, WARN, ERROR로 변경 가능
```

### Quarto 문서화

Quarto 문서를 빌드하려면:

```bash
quarto render
```

### 문의

* **GitHub Repository**: [p3135-r450-template](git@github.com:BenKorea/p3135-r450-template.git)
