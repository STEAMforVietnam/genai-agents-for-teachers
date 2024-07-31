import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Set the path to the Tesseract executable if needed (for Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

def search_text_in_ocr_results(ocr_results, search_term):
    """
    Search for the search_term in the OCR results and return the matched results.
    """
    results = []
    for page_num, text in enumerate(ocr_results):
        if search_term.lower() in text.lower():
            results.append((page_num, text))
    return results

def extract_and_search_text_from_pdf(pdf_path, search_term):
    """
    Convert PDF pages to images, perform OCR on each image, and search for the term.
    """
    images = pdf_to_images(pdf_path)
    ocr_results = [ocr_image(image) for image in images]
    search_results = search_text_in_ocr_results(ocr_results, search_term)
    return search_results

def main(pdf_path, search_term):
    """
    Main function to extract text from a PDF and search for a term.
    """
    print(f"Processing PDF: {pdf_path}")
    results = extract_and_search_text_from_pdf(pdf_path, search_term)

    if results:
        for page_num, text in results:
            print(f"Found on page {page_num + 1}:\n{text}\n")
    else:
        print(f"No instances of '{search_term}' found.")

if __name__ == "__main__":
    pdf_path = '../data/test1.pdf'  # Replace with the path to your PDF file
    search_term = 'nguyên tử'  # Replace with the term you want to search for
    main(pdf_path, search_term)
