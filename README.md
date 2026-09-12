# 🤖 MR Analyst — AI-Powered Data Analyst

> An AI-powered data analysis platform that allows users to upload datasets and documents, ask questions in natural language, retrieve relevant information, and generate SQL queries automatically.

---

## 🚀 Live Demo

🔗 **Demo:** [mr-analyst](https://mr-analyst.streamlit.app/)

---

## 📸 Screenshots

### 🏠 Main Interface

<img width="1358" height="875" alt="MR Analyst Interface" src="https://github.com/user-attachments/assets/3f6290c1-fe2f-45f4-975f-276d1098d9f6" />
<img width="1277" height="475" alt="Screenshot 2026-09-12 132757" src="https://github.com/user-attachments/assets/b5224835-5c87-475c-bcd1-33787f9cf8ca" />




### 📂 File Upload

<img width="1302" height="303" alt="Screenshot 2026-09-12 133257" src="https://github.com/user-attachments/assets/4099a1f0-9c11-4fac-862f-ce89e3297531" />


### 🔎 AI Embedding Process

<img width="1318" height="532" alt="Screenshot 2026-09-12 133436" src="https://github.com/user-attachments/assets/178d428c-c8da-4806-b19c-5ff74db49ed2" />

### 🔎 Top 3 Retrieved Chunks

<img width="1310" height="355" alt="Screenshot 2026-09-12 133838" src="https://github.com/user-attachments/assets/3e9763fe-a8e1-4160-9a03-c7d3cf0af7d1" />
<img width="1287" height="882" alt="Screenshot 2026-09-12 133945" src="https://github.com/user-attachments/assets/b0091c2a-5564-48aa-a316-e9efcc06ba13" />

### 🤖 AI Response

<img width="1318" height="455" alt="Screenshot 2026-09-12 140918" src="https://github.com/user-attachments/assets/0e1ed640-6de4-499b-9b49-6428671835a0" />

### 🗄️ SQL Generator

<img width="1302" height="692" alt="Screenshot 2026-09-12 141446" src="https://github.com/user-attachments/assets/f252bb94-6410-462a-a649-703e3b7a036b" />


### 🧠 One-Click AI Analyst

<img width="1297" height="853" alt="Screenshot 2026-09-12 141215" src="https://github.com/user-attachments/assets/9ca1d89c-789c-4657-856f-6af82de43b53" />

---

# 📌 About The Project

**MR Analyst** is an AI-powered platform designed to help data analysts interact with their data using natural language.

Instead of manually searching through large datasets, documents, or writing complex SQL queries, users can upload their files and ask questions directly.

The application processes uploaded data, creates semantic embeddings, stores them in a vector database, retrieves the most relevant information, and uses an AI model to generate a useful response.

The platform also includes a dedicated **SQL Generator** that converts natural-language requirements into **MySQL 8.0 compatible SQL queries**.

---

# ✨ Features

## 📂 Multi-Format File Upload

MR Analyst supports:

- CSV
- XLSX
- XLS
- PDF
- DOCX
- TXT

Users can upload multiple files and analyze information from relevant documents.

---

## 🔍 AI-Powered Data Retrieval

Uploaded content is divided into smaller chunks and converted into vector embeddings using:

```text
sentence-transformers/all-MiniLM-L6-v2
