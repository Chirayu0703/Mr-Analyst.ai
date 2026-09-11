import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import pandas as pd
import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Connect to Groq
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
# Embedding model
@st.cache_resource
def load_embedding_model():

    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

embedding_model = load_embedding_model()


# ChromaDB
chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="mr_analyst"
)




# -----------------------------
# Page Title
# -----------------------------

st.title("MR Analyst")

st.write("Welcome to India's best AI Platform for Analysts")


# -----------------------------
# File Upload
# -----------------------------

uploaded_file = st.file_uploader(
    "Kindly Upload your file to begin",
    type=["csv", "xlsx", "xls", "pdf", "docx", "txt"],
    accept_multiple_files=True
)

if st.button("Upload Now"):
    if uploaded_file:
        st.session_state["uploaded_file"] = uploaded_file
        st.success(f"{len(uploaded_file)} file(s) uploaded successfully!")

    else:
        st.warning("Please select at least one file.")

# pdf extraction function
def extract_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

# CSV extraction function
def extract_csv(file):

    df = pd.read_csv(file)

    return df.to_string(index=False)

# excel extraction frunction
def extract_excel(file):

    df = pd.read_excel(file)

    return df.to_string(index=False)

def extract_file(file):

    if file.name.endswith(".csv"):
        return extract_csv(file)

    elif file.name.endswith(".pdf"):
        return extract_pdf(file)

    elif file.name.endswith(".xlsx") or file.name.endswith(".xls"):
        return extract_excel(file)
    
    else:
        raise ValueError("Unsupported file type")

# -----------------------------
# Extract Data
# -----------------------------

if st.button("Extract Data"):

    if "uploaded_file" not in st.session_state:

        st.warning("Please upload files first.")

    else:

        extracted_data = []

        for file in st.session_state["uploaded_file"]:

            content = extract_file(file)

            extracted_data.append({
                "filename": file.name,
                "content": content
            })

        st.session_state["extracted_data"] = extracted_data

        st.success(
            f"Data extracted from {len(extracted_data)} file(s) successfully!"
        )

def chunk_text(text, chunk_size=1000, overlap=100):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_embeddings(extracted_data):

    all_chunks = []
    all_embeddings = []

    for document in extracted_data:

        filename = document["filename"]
        content = document["content"]

        # Step 1: Create chunks
        chunks = chunk_text(content)

        # Step 2: Convert chunks into embeddings
        embeddings = embedding_model.encode(chunks)

        # Store chunks and embeddings
        for chunk, embedding in zip(chunks, embeddings):

            all_chunks.append({
                "filename": filename,
                "content": chunk
            })

            all_embeddings.append(embedding)

    return all_chunks, all_embeddings

 # store in chromaDB
def store_in_chromadb(chunks, embeddings):

    batch_size = 5000

    total_documents = len(chunks)

    for start in range(0, total_documents, batch_size):

        end = min(
            start + batch_size,
            total_documents
        )

        batch_chunks = chunks[start:end]
        batch_embeddings = embeddings[start:end]

        documents = []
        metadatas = []
        ids = []

        for index, (chunk, embedding) in enumerate(
            zip(batch_chunks, batch_embeddings),
            start=start
        ):

            documents.append(
                chunk["content"]
            )

            metadatas.append({
                "filename": chunk["filename"],
                "chunk_index": index
            })

            ids.append(
                f"{chunk['filename']}_{index}"
            )

        collection.upsert(
            documents=documents,
            embeddings=[
                embedding.tolist()
                for embedding in batch_embeddings
            ],
            metadatas=metadatas,
            ids=ids
        )

    return total_documents

# -----------------------------
# Run Complete AI Pipeline
# -----------------------------

def run_complete_ai_pipeline(files, question):

    # ==========================================
    # STEP 1: EXTRACT DATA
    # ==========================================

    extracted_data = []

    for file in files:

        file.seek(0)

        content = extract_file(file)

        extracted_data.append({
            "filename": file.name,
            "content": content
        })

    # ==========================================
    # STEP 2: CREATE CHUNKS
    # ==========================================

    chunks, embeddings = create_embeddings(
        extracted_data
    )

    # ==========================================
    # STEP 3: STORE IN CHROMADB
    # ==========================================

    total_chunks = store_in_chromadb(
        chunks,
        embeddings
    )

    # ==========================================
    # STEP 4: RETRIEVE RELEVANT CHUNKS
    # ==========================================

    results = retrieve_top_chunks(
        question,
        top_k=3
    )

    retrieved_chunks = results["documents"][0]

    # ==========================================
    # STEP 5: CREATE CONTEXT
    # ==========================================

    context = "\n\n".join(
        retrieved_chunks
    )

    # ==========================================
    # STEP 6: ASK GROQ AI
    # ==========================================

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",

                "content": """
You are MR Analyst, an AI assistant for data analysts.

Answer the user's question using only the
provided context.

Rules:

1. Use the uploaded data as the primary source.
2. Do not invent information.
3. If the answer cannot be found in the
   uploaded data, clearly say so.
4. Give a clear and concise answer.
5. When useful, provide calculations,
   comparisons, trends, or bullet points.
6. If multiple files were uploaded, use
   information from all relevant files.
"""
            },

            {
                "role": "user",

                "content": f"""
Context from uploaded files:

{context}

User Question:

{question}
"""
            }
        ],

        temperature=0.2
    )

    answer = response.choices[0].message.content

    return {
        "extracted_data": extracted_data,
        "chunks": chunks,
        "embeddings": embeddings,
        "total_chunks": total_chunks,
        "retrieved_chunks": retrieved_chunks,
        "answer": answer
    }

if st.button("Create Chunks & Embeddings"):

    if "extracted_data" not in st.session_state:

        st.warning("Please extract the data first.")

    else:

        chunks, embeddings = create_embeddings(
            st.session_state["extracted_data"]
        )

        st.session_state["chunks"] = chunks
        st.session_state["embeddings"] = embeddings

        st.success(
            f"Created {len(chunks)} chunks and embeddings successfully!"
        )

# -----------------------------
# Store in ChromaDB
# -----------------------------

if st.button("Store in ChromaDB"):

    if "chunks" not in st.session_state:

        st.warning(
            "Please create chunks and embeddings first."
        )

    else:

        total_chunks = store_in_chromadb(
            st.session_state["chunks"],
            st.session_state["embeddings"]
        )

        st.success(
            f"{total_chunks} chunks stored in ChromaDB!"
        )
# -----------------------------
# Ask AI
# -----------------------------

st.title("Now Ask AI about your file")

question = st.text_input(
    "Ask your question here"
)



# -----------------------------
# Ask AI Button
# -----------------------------

def retrieve_top_chunks(question, top_k=3):

    # Convert question into embedding
    question_embedding = embedding_model.encode(
        question
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    return results

# -----------------------------
# Test Retrieval
# -----------------------------

if st.button("Retrieve Top 3 Chunks"):

    if collection.count() == 0:

        st.warning(
            "ChromaDB is empty. Please store your chunks first."
        )

    elif question.strip() == "":

        st.warning(
            "Please enter a question first."
        )

    else:

        results = retrieve_top_chunks(question, top_k=3)

        st.subheader("Top 3 Retrieved Chunks")

        for i, chunk in enumerate(
            results["documents"][0]
        ):

            st.write(f"### Chunk {i + 1}")

            st.write(chunk)

            st.write(
                "Source:",
                results["metadatas"][0][i]["filename"]
            )

# -----------------------------
# Ask AI Button
# -----------------------------

if st.button("Ask AI"):

    if question.strip() == "":

        st.warning("Please enter a question first.")

    elif collection.count() == 0:

        st.warning(
            "Please upload, extract and store your files first."
        )

    else:

        # -----------------------------
        # Step 1: Retrieve top 3 chunks
        # -----------------------------

        results = retrieve_top_chunks(
            question,
            top_k=3
        )

        retrieved_chunks = results["documents"][0]

        # -----------------------------
        # Step 2: Create context
        # -----------------------------

        context = "\n\n".join(
            retrieved_chunks
        )

        # -----------------------------
        # Step 3: Show retrieved data
        # -----------------------------

        st.subheader("Retrieved Context")

        for i, chunk in enumerate(retrieved_chunks):

            st.write(f"### Chunk {i + 1}")
            st.write(chunk)

        # -----------------------------
        # Step 4: Call Groq
        # -----------------------------

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[

                {
                    "role": "system",
                    "content": """
                    You are MR Analyst, an AI assistant for data analysts.

                    Answer the user's question using the provided context.

                    If the answer cannot be found in the context,
                    clearly say that the information is not available
                    in the uploaded documents.

                    Do not make up information.
                    """
                },

                {
                    "role": "user",
                    "content": f"""
                    Context from uploaded documents:

                    {context}

                    User Question:

                    {question}
                    """
                }
            ],

            temperature=0.2
        )

        # -----------------------------
        # Step 5: Display answer
        # -----------------------------

        answer = response.choices[0].message.content

        st.subheader("AI Response")

        st.markdown(answer)


# -----------------------------
# SQL Generator
# -----------------------------

def generate_sql_from_file(file, question):

    # Reset file pointer
    file.seek(0)

    # Read CSV
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)

    elif file.name.endswith(".xlsx") or file.name.endswith(".xls"):
        df = pd.read_excel(file)

    else:
        raise ValueError("SQL Generator supports CSV, XLSX and XLS files.")

    # Get column information
    schema = df.dtypes.astype(str).to_dict()

    # Get sample rows
    sample_data = df.head(5).to_dict(orient="records")

    # Create schema text
    schema_text = "\n".join(
        [
            f"{column}: {dtype}"
            for column, dtype in schema.items()
        ]
    )

    # Call Groq
    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",
                "content": """
You are MR Analyst, an expert SQL developer.

Your task is to generate SQL queries for MySQL 8.0
based strictly on the provided CSV dataset schema
and sample data.

Rules:

1. Generate ONLY MySQL-compatible SQL.
2. Use only columns that actually exist in the dataset.
3. Do not invent column names.
4. Infer the appropriate table name from the CSV filename.
5. Use correct MySQL syntax.
6. Make the SQL directly runnable in MySQL Workbench.
7. Do not use PostgreSQL, SQL Server, SQLite, or other SQL dialects.
8. If the user's request cannot be answered using the available
   columns, clearly explain what information is missing.
9. Return the SQL inside a single ```sql code block.
10. After the SQL, provide a short explanation of what the query does.
11. Do not generate Python or pandas code.
12. Do not assume columns that are not present in the dataset.

The dataset schema and sample data will be provided by the user.
"""
            },

            {
                "role": "user",
                "content": f"""

Filename:
{file.name}

Dataset Schema:

{schema_text}

Sample Data:

{sample_data}

User's SQL Requirement:

{question}
"""
            }

        ],

        temperature=0.1
    )

    return response.choices[0].message.content

# -----------------------------
# SQL Generator
# -----------------------------

if st.button("Generate SQL Code"):

    # Check if files were uploaded
    if "uploaded_file" not in st.session_state:

        st.warning(
            "Please upload a CSV, XLSX or XLS file first."
        )

    else:

        # Find CSV files
        sql_files = [
            file
            for file in st.session_state["uploaded_file"]
            if file.name.lower().endswith((".csv", ".xlsx", ".xls"))
        ]

        # No CSV found
        if len(sql_files) == 0:

            st.warning(
                "SQL Generator supports CSV, XLSX and XLS files."
            )

        # More than one CSV
        elif len(sql_files) > 1:

            st.warning(
                "Please upload only one CSV, XLSX or XLS file "
                "when using the SQL Generator."
            )

        # Exactly one CSV
        else:

            if question.strip() == "":

                st.warning(
                    "Please enter your SQL requirement "
                    "in the question box first."
                )

            else:

                data_file = sql_files[0]

                sql_code = generate_sql_from_file(
                    data_file,
                    question
                )

                st.subheader("Generated MySQL Code")

                st.markdown(sql_code)

# =====================================================
# ONE-CLICK AI ANALYST
# =====================================================

st.markdown("---")

st.subheader("🚀 One-Click AI Analyst")

st.write(
    "Automatically upload, extract, chunk, embed, "
    "store, retrieve and ask AI in one click."
)

# Bottom-right button
col1, col2, col3 = st.columns([5, 2, 1])

with col3:

    run_all = st.button(
        "Ask AI",
        key="one_click_ai",
        use_container_width=True
    )


if run_all:

    # -----------------------------------------
    # Check uploaded files
    # -----------------------------------------

    if "uploaded_file" not in st.session_state:

        st.warning(
            "Please upload at least one file first."
        )

    # -----------------------------------------
    # Check question
    # -----------------------------------------

    elif question.strip() == "":

        st.warning(
            "Please enter your question first."
        )

    else:

        try:

            # =================================
            # Progress
            # =================================

            progress = st.progress(0)

            status = st.empty()


            # =================================
            # STEP 1
            # =================================

            status.info(
                "📄 Step 1/5 — Extracting data..."
            )

            extracted_data = []

            for file in st.session_state["uploaded_file"]:

                file.seek(0)

                content = extract_file(file)

                extracted_data.append({
                    "filename": file.name,
                    "content": content
                })

            st.session_state["extracted_data"] = extracted_data

            progress.progress(20)


            # =================================
            # STEP 2
            # =================================

            status.info(
                "✂️ Step 2/5 — Creating chunks and embeddings..."
            )

            chunks, embeddings = create_embeddings(
                extracted_data
            )

            st.session_state["chunks"] = chunks

            st.session_state["embeddings"] = embeddings

            progress.progress(40)


            # =================================
            # STEP 3
            # =================================

            status.info(
                "🧠 Step 3/5 — Storing knowledge in ChromaDB..."
            )

            total_chunks = store_in_chromadb(
                chunks,
                embeddings
            )

            progress.progress(60)


            # =================================
            # STEP 4
            # =================================

            status.info(
                "🔎 Step 4/5 — Searching relevant information..."
            )

            results = retrieve_top_chunks(
                question,
                top_k=3
            )

            retrieved_chunks = results["documents"][0]

            context = "\n\n".join(
                retrieved_chunks
            )

            progress.progress(80)


            # =================================
            # STEP 5
            # =================================

            status.info(
                "🤖 Step 5/5 — MR Analyst is thinking..."
            )

            response = client.chat.completions.create(

                model="openai/gpt-oss-20b",

                messages=[

                    {
                        "role": "system",

                        "content": """
You are MR Analyst, an AI assistant for
data analysts.

Answer the user's question using only the
provided context.

Rules:

1. Use the uploaded data as the primary source.
2. Do not make up information.
3. If the answer is not available in the
   uploaded data, clearly say so.
4. Give a clear and useful answer.
5. Use bullet points when appropriate.
6. Perform calculations when the context
   contains sufficient information.
7. Compare values when useful.
"""
                    },

                    {
                        "role": "user",

                        "content": f"""
Uploaded file context:

{context}

User question:

{question}
"""
                    }

                ],

                temperature=0.2
            )

            answer = response.choices[0].message.content

            progress.progress(100)

            status.success(
                "✅ Complete! MR Analyst finished the analysis."
            )


            # =================================
            # SHOW PIPELINE SUMMARY
            # =================================

            st.success(
                f"Processed "
                f"{len(extracted_data)} file(s), "
                f"created {len(chunks)} chunks."
            )


            # =================================
            # SHOW AI ANSWER
            # =================================

            st.markdown("---")

            st.subheader(
                "🤖 MR Analyst Answer"
            )

            st.markdown(answer)


            # =================================
            # SHOW SOURCES
            # =================================

            st.markdown("---")

            st.subheader(
                "📚 Sources Used"
            )

            for i, chunk in enumerate(
                retrieved_chunks
            ):

                st.write(
                    f"### Source {i + 1}"
                )

                st.write(chunk)


                # Get source filename
                try:

                    source_filename = results[
                        "metadatas"
                    ][0][i]["filename"]

                    st.caption(
                        f"Source: {source_filename}"
                    )

                except:

                    pass


        except Exception as e:

            st.error(
                f"❌ Something went wrong: {str(e)}"
            )