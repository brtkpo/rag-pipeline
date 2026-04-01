import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

def upload_file(uploaded_file):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    response = requests.post(f"{API_URL}/upload", files=files)
    response.raise_for_status()
    return response.json()

def get_files():
    response = requests.get(f"{API_URL}/files")
    response.raise_for_status()
    return response.json().get("files", [])

def delete_file(filename):
    response = requests.delete(f"{API_URL}/files/{filename}")
    response.raise_for_status()

def ask_question(question):
    response = requests.post(f"{API_URL}/chat", json={"question": question})
    response.raise_for_status()
    return response.json()["answer"]