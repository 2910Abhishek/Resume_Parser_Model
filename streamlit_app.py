import streamlit as st
import fitz
import spacy
from spacy.pipeline import EntityRuler
import os
import logging
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Loading pretrained model
nlp = spacy.load("en_core_web_lg")
# jsonl file
skills_pattern_file = "jz_skill_patterns.jsonl"

# Create an EntityRuler instance with a unique name
ruler = nlp.add_pipe("entity_ruler", name="my_entity_ruler")

# Load patterns from disk
ruler.from_disk(skills_pattern_file)

@st.cache_data(hash_funcs={spacy.language.Language: id})
def load_model():
    return nlp

@st.cache_data(hash_funcs={str: hash})
def parse_resume(pdf_file_path):
    text = ""
    with fitz.open(pdf_file_path) as pdf_doc:
        for page in pdf_doc:
            text += page.get_text()
    return text

def extract_email(text):
    # Using regular expression to extract email addresses
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return emails[0] if emails else ''

def extract_skills(text):
    doc = nlp(text)
    skills = set()
    for ent in doc.ents:
        if ent.label_ == 'SKILL':
            skills.add(ent.text.lower().capitalize())
    return skills

def main():
    st.title('Resume Skills Extractor')

    uploaded_file = st.file_uploader("Upload a resume (PDF format)", type="pdf")

    if uploaded_file is not None:
        # Save the PDF file temporarily
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract text from PDF using fitz
        text = parse_resume("temp.pdf")

        # Process text to extract skills
        skills = extract_skills(text)

        # Extract email using regular expression
        email = extract_email(text)

        # Remove temporary PDF file
        os.remove("temp.pdf")

        result = {"skills": list(skills), "email": email}

        st.json(result)

if __name__ == '__main__':
    main()
