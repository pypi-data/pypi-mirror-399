from setuptools import setup, find_packages
from typing import List

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()     
   

__version__ = "0.0.5"
REPO_NAME = "mongodbconnectionhminh@@"
PKG_NAME= "mongodb-connect-hminh"
AUTHOR_USER_NAME = "hoangminh125"
AUTHOR_EMAIL = "mluu9151@gmail.com"

setup(
    name=PKG_NAME,#đây là tên của gói
    version=__version__,#Phiên bản của gói
    author=AUTHOR_USER_NAME,#Tên tác giả của gói này
    author_email=AUTHOR_EMAIL,#Email tác giả 
    description="A python package for connecting with database.",#Viết mô tả ngắn gọn về gói
    long_description=long_description,#Mô tả dài về gói
    long_description_content_type="text/markdown",#Định dạng của mô tả dài VD: text/markdown
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",#URL của kho lưu trữ gói trên GitHub
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "src"},#Chỉ định thư mục gốc cho mã nguồn của gói
    packages=find_packages(where="src"),#Tự động tìm và bao gồm tất cả các gói con trong thư mục src
    )



