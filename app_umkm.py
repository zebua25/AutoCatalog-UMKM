# Auto-Catalog Generator UMKM

import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import pandas as pd
import os

# Load model and processor
@st.cache_resource
def load_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return processor, model, device

processor, model, device = load_model()

# Streamlit UI
st.set_page_config(page_title="Auto-Catalog Generator UMKM")
st.title("🛍️ Auto-Catalog Generator untuk UMKM")
st.write("Upload gambar produk UMKM kamu, dan sistem kami akan otomatis membuat katalog produk!")

uploaded_files = st.file_uploader("Upload Gambar Produk", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

catalog = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file).convert("RGB")
        inputs = processor(image, return_tensors="pt").to(device)
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

        st.image(image, caption="Gambar Produk", width=250)
        st.write(f"**Judul Otomatis:** {caption.title()}")
        st.write(f"**Deskripsi:** {caption}")

        kategori = st.selectbox(f"Kategori untuk: {caption.title()}", ["Makanan", "Minuman", "Kerajinan", "Pakaian", "Lainnya"], key=caption)
        harga = st.text_input(f"Harga untuk: {caption.title()}", value="Rp 0", key=caption+"_harga")

        catalog.append({
            "Judul Produk": caption.title(),
            "Deskripsi": caption,
            "Kategori": kategori,
            "Harga": harga
        })

    if catalog:
        st.subheader("📦 Katalog Produk Kamu")
        df_catalog = pd.DataFrame(catalog)
        st.dataframe(df_catalog)

        csv = df_catalog.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Katalog (CSV)", data=csv, file_name="katalog_umkm.csv", mime="text/csv")
