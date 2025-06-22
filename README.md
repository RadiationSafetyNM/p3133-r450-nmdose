## 프로젝트 개요
1. 필요한 기능
 1) 병원 clinicalPACS에서 researchPACS로 사용자가 지정하는 ModalitiesInStudy들인 Study들retrieve (추출)
(1)추출대상검사 오류점검하기
- 사용자가 설정한 ModalitiesInStudy 인 모든 StudyDescription들 진행
- StudyDescription별로 가장 빠른 StudyDate를 비교하여 가장빠른 날짜 결정
- 가장빠른날짜부터 현재까지 모든 Study들을 조회하여 StudyDate, StudDescription, ModalitiesInStudy, StudyInstanxeUid 회신받아 database 만들기
- StadDescription별로 ModalitiesInStudy조사해서 잘못된 ModalitiesInStudy로 되어 있다면 오류수정
- 누락된 StudyDescription이 있다면 사용자가 설정에 추가하고 이것도 추가하여 조회
(2) (1)단계에서 확정된 검사들 추출하기
- StudyInstanceUID를 movescu로 전달하여 retrieve 구현
- 단계별 성공여부는 stdout/stderr을 이용하고 log 파일로 정리
- 위사항을 nmdose database rpacs schema에 table로도 저장
(3) 연도별 검사항목별 집계 등을 웹페이지로 제공
2) researchPACS에서 선량보고서 및 필요한 Image 추출후 dosePACS로 전송
(1) 구조화된 선량보고서
(2) Study 마다 Series별 Image instance 1개씩
3) dosePACS에서는 선량보고서와 Image dicomhead를 파싱하여 선량정보추출
(1) 선량보고서는 CT 선량정보추출
(2) Image Instance 중 MidalitiesInSeries가 PT 인 경우는 방사성의약품 투여량 정보 추출
(3) 검사프로토콜 정보도 같이 추출
(4) 검사프로토콜별 선량분석 및 웹페잊로 제공
## 개발환경
1. 원도우10 PC 및 윈도우 11노트북 (WSL2)
2. 파이썬
3. dcmtk
4. R
5. Git
6. VS Code/ R server
## 시스템 아키텍처
1. clinicalPACS (실제 병원망에 연결된 PACS) NMPACS 172.17.111.214:104
2. researchPACS ORTHANC 127.0.0.1:4242
1) PostgreSQL을 연결하여 indexing까지민 구현하고 저장은 Orthanc 고유의 것을 사용
3. dosePACS NMDOSE127.0.01:5678
4. simulationPACS (개발자 PC)
1) 개발단계에서 네트워크 연결이 없더라도 테스트위해 구축  NMFULLDATA 127.0.0.1:5680 (ENABLE_SIMULATION=1 .env변수 이용)
## 실행 모드
실행명령어에 인자로 running-mode (dev, test, prod)로 주어서 구현
auth-mode 인자로 dev, keycloak로 구현
1. ENABLE_SIMULATION=0이면
1) Clinical PACS → Research PACS로 DICOM 파일 전송
2) Research PACS에서 선별 후 Dose PACS로 선량 정보 전송
2. Simulation 모드 (ENABLE_SIMULATION=1)
1) Simulation PACS → Research PACS로 DICOM 파일 전송
2) 노트북개발환경 등 병원 네트워크가 연결되지 않을 때 모사 PACS
## 전송 및 저장 전략
1. 전체 전송
1) 모든 DICOM 객체를 Research PACS에 보존
2. 선별 전송 또는 자동 삭제
1) 대용량 전송이 발생하는 병원의 경우 선량 정보 파일(RDSR/SR)만 Dose PACS로 직접 전송
2) 또는 Research PACS에 보관 후 불필요 파일 자동 삭제
## 기술 스택
1. 언어 및 툴
1) Python 기반 스크립트 (속도 중요 구간: DCMTK CLI 활용)
2. 오픈소스 PACS
1) Research PACS: Orthanc
2) Dose/Simulation PACS: Conquest
3. 데이터베이스
1) PostgreSQL (Orthanc 메타데이터, 전송 로그 저장)
4. 보안솔루션
1) keyOak 등의 오픈소스 적용
2) 가능하다면 하드디스크 수준의 암호화 검토
3) DICOM 통신에 대해서는 TLS 옵션, 인증서 옵션으로 구축
## 개발 환경
1. OS: Windows 10 or Window11+ WSL2 Ubuntu
2. 가상환경: Python venv (VS Code 연동)
3. 동기화: GitHub 리포지토리 사용 (PC/노트북 간)
4. 파이썬 편집모드 사용
## 폴더 구조 (C:\nmdose)
```
C:\nmdose
├─ src/nmdose
│          ├─ api
│          │     └─ start-findscu.py
│          ├─ config_loader
│          │           └─ nmdose_accounts_loader.py
│          │           └─ dotenv_loader.py
│          │           └─ dicom_network_entities_loader.py
│          │           └─ retrieve_options_loader.py
│          ├─ env\init.py
│          ├─ utils
│          └─ tasks\findscu_core.py
│          ├─ templates
│          │           └─ dashboard.html
│          └─ main.py
│          └─ run.py
├─ scripts
│  └─ findscu_preview.py
│  └─ finds_move.py
├─ tests
└─ config\
│  └─ nmdose_accounts.yaml
│  └─ postgresql.yaml
│  └─ dicom_network_entities.yaml
│  └─ retrieve_options.yaml
│  └─ schema_definitions.yaml
└─ pyproject.toml
└─ (venv)
└─ requirements.txt
└─ .env
```
## 보안
비밀번호는 vault 오픈소스를 이용하여 저장
개발단계에는 vault server -dev 등의 간편한 옵션으로 진행
