import streamlit as st
import requests
from PIL import Image
import io
import pandas as pd

# Ganti ini dengan token kamu dari HuggingFace
API_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Fungsi untuk kirim gambar dan dapatkan caption
def query_image(image_bytes):
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"❌ Gagal memanggil API: {response.status_code} - {response.text}")
        return None

# App UI
st.set_page_config(page_title="Auto-Catalog UMKM", layout="centered")
st.title("🛒 Auto-Catalog Generator untuk UMKM")
st.markdown("Upload gambar produk, dan AI akan buatkan deskripsi katalog secara otomatis.")

uploaded_files = st.file_uploader("Upload gambar produk", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

data_katalog = []

if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file).convert("RGB")
        st.image(image, width=300, caption=f"Gambar: {file.name}")

        # Convert image ke bytes
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()

        # Kirim ke API
        result = query_image(image_bytes)
        if result and isinstance(result, list) and "generated_text" in result[0]:
            caption = result[0]["generated_text"]
        else:
            caption = "Deskripsi tidak tersedia"

        # Tambahkan ke data katalog
        judul = caption.strip().title()
        kategori = "Fashion" if "shirt" in caption.lower() or "dress" in caption.lower() else "Umum"
        harga = "Rp100.000"

        data_katalog.append({
            "Nama File": file.name,
            "Judul Produk": judul,
            "Deskripsi Produk": caption,
            "Kategori": kategori,
            "Harga": harga
        })

    # Tampilkan katalog
    df = pd.DataFrame(data_katalog)
    st.success("✅ Katalog berhasil dibuat otomatis oleh AI!")
    st.dataframe(df)

    # Tombol unduh
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Unduh Katalog (CSV)", data=csv, file_name="katalog_umkm.csv", mime="text/csv")
