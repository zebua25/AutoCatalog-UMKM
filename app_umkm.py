import streamlit as st
import requests
from PIL import Image
import pandas as pd
from io import BytesIO

# Masukkan token Hugging Face kamu di sini
API_TOKEN = "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"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"

st.title("🛍️ Auto-Catalog Generator UMKM dengan AI Cloud")

uploaded_files = st.file_uploader("Upload Gambar Produk", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

catalog = []

def query_hf_api(image_bytes):
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    if response.status_code == 200:
        output = response.json()
        # output format: [{'generated_text': 'some caption'}]
        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"]
        else:
            return "Caption tidak ditemukan"
    else:
        st.error(f"❌ Gagal memanggil API: {response.status_code} - {response.text}")
        return None

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Gambar Produk", width=250)

        # Convert image to bytes
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()

        caption = query_hf_api(img_bytes)
        if caption:
            st.write(f"**Judul Otomatis:** {caption.title()}")
            st.write(f"**Deskripsi:** {caption}")

            kategori = st.selectbox(f"Kategori untuk: {caption.title()}", ["Makanan", "Minuman", "Kerajinan", "Pakaian", "Lainnya"], key=uploaded_file.name)
            harga = st.text_input(f"Harga untuk: {caption.title()}", value="Rp 0", key=uploaded_file.name + "_harga")

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
