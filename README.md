# 🤖 MR Analyst — AI-Powered Data Analyst

> An AI-powered data analysis platform that allows users to upload datasets and documents, ask questions in natural language, retrieve relevant information, and generate SQL queries automatically.

---

## 🚀 Live Demo

🔗 **Demo:** [Add your Streamlit demo link here]([DEMO_LINK](https://mr-analyst.streamlit.app/))

---

## 📸 Screenshots

### 🏠 Main Interface

![MR Analyst Interface](screenshots/home.png)

### 📂 File Upload

![File Upload](screenshots/upload.png)

### 🔎 AI Data Analysis

![AI Analysis](screenshots/analysis.png)

### 🤖 AI Response

![AI Response](screenshots/ai-response.png)

### 🧠 One-Click AI Analyst

![One-Click AI Analyst](screenshots/one-click.png)

### 🗄️ SQL Generator

![SQL Generator](screenshots/sql-generator.png)

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
