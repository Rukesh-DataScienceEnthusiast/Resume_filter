import os
from flask import Flask, render_template, request
import re
from pdfminer.high_level import extract_text
import docx2txt
import zipfile

app = Flask(__name__)


def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


def extract_text_from_docx(docx_path):
    return docx2txt.process(docx_path)


def extract_text_from_text(text_path):
    with open(text_path, 'r') as file:
        return file.read()


def extract_skills_from_resume(text, skills_list):
    matched_skills = []
    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        if re.search(pattern, text, re.IGNORECASE):
            matched_skills.append(skill)
    return matched_skills


@app.route('/')
def index():
    return render_template('getr.html')


@app.route('/upload', methods=['POST'])
def extract_skills():
    if 'resumes' not in request.files:
        return 'No file uploaded'

    resumes_zip = request.files['resumes']
    if resumes_zip.filename == '':
        return 'No file selected'

    # Save the uploaded zip file temporarily
    upload_dir = 'upload'
    os.makedirs(upload_dir, exist_ok=True)
    zip_path = os.path.join(upload_dir, resumes_zip.filename)
    resumes_zip.save(zip_path)

    # Extract resumes from the uploaded zip file
    extracted_resumes = {}
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith('.pdf') or file_name.endswith('.docx') or file_name.endswith('.txt'):
                resume_path = os.path.join(upload_dir, file_name)
                zip_ref.extract(file_name, upload_dir)

                # Extract text from the resume based on file extension
                if file_name.endswith('.pdf'):
                    text = extract_text_from_pdf(resume_path)
                elif file_name.endswith('.docx'):
                    text = extract_text_from_docx(resume_path)
                elif file_name.endswith('.txt'):
                    text = extract_text_from_text(resume_path)

                # List of predefined skills
                skills_list = ['Python', 'C', 'Data Analysis', 'Machine Learning', 'Communication',
                               'Project Management', 'Deep Learning', 'SQL', 'Tableau']

                # Extract skills from the resume text
                extracted_skills = extract_skills_from_resume(text, skills_list)

                # Check if any skill exists in the extracted skills
                if extracted_skills:
                    extracted_resumes[file_name] = extracted_skills

    return render_template('select.html', resumes=extracted_resumes)


if __name__ == '__main__':
    app.run(debug=True)
