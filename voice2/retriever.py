import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

def get_bank_context(query):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    db = FAISS.load_local("bank_faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    # Վերցնում ենք մի քիչ ավելի շատ արդյունք (օրինակ 6), որպեսզի հետո զտենք
    docs = db.similarity_search(query, k=6)
    
    context_parts = []
    seen_content = set() # Կրկնությունները բռնելու համար

    for doc in docs:
        content = doc.page_content.strip()
        # Եթե այս տեքստը արդեն տեսել ենք, բաց ենք թողնում
        if content not in seen_content:
            url = doc.metadata.get("url", "Աղբյուրը նշված չէ")
            context_parts.append(f"{content}\n(Աղբյուր: {url})")
            seen_content.add(content)
        
        # Երբ ունենք 3 տարբեր արդյունք, կանգնում ենք
        if len(context_parts) == 3:
            break
            
    return "\n\n---\n\n".join(context_parts)

# Փորձարկման համար (կարող ես ջնջել հետո)
if __name__ == "__main__":
    test_query = "Ի՞նչ վարկեր ունեք"
    result = get_bank_context(test_query)
    print("🔎 Բազայի գտած տվյալները:\n", result)