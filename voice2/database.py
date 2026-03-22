import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def create_vector_db():
    print("📄 Կարդում ենք final_bank_data.json ֆայլը...")
    try:
        with open("final_bank_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Սխալ: final_bank_data.json ֆայլը չի գտնվել:")
        return

    all_texts = []
    all_metadatas = []

    # 1. Սահմանում ենք splitter-ը մեկ անգամ (օպտիմալացված) [cite: 13, 28]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, 
        chunk_overlap=100
    )

    print("✂️ Տեքստը բաժանում ենք կտորների (Chunking)...")

    # 2. Տվյալների մշակում
    # Քո JSON-ի կառուցվածքը՝ { Bank: { Category: [ {text: ..., url: ...} ] } }
    for bank, categories in data.items():
        for category, items in categories.items():
            for item in items:
                text = item.get("text", "").strip()
                url = item.get("url", "N/A") # Ավելացրել ենք URL-ը metadata-ի համար 
                
                if text:
                    chunks = splitter.split_text(text)
                    for chunk in chunks:
                        all_texts.append(chunk)
                        all_metadatas.append({
                            "bank": bank,
                            "category": category,
                            "url": url
                        })

    print(f"✅ Ստացվեց {len(all_texts)} կտոր:")

    # 3. Ծածկագրում (Encoding) անվճար մոդելով [cite: 11, 19]
    print("🔢 Ստեղծում ենք embeddings (սա կարող է մի քանի րոպե տևել)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"} 
    )

    # 4. Պահպանում FAISS բազայում [cite: 2, 28]
    print("💾 Պահպանում ենք FAISS բազան...")
    db = FAISS.from_texts(all_texts, embeddings, metadatas=all_metadatas)
    db.save_local("bank_faiss_index")
    
    print("✨ Ավարտված է: Բազան պահպանված է 'bank_faiss_index/' թղթապանակում:")

if __name__ == "__main__":
    create_vector_db()