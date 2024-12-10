import streamlit as st

import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
import streamlit as st
import pandas as pd
from io import StringIO


# Dummy data voor het DataFrame
from azure.storage.blob import BlobClient, BlobServiceClient

st.set_page_config(layout="wide")

conn_str = st.secrets["CONN_STR"]


@st.cache_data
def get_data():
    blob_client = BlobClient.from_connection_string(conn_str=conn_str, container_name="data", blob_name="cjib_differences_v2.csv")
    csv_data = blob_client.download_blob().content_as_text()
    df = pd.read_csv(StringIO(csv_data)).sample(10)
    return df


df = get_data()  


# Function to highlight differences with colored tags
def highlight_differences(text1, text2):
    matcher = SequenceMatcher(None, text1.split(), text2.split())
    highlighted_text1 = []
    highlighted_text2 = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':  # Substitution
            highlighted_text1.append(f'<span style="color: blue; font-weight: bold;">{" ".join(text1.split()[i1:i2])}</span>')
            highlighted_text2.append(f'<span style="color: blue; font-weight: bold;">{" ".join(text2.split()[j1:j2])}</span>')
        elif tag == 'insert':  # Insertion
            highlighted_text2.append(f'<span style="color: green; font-weight: bold;">{" ".join(text2.split()[j1:j2])}</span>')
        elif tag == 'delete':  # Deletion
            highlighted_text1.append(f'<span style="color: red; font-weight: bold;">{" ".join(text1.split()[i1:i2])}</span>')

        elif tag == 'equal':  # No change
            highlighted_text1.append(" ".join(text1.split()[i1:i2]))
            highlighted_text2.append(" ".join(text2.split()[j1:j2]))

    # If there are no insertions, ensure highlighted_text2 matches the baseline
    highlighted_text2 = highlighted_text2 or [" ".join(text2.split())]

    return " ".join(highlighted_text1), " ".join(highlighted_text2)

# Initialize session state for row index
if "row_index" not in st.session_state:
    st.session_state.row_index = 1

st.title("Zie het verschil tussen een oud en nieuw artikel (ter illustratie met irrelevant wetsartikelen)")

# st.subheader("<span style='color: red;'>Blauw</span> betekent dat een stuk tekst is vervangen door een ander stuk tekst. Groen betekent dat een stuk tekst is toegevoegd. Rood betekent dat een stuk tekst is verwijderd.")


# Get the current row's texts
current_row = df.iloc[st.session_state.row_index]
text_left = current_row["huidig_artikel_tekst"]
text_right = current_row["nieuw_artikel_tekst"]

# Highlight differences
highlighted_text_left, highlighted_text_right = highlight_differences(text_left, text_right)

# Create two columns
col1, col2 = st.columns(2)

# Display the highlighted texts
with col1:
    st.subheader(f"{current_row['huidig_artikel_naam']} oud")
    st.markdown(f"<p style='font-size: 18px;'>{highlighted_text_left}</p>", unsafe_allow_html=True)

with col2:
    st.subheader(f"{current_row['nieuw_artikel_naam']} nieuw")
    st.markdown(f"<p style='font-size: 18px;'>{highlighted_text_right}</p>", unsafe_allow_html=True)

# Button to move to the next row
if st.button("Volgend artikel"):
    st.session_state.row_index = (st.session_state.row_index + 1) % len(df)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<b>Legenda</b>", unsafe_allow_html=True)
st.markdown(f"<span style='color: blue;'>Blauw</span> betekent dat een stuk tekst is vervangen door een ander stuk tekst.", unsafe_allow_html=True)
st.markdown(f"<span style='color: green;'>Groen</span> betekent dat een stuk tekst is toegevoegd", unsafe_allow_html=True)
st.markdown(f"<span style='color: red;'>Rood</span> betekent dat een stuk tekst is verwijderd.", unsafe_allow_html=True)
st.markdown(f"Zwart betekent dat een stuk tekst niet is aangepast.", unsafe_allow_html=True)