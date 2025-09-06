# Install required libraries
!pip install transformers torch datasets llama-index-core llama-index-embeddings-huggingface llama-index-vector-stores-faiss llama-index-readers-file faiss-cpu sentence-transformers huggingface_hub streamlit pyngrok bitsandbytes accelerate -q

# Import libraries
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from datasets import load_dataset
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
import os
from huggingface_hub import login
import streamlit as st
from pyngrok import ngrok

# Step 1: Log in to Hugging Face
hf_token = "hf_HxMrjShCngjwGxxxxxxxxxxxxxxxx"
login(hf_token)

# Step 2: Load the Dataset
ds = load_dataset("codeparrot/apps", "all", split="train")
print(f"Dataset loaded with {len(ds)} examples")
print("Dataset features:", ds.features)


# Step 3: Prepare Knowledge Base for Retrieval
os.makedirs("knowledge_base", exist_ok=True)
for i, example in enumerate(ds.select(range(500))):
    try:
        solution = example['solutions'][0] if example['solutions'] else "No solution available"
        with open(f"knowledge_base/doc_{i}.txt", "w", encoding="utf-8") as f:
            f.write(f"### Problem\n{example['question']}\n\n### Solution\n{solution}")
    except Exception as e:
        print(f"Error writing doc_{i}.txt: {e}")

try:
    documents = SimpleDirectoryReader("knowledge_base").load_data()
    print(f"Loaded {len(documents)} documents")
except Exception as e:
    print(f"Error loading documents: {e}")
    raise

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.embed_model = embed_model

d = 384
faiss_index = faiss.IndexFlatL2(d)
vector_store = FaissVectorStore(faiss_index=faiss_index)
index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)
print("Knowledge base indexed successfully")


# Step 4: Load Pre-trained LLaMA 3.2 Model from Hugging Face with 4-bit Quantization
model_name = "meta-llama/Llama-3.2-3B-Instruct"
quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quant_config,
    device_map="auto"
)
print(f"Model loaded on {torch.cuda.current_device()}")

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# Step 5: Define RAG Function
def generate_solution_with_rag(problem, top_k=1):
    retriever = index.as_retriever(similarity_top_k=top_k)
    retrieved_nodes = retriever.retrieve(problem)
    context = retrieved_nodes[0].text if retrieved_nodes else "No relevant context found."
    
    prompt = f"Given the following competitive programming problem:\n\n{problem}\n\nRelevant context:\n{context}\n\nGenerate a solution in Python:"
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    
    solution = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return solution


# Step 6: Create Streamlit App
with open("app.py", "w") as f:
    f.write('''
import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
import os

# Load model and index
model_name = "meta-llama/Llama-3.2-3B-Instruct"
quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant_config, device_map="auto")
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

documents = SimpleDirectoryReader("knowledge_base").load_data()
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.embed_model = embed_model
d = 384
faiss_index = faiss.IndexFlatL2(d)
vector_store = FaissVectorStore(faiss_index=faiss_index)
index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)

def generate_solution_with_rag(problem, top_k=1):
    retriever = index.as_retriever(similarity_top_k=top_k)
    retrieved_nodes = retriever.retrieve(problem)
    context = retrieved_nodes[0].text if retrieved_nodes else "No relevant context found."
    prompt = f"Given the following competitive programming problem:\\n\\n{problem}\\n\\nRelevant context:\\n{context}\\n\\nGenerate a solution in Python:"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=300, temperature=0.7, top_p=0.9, do_sample=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

st.title("Competitive Programming Solver with RAG")
st.write("Enter a competitive programming problem below to get a Python solution.")
problem = st.text_area("Problem Statement", "Given an array of integers, find the maximum sum subarray.")
if st.button("Generate Solution"):
    with st.spinner("Generating solution..."):
        response = generate_solution_with_rag(problem)
        st.subheader("Generated Solution:")
        st.code(response, language="python")
        solution_start = response.find("Solution:")
        if solution_start != -1:
            st.subheader("Extracted Solution Code:")
            st.code(response[solution_start:], language="python")
''')


# Step 7: Set up ngrok and run Streamlit
ngrok.set_auth_token("2u1dTdyOzldkQy1nwb0XrZb0f1I_ydMH7oJd97uqACjhvkE2")  # Replace with your ngrok token

# Start Streamlit app
!streamlit run app.py &>/dev/null &

# Create a public URL with ngrok
public_url = ngrok.connect(8501)

print(f"Access your Streamlit app here: {public_url}")
