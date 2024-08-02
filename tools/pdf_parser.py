import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from crewai_tools import tool
from typing import List, Dict, Tuple

def pdf_to_images(pdf_path):
    """
    Convert each page of the PDF to an image and return the list of images.
    """
    images = convert_from_path(pdf_path)
    return images

def ocr_image(image, lang='vie'):
    """
    Perform OCR on the provided image and return the extracted text.
    """
    text = pytesseract.image_to_string(image, lang=lang)
    return text

@tool("PDFParserTool")
def extract_and_search_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Convert PDF pages to images, perform OCR on each image, and return the pdf as an array.
    Arguments:
        pdf_path is the relative path to this file of absolute path
    Return: a list of string in which index represents the page, and value represent text of the page
    """
    images = pdf_to_images(pdf_path)
    ocr_results = [ocr_image(image) for image in images]
    return ocr_results
    

def search_text_in_ocr_results(ocr_results, search_term):
    """
    Search for the search_term in the OCR results and return the matched results.
    """
    results = []
    for page_num, text in enumerate(ocr_results):
        if search_term.lower() in text.lower():
            results.append((page_num, text))
    return results

@tool("PDFSearchTool")
def pdf_searcher(ocr_results: List[str], search_term: str) -> List[Tuple[int,str]]:
    """
    This tools search for a desired term in pdf file which is convert to text and return the result
    Arguments:
        ocr_results is converted version of a pdf file to text
        search_term is the term which you want to search in the pdf file
    return: a list of tuple, 1st element of tuple is the page, 2nd element of typle is the text of that result page
    """
    results = search_text_in_ocr_results(ocr_results, search_term)

    return results
if __name__ == "__main__":
    pdf_path = '../data/test1.pdf'  # Replace with the path to your PDF file
    search_term = 'nguyên tử'  # Replace with the term you want to search for
    main(pdf_path, search_term)