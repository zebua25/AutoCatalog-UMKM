import streamlit as st
import requests
import base64
from PIL import Image
import io
import pandas as pd

API_TOKEN = "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"  # Ganti ini dengan token kalian
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error dari API: {response.status_code} - {response.text}")
        return None

st.title("🛍️ Auto-Catalog UMKM (HuggingFace API Version)")
st.markdown("Upload gambar produk, AI akan buatkan deskripsi otomatis.")

uploaded_files = st.file_uploader("Upload Gambar Produk", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

data_katalog = []

if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file).convert("RGB")
        st.image(image, width=200, caption="Preview Gambar")

        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        payload = {"inputs": {"image": img_str}}
        result = query(payload)

        if result and isinstance(result, list) and "generated_text" in result[0]:
            caption = result[0]["generated_text"]
        else:
            caption = "Deskripsi tidak tersedia"

        judul = caption.title()
        kategori = "Fashion" if "shirt" in caption.lower() or "shoe" in caption.lower() else "Umum"
        harga = f"Rp{str(100000)}"

        data_katalog.append({
            "Nama File": file.name,
            "Judul": judul,
            "Deskripsi": caption,
            "Kategori": kategori,
            "Harga": harga
        })

    df = pd.DataFrame(data_katalog)
    st.success("🎉 Katalog berhasil dibuat otomatis!")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Unduh Katalog CSV", csv, "katalog_umkm.csv", "text/csv")
