from setuptools import setup, find_packages

setup(
    name="pe-coupling-analyzer",
    version="1.0.0",
    description="聚乙烯粘接声力耦合分析系统",
    author="北京信息科技大学",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "pe-analyzer=main:main",
        ],
    },
)
