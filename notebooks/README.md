# How to run pdf_parser.py
## install tesseract
### Ubuntu
```sudo apt-get install tesseract-ocr```
### Mac
```brew install tesseract```
### Windows
https://github.com/UB-Mannheim/tesseract/wiki

## install tessract viet lang
### Ubuntu
```sudo apt-get install tesseract-ocr-vie```
### Mac
```brew install tesseract-lang```
### Windows
download vie.traineddata from https://github.com/tesseract-ocr/tessdata/blob/master/vie.traineddata

## Run example
1. copy a book in data/test1.pdf
2. change search term in pdf_parser.py
3. ```python pdf_parser.py```