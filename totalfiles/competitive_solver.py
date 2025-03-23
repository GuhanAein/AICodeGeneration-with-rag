# import streamlit as st
# import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
# from datasets import load_dataset
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.vector_stores.faiss import FaissVectorStore
# import faiss
# import os
# from huggingface_hub import login

# HF_TOKEN = "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"
# login(HF_TOKEN)

# def setup_competitive_solver():
#     os.makedirs("knowledge_base", exist_ok=True)
#     ds = load_dataset("codeparrot/apps", "all", split="train", trust_remote_code=True)
#     for i, example in enumerate(ds.select(range(100))):
#         solution = example['solutions'][0] if example['solutions'] else "No solution available"
#         with open(f"knowledge_base/doc_{i}.txt", "w", encoding="utf-8") as f:
#             f.write(f"### Problem\n{example['question']}\n\n### Solution\n{solution}")
    
#     documents = SimpleDirectoryReader("knowledge_base").load_data()
#     embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     Settings.embed_model = embed_model
#     d = 384
#     faiss_index = faiss.IndexFlatL2(d)
#     vector_store = FaissVectorStore(faiss_index=faiss_index)
#     return VectorStoreIndex.from_documents(documents, vector_store=vector_store)

# def generate_solution_with_rag(problem, index):
#     model_name = "meta-llama/Llama-3.2-3B-Instruct"
#     quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16, bnb_4bit_quant_type="nf4")
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant_config, device_map="auto")
#     if tokenizer.pad_token is None:
#         tokenizer.pad_token = tokenizer.eos_token
    
#     retriever = index.as_retriever(similarity_top_k=1)
#     retrieved_nodes = retriever.retrieve(problem)
#     context = retrieved_nodes[0].text if retrieved_nodes else "No relevant context found."
#     prompt = f"Given the following competitive programming problem:\n\n{problem}\n\nRelevant context:\n{context}\n\nGenerate a solution in Python:"
#     inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
#     outputs = model.generate(**inputs, max_new_tokens=300, temperature=0.7, top_p=0.9, do_sample=True)
#     return tokenizer.decode(outputs[0], skip_special_tokens=True)

# def run():
#     st.subheader("Competitive Programming Solver with RAG")
#     with st.spinner("Setting up solver..."):
#         index = setup_competitive_solver()
#     problem = st.text_area("Problem Statement", "Given an array of integers, find the maximum sum subarray.", height=200)
#     if st.button("Generate Solution"):
#         with st.spinner("Generating solution..."):
#             try:
#                 response = generate_solution_with_rag(problem, index)
#                 st.subheader("Generated Solution:")
#                 st.code(response, language="python")
#             except Exception as e:
#                 st.error(f"Error generating solution: {str(e)}")