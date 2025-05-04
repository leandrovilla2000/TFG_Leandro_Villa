import os
from datetime import datetime
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from PIL import Image
import pytesseract
import speech_recognition as sr
import moviepy as mp
from utils import extract_metadata_from_file

def load_documents(directory_path):
    docs = []

    # Documents Loading
    pdfFiles = [f for f in os.listdir(directory_path) if f.endswith(".pdf")]
    docxFiles = [f for f in os.listdir(directory_path) if f.endswith(".docx")]
    txtFiles = [f for f in os.listdir(directory_path) if f.endswith(".txt")]
    imageFiles = [f for f in os.listdir(directory_path) if f.endswith((".png", ".jpg", ".jpeg"))]
    audioFiles = [f for f in os.listdir(directory_path) if f.endswith((".mp3", ".wav"))]
    videoFiles = [f for f in os.listdir(directory_path) if f.endswith((".mp4", ".avi"))]

    # PDF
    for pdf in pdfFiles:
        path = os.path.join(directory_path, pdf)
        loader = PyPDFLoader(path)
        loaded = loader.load()
        for doc in loaded:
            doc.metadata.update(extract_metadata_from_file(path))
            docs.append(doc)

    # DOCX
    for docx in docxFiles:
        path = os.path.join(directory_path, docx)
        loader = Docx2txtLoader(path)
        loaded = loader.load()
        for doc in loaded:
            doc.metadata.update(extract_metadata_from_file(path))
            docs.append(doc)

    # TXT
    for txt in txtFiles:
        path = os.path.join(directory_path, txt)
        loader = TextLoader(path)
        loaded = loader.load()
        for doc in loaded:
            doc.metadata.update(extract_metadata_from_file(path))
            docs.append(doc)

    # Images
    for img in imageFiles:
        path = os.path.join(directory_path, img)
        text = pytesseract.image_to_string(Image.open(path))
        docs.append(Document(page_content=text, metadata=extract_metadata_from_file(path)))

    # Audios
    recognizer = sr.Recognizer()
    for audio in audioFiles:
        path = os.path.join(directory_path, audio)
        with sr.AudioFile(path) as source:
            audioData = recognizer.record(source)
            text = recognizer.recognize_google(audioData)
            docs.append(Document(page_content=text, metadata=extract_metadata_from_file(path)))

    # Videos
    for video in videoFiles:
        path = os.path.join(directory_path, video)
        audio_path = path.rsplit(".", 1)[0] + "_temp.wav"
        mp.VideoFileClip(path).audio.write_audiofile(audio_path, verbose=False, logger=None)
        with sr.AudioFile(audio_path) as source:
            audioData = recognizer.record(source)
            text = recognizer.recognize_google(audioData)
            docs.append(Document(page_content=text, metadata=extract_metadata_from_file(path)))
        os.remove(audio_path)

    return docs