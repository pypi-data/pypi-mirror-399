import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async-drf-api",
    version="0.3.0",
    author="sixsfish",
    author_email="sixsfish@foxmail.com",
    description="An asynchronous Web API framework based on Starlette, inspired by Django REST Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sixsfish/async_drf_api",
    packages=["async_drf_api",
     "async_drf_api.web",
        "async_drf_api.orm",
        "async_drf_api.serializers",
        "async_drf_api.views",
        ],  # 明确指定包名，避免包含其他目录
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.12",
    install_requires=[
        "starlette>=0.41.3",
        "uvicorn[standard]>=0.34.0",
    ],
)

