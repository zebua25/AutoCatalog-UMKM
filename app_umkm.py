import streamlit as st
import requests
from PIL import Image
import io
import pandas as pd
import base64

# Ganti dengan token milik kalian
API_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def query(image_base64):
    payload = {
        "inputs": {
            "image": image_base64
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"❌ Gagal memanggil API: {response.status_code} - {response.text}")
        return None

st.set_page_config(page_title="Auto-Catalog UMKM")
st.title("🛍️ Auto-Catalog Generator untuk UMKM")
st.markdown("Upload gambar produk, AI akan menghasilkan deskripsi katalog secara otomatis.")

uploaded_files = st.file_uploader("Upload gambar produk", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

data_katalog = []

if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file).convert("RGB")
        st.image(image, width=300)

        encoded_image = encode_image(image)
        result = query(encoded_image)

        if result and isinstance(result, list) and "generated_text" in result[0]:
            caption = result[0]["generated_text"]
        else:
            caption = "Deskripsi tidak tersedia"

        judul = caption.title()
        kategori = "Umum"
        harga = "Rp100.000"

        data_katalog.append({
            "Nama File": file.name,
            "Judul Produk": judul,
            "Deskripsi Produk": caption,
            "Kategori": kategori,
            "Harga": harga
        })

    df = pd.DataFrame(data_katalog)
    st.success("✅ Katalog berhasil dibuat otomatis!")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Unduh Katalog (CSV)", csv, "katalog_umkm.csv", "text/csv")
