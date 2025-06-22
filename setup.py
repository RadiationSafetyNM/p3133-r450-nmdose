# setup.py
import pathlib
from setuptools import setup, find_packages

# 프로젝트 루트 경로
HERE = pathlib.Path(__file__).parent

# README.md를 long_description에 넣기
long_description = (HERE / "README.md").read_text(encoding="utf-8")

# requirements.txt에서 의존성 읽기
install_requires = [
    "iniconfig==2.1.0",
    "packaging==25.0",
    "pluggy==1.6.0",
    "Pygments==2.19.1",
    "pytest==8.4.0",
    "PyYAML==6.0.2"
]

setup(
    name="NMDose",        # 복제 후 프로젝트명으로 변경
    version="0.1.0",
    description="프로젝트 설명을 간단히 적어주세요",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BenKorea",
    author_email="benkorea.ai@gmail.com",
    python_requires=">=3.8",

    # 프로젝트 내 파이썬 패키지 자동 탐색
    packages=find_packages(exclude=[
        "docs", "data", "notebooks", "R", "*.qmd", "logs", "styles"
    ]),
    include_package_data=True,
    install_requires=install_requires,

    # 스크립트를 커맨드라인 커맨드로 등록 (필요에 따라 수정)
    entry_points={
        "console_scripts": [
            "load-excel = scripts.py.load_excel:main",
            "insert-to-db = scripts.py.insert_to_db:main",
            # "fetch-plot = scripts.r.db_fetch_plot:main",  ← R 스크립트인 경우 제외
        ]
    },
)
