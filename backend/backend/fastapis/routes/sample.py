from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import docx
import os
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router
router = APIRouter(
    prefix="/sample",
    tags=["Sample"]
)

# Load data and model
try:
    # Use a relative path or check if file exists
    file_path = r"C:\Users\mdyus\Downloads\monarch\abstractevent.csv"
    if not os.path.exists(file_path):
        print(f"Warning: File not found at {file_path}")
        # Create a dummy dataframe for testing
        df = pd.DataFrame({
            "abstract": ["Sample abstract 1", "Sample abstract 2"],
            "category": ["Category A", "Category B"]
        })
    else:
        df = pd.read_csv(file_path)
    
    abstracts = df["abstract"].astype(str).tolist()
    
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("Generating embeddings (only once)...")
    embeddings = model.encode(abstracts, show_progress_bar=True)
    
    print("Backend Ready 🚀")
    
except Exception as e:
    print(f"Error during initialization: {e}")
    # Create fallback dummy data
    df = pd.DataFrame({
        "abstract": ["Sample abstract 1", "Sample abstract 2"],
        "category": ["Category A", "Category B"]
    })
    abstracts = df["abstract"].astype(str).tolist()
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(abstracts)

# -----------------------------
# FILE PROCESSING FUNCTIONS
# -----------------------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + " "
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + " "
    return text

def extract_text(file, filename):
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file)
    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file format")

# -----------------------------
# SIMILARITY FUNCTION
# -----------------------------
def search_similar_patents(query_text, top_k=5):
    query_embedding = model.encode([query_text])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        score = float(similarities[idx])
        status = "⚠ Possible Duplicate" if score > 0.90 else "Unique"
        
        results.append({
            "abstract": df.iloc[idx]["abstract"],
            "category": df.iloc[idx].get("category", "N/A"),
            "similarity_score": f"{round(score * 100, 2)}%",
            "status": status
        })
    
    return results

# -----------------------------
# FUNCTION TO WRITE RESULTS TO TXT FILE
# -----------------------------
def save_results_to_file(results, uploaded_filename, query_text_preview=""):
    # Get user's Downloads folder
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Create a subfolder for patent results (optional)
    patent_folder = os.path.join(downloads_folder, "patent_results")
    if not os.path.exists(patent_folder):
        os.makedirs(patent_folder)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = "".join(c for c in uploaded_filename if c.isalnum() or c in "._- ")[:50]
    output_filename = f"patent_similarity_{safe_filename}_{timestamp}.txt"
    output_path = os.path.join(patent_folder, output_filename)
    
    # Write results to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("PATENT SIMILARITY SEARCH RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Uploaded File: {uploaded_filename}\n")
        f.write(f"Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Results saved to: {output_path}\n\n")
        
        if query_text_preview:
            f.write("Query Text Preview:\n")
            f.write("-" * 40 + "\n")
            f.write(query_text_preview[:500] + ("..." if len(query_text_preview) > 500 else "") + "\n\n")
        
        f.write("TOP MATCHING PATENTS\n")
        f.write("=" * 80 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"RESULT #{i}\n")
            f.write("-" * 40 + "\n")
            f.write(f"Similarity Score: {result['similarity_score']}\n")
            f.write(f"Status: {result['status']}\n")
            f.write(f"Category: {result['category']}\n")
            f.write(f"Abstract: {result['abstract'][:300]}...\n" if len(result['abstract']) > 300 else f"Abstract: {result['abstract']}\n")
            f.write("\n" + "=" * 40 + "\n\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    # Also save a log file with just the basic info (optional)
    log_path = os.path.join(patent_folder, "search_log.txt")
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{timestamp} - {uploaded_filename} - Results saved to: {output_filename}\n")
    
    return output_path

# -----------------------------
# ROUTES
# -----------------------------
@router.get("/")
def home():
    return {"message": "Patent Similarity Backend Running 🚀"}

@router.post("/upload-search")
async def upload_and_search(file: UploadFile = File(...)):
    print('yusuff bhai')
    # Check if file exists (is not None and has content)
    if file is None or file.filename is None or file.filename == "":
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "File not found or no file uploaded"}
        )
    
    try:
        print(f'Processing file: {file.filename}')
        
        # Check if file has content
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # Reset file pointer to beginning
        
        if file_size == 0:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "File is empty"}
            )
        
        # Extract text from uploaded file
        text = extract_text(file.file, file.filename)
        
        if not text.strip():
            error_msg = "File contains no readable text"
            # Save error to file (silently)
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            patent_folder = os.path.join(downloads_folder, "patent_results")
            if not os.path.exists(patent_folder):
                os.makedirs(patent_folder)
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_filename = f"error_{timestamp}.txt"
            error_path = os.path.join(patent_folder, error_filename)
            
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(f"ERROR: {error_msg}\n")
                f.write(f"File: {file.filename}\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": error_msg}
            )
        
        # Perform similarity search
        results = search_similar_patents(text)
        
        # Save results to file in local Downloads folder
        save_results_to_file(
            results, 
            file.filename, 
            query_text_preview=text[:200]
        )
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "File processed successfully"}
        )
    
    except ValueError as e:
        # Handle unsupported file format
        if "Unsupported file format" in str(e):
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "File not found or unsupported format"}
            )
        else:
            # Save error to file silently
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            patent_folder = os.path.join(downloads_folder, "patent_results")
            if not os.path.exists(patent_folder):
                os.makedirs(patent_folder)
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_filename = f"error_{timestamp}.txt"
            error_path = os.path.join(patent_folder, error_filename)
            
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(f"ERROR: {str(e)}\n")
                f.write(f"File: {file.filename}\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "File not found or invalid"}
            )
    
    except Exception as e:
        # Save error to file silently
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        patent_folder = os.path.join(downloads_folder, "patent_results")
        if not os.path.exists(patent_folder):
            os.makedirs(patent_folder)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_filename = f"error_{timestamp}.txt"
        error_path = os.path.join(patent_folder, error_filename)
        
        with open(error_path, 'w', encoding='utf-8') as f:
            f.write(f"ERROR: {str(e)}\n")
            f.write(f"File: {file.filename}\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "File not found or processing error"}
        )

# Include the router in the app
app.include_router(router)

# Add a root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Patent Similarity API"}