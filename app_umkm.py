import streamlit as st
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import pandas as pd

# Load model only once
@st.cache_resource
def load_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

processor, model = load_model()

# Web UI
st.set_page_config(page_title="Auto-Catalog UMKM", layout="wide")
st.title("🛍️ Auto-Catalog UMKM: Upload Gambar → Dapatkan Katalog Otomatis!")
st.markdown("Powered by AI (BLIP) – Gratis dan praktis untuk UMKM Indonesia 🇮🇩")

uploaded_files = st.file_uploader("📤 Upload Gambar Produk", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

data_katalog = []

if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file).convert('RGB')
        st.image(image, width=200, caption="Preview Gambar")

        # Generate Caption
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

        # Proses Katalog Otomatis
        judul = caption.title()
        kategori = "Fashion" if "shirt" in caption.lower() or "shoe" in caption.lower() else "Umum"
        harga = "Rp{:,.0f}".format(torch.randint(50000, 250000, (1,)).item())

        data_katalog.append({
            "Nama File": file.name,
            "Judul": judul,
            "Deskripsi": caption,
            "Kategori": kategori,
            "Harga": harga
        })

    # Tampilkan Tabel Katalog
    df = pd.DataFrame(data_katalog)
    st.success("🎉 Katalog berhasil dibuat otomatis!")
    st.dataframe(df)

    # Tombol Unduh CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Unduh Katalog CSV", csv, "katalog_umkm.csv", "text/csv")
