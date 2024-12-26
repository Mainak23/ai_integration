import os
import cv2
import numpy as np
from wand.image import Image
import pytesseract
from PyPDF2 import PdfReader, PdfWriter,PdfMerger
from nltk.util import ngrams
import shutil
import time
import chromadb
import datetime
from cryptography.fernet import Fernet
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Check if the Tesseract path is set correctly (optional)
if not os.path.isfile(pytesseract.pytesseract.tesseract_cmd):
    raise FileNotFoundError(f"Tesseract executable not found at {pytesseract.pytesseract.tesseract_cmd}")

import logging
from logging.handlers import RotatingFileHandler


# Create a custom logger
logger = logging.getLogger("FileChangeLogger")
logger.setLevel(logging.INFO)

# Define format for logging (old name, new name, and creation time)
file_format = logging.Formatter('%(asctime)s - Old Name: %(old_name)s - New Name: %(new_name)s - Created At: %(creation_time)s')

# Set up a rotating file handler
rotating_handler = RotatingFileHandler('app.log', maxBytes=2000, backupCount=5)
rotating_handler.setFormatter(file_format)
logger.addHandler(rotating_handler)

# Log function that includes custom fields
def log_file_change(old_name, new_name,time):
    # Define extra information to be passed to logger
    extra = {
        'old_name': old_name,
        'new_name': new_name,
        'creation_time': time
    }
    # Log the change
    logger.info("File name changed", extra=extra)

# Example usage

class DatabaseHandler:
    """Handles PDF splitting and conversion to images."""
    primary_folder_path = os.path.join(os.getcwd(), "input_storage_minde", "file_primary_storage_minde")
    secondary_folder_path = os.path.join(os.getcwd(), "input_storage_minde", "file_secondary_storage_minde")

    os.makedirs(primary_folder_path, exist_ok=True)
    os.makedirs(secondary_folder_path, exist_ok=True)

    @classmethod
    def split_pdf(cls, pdf_path):
        """Split a PDF into individual pages and store them."""
        with open(pdf_path, 'rb') as fo:
            pdf_reader = PdfReader(fo)
            if len(pdf_reader.pages) > 0:
                for page_number, page in enumerate(pdf_reader.pages):
                    pdf_writer = PdfWriter()
                    pdf_writer.add_page(page)
                    output_file_path = f'{cls.primary_folder_path}/page_{page_number + 1}.pdf'
                    with open(output_file_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
            else:
                shutil.move(pdf_path, cls.primary_folder_path)

        return [os.path.join(cls.primary_folder_path, file) 
                for file in os.listdir(cls.primary_folder_path) if file.endswith('.pdf')]
    
    @classmethod
    def convert_pdf_to_image(cls, pdf_path):
        """Convert a PDF to PNG image."""
        output_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        png_path = os.path.join(cls.secondary_folder_path, f'{output_filename}.png')
        with Image(filename=pdf_path, resolution=600) as img:
            with img.convert('png') as converted:
                converted.compression_quality = 99
                converted.save(filename=png_path)
        return png_path
    @classmethod
    def convert(cls,pdf_path):
        output_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        png_path = os.path.join(cls.secondary_folder_path,output_filename + '.png')
        ocr_path = os.path.join(cls.secondary_folder_path,output_filename + '-ocr.pdf')
        with Image(filename=pdf_path, resolution=300) as img:
            with img.convert('png') as converted:
                converted.compression_quality = 99
                converted.save(filename=png_path)
        extracted_text = pytesseract.image_to_pdf_or_hocr(png_path, lang='eng', config='--psm 1')
        with open(ocr_path, 'wb') as ocr_file:
            ocr_file.write(extracted_text)
            print('OCR conversion completed for: ' + pdf_path)
                # Delete temporary PNG file
        if os.path.exists(png_path):
            os.remove(png_path)
            print('Temporary PNG file deleted.')
            return ocr_path

class TextRetrieval:
    @staticmethod
    def extract_text_image(image_path):
        """Extract text from an image using OCR."""
        return pytesseract.image_to_string(image_path).lower()
    @staticmethod
    def extract_text_pdf(file_path):
        reader = PdfReader(file_path)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
        return text

def convert(cls,pdf_path):
    output_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    png_path = os.path.join(cls.secondary_folder_path,output_filename + '.png')
    ocr_path = os.path.join(cls.secondary_folder_path,output_filename + '-ocr.pdf')
    with Image(filename=pdf_path, resolution=300) as img:
        with img.convert('png') as converted:
            converted.compression_quality = 99
            converted.save(filename=png_path)
    extracted_text = pytesseract.image_to_pdf_or_hocr(png_path, lang='eng', config='--psm 1')
    with open(ocr_path, 'wb') as ocr_file:
        ocr_file.write(extracted_text)
        print('OCR conversion completed for: ' + pdf_path)
            # Delete temporary PNG file
    if os.path.exists(png_path):
        os.remove(png_path)
        print('Temporary PNG file deleted.')
        return ocr_path

def delete_files_in_directory(directory):
    """Delete all files in a directory."""
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                os.remove(os.path.join(root, file))
    except Exception as e:
        print(f"Error deleting files: {e}")

def get_files_sorted_by_creation(directory:str) -> str:
    """Return files sorted by creation time."""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return sorted(files, key=os.path.getctime)

def preprocess_file(file_path:str) -> str:
    db_path = os.path.join(os.getcwd(), "input_storage_minde", "data_base")
    out_put_path=os.path.join(os.getcwd(),"input_storage_minde", "out_put_folder")
    folder_pdf=os.path.join(os.getcwd(),"input_storage_minde", "file_primary_storage_minde")
    folder_pdf_1=os.path.join(os.getcwd(), "input_storage_minde", "file_secondary_storage_minde")
    collection_name="my_collection"

    os.makedirs(out_put_path,exist_ok=True)
    os.makedirs(db_path, exist_ok=True)

    key = Fernet.generate_key()
    cipher = Fernet(key)
    client = chromadb.PersistentClient(path=db_path)

    pdf_process=DatabaseHandler()
    text_retrival=TextRetrieval()

    collection = client.get_or_create_collection(name=collection_name)
    path_pdf=file_path
    path_modefy=path_pdf.split("\\")[-1]
    print(path_modefy)
    merger = PdfMerger()
    split_pdf=pdf_process.split_pdf(path_pdf)
    split_pdf_create=get_files_sorted_by_creation(folder_pdf)
    time.sleep(0.5)
    convert_png=[]
    for path in split_pdf_create:
        #convert_png.append(pdf_process.convert_pdf_to_image(path))
        convert_png.append(pdf_process.convert(path))
        time.sleep(0.5)
    #convert_png=[pdf_process.convert_pdf_to_image(path) for path in split_pdf_create]

    pdf_page_map={}
    text_map = {}
    for index,value in enumerate(split_pdf_create):
        pdf_page_map[value.split("\\")[-1]] = value 
    for index,value in enumerate(convert_png):
        text_map[value.split("\\")[-1].replace(".png", ".pdf")] = text_retrival.extract_text_pdf(value)

    for key,value in text_map.items():
        collection.add(
            documents=value,
            ids=key
            )
        print(f"Added documents to the collection.")

    time.sleep(0.5)
    results = collection.query(query_texts=[" "],where_document={"$contains": "total"})["ids"][0]
    print(results)
    client.delete_collection(collection_name)
    keys_position={result: idx for idx, result in enumerate(pdf_page_map.keys())}
    subset_dict = {key: keys_position[key] for key in results if key in keys_position.keys()}
    print(subset_dict)
    sorted_pages = list({k: v for k, v in sorted(subset_dict.items(), key=lambda item: item[1])}.keys())
    start_key=next(iter(pdf_page_map))
    end_key=sorted_pages[0]
    truncated_data = list({k: v for k, v in pdf_page_map.items() if k >= start_key and k <= end_key}.keys())
    print(truncated_data)
    subset_page = list({key: pdf_page_map[key] for key in truncated_data if key in pdf_page_map}.values())
    #print(subset_page)
    ####need to change the funtion subset_page####
    #C:\Users\USER\Desktop\paid_ocr\input_storage_minde\file_primary_storage_minde\page_1.pdf
    output_file = os.path.join(out_put_path,f"process_{path_modefy}.pdf")
    [merger.append(pdf) for pdf in subset_page]
    merger.write(output_file)
    merger.close()
    creation_time = os.path.getctime(output_file)
    creation_time_readable = datetime.datetime.fromtimestamp(creation_time) 
    new_name=f"{path_modefy}_{creation_time_readable}" .encode()
    start_index = 20
    encrypted_data = cipher.encrypt(new_name)[start_index:start_index + 4]
    output_file_1 = os.path.join(out_put_path,f"{encrypted_data}.pdf")
    os.rename(output_file, output_file_1)
    delete_files_in_directory(folder_pdf)
    delete_files_in_directory(folder_pdf_1)
    #print(output_file_1)
    pdf_page_count=len(list(keys_position.keys()))
    log_file_change(output_file, output_file_1,creation_time_readable)
    page_count_actions=len(subset_page)
    
    return output_file_1,pdf_page_count,page_count_actions




image_path=r"C:\Users\USER\Desktop\paid_ocr\roni_pdf"
path_=os.listdir(image_path)
image_path_1=[os.path.join(image_path,path) for path in path_]

file_name = "extratc_text.txt"

# Write to the file
with open(file_name, "w") as file:
    for path in image_path_1:
        file.write(path + "\n")  # Write image path followed by a newline
        file.write("#########\n")  # Separator with a newline
        try:
            # Extract text from image and write it to the file
            extracted_text = pytesseract.image_to_string(path)
            file.write(extracted_text + "\n")  # Write extracted text followed by a newline
        except Exception as e:
            file.write(f"Error processing {path}: {e}\n") 


print(pytesseract.image_to_string(image_path_1[1]))
