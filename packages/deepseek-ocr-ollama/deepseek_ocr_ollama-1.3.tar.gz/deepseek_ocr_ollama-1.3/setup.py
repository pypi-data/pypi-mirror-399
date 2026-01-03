#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setup(
  name="deepseek-ocr-ollama",
  version="1.3",
  packages=find_packages(),
  description="A simple script that uses the Ollama API to get the Markdown text from a PDF or image file using the DeepSeek-OCR model",
  entry_points={
    'console_scripts': [
      'deepseek-ocr-ollama = deepseek_ocr_ollama.__main__:main',
    ],
  },
  url="https://github.com/jfhack/deepseek-ocr-ollama",
  install_requires=[
    'ollama',
    'pymupdf',
    'python-dotenv',
    'tqdm',
    'pillow'
  ],
  long_description=long_description,
  long_description_content_type="text/markdown"
)
