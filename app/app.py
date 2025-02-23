"""Main LLM app"""
import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def extract_text_from_docx(filepath):
    """Extract text from a DOCX file"""
    doc = Document(filepath)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def simplify_text(text):
    """Simplify text using AI"""
    try:
        print("versimpelen")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Je bent een expert in het versimpelen van tekst. Maak de tekst begrijpelijk voor iedereen."},
                {"role": "user", "content": f"Versimpel deze tekst:\n\n{text}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error bij het versimpelen: {str(e)}"

def summarize_text(text):
    """Summarize text using AI in max 100 words"""
    try:
        print("samenvatten")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Je bent een expert in het samenvatten van tekst. Maak een samenvatting van maximaal 100 woorden."},
                {"role": "user", "content": f"Vat deze tekst samen in maximaal 100 woorden:\n\n{text}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error bij het samenvatten: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Geen bestand geupload', 400
            
        file = request.files['file']
        if file.filename == '':
            return 'Geen bestand geselecteerd', 400
            
        if file and file.filename.endswith('.docx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            document_text = extract_text_from_docx(filepath)
            transformation_type = request.form.get('transformation_type')

            if transformation_type == 'versimpel':
                transformed_text = simplify_text(document_text)
            elif transformation_type == 'samenvatten':
                transformed_text = summarize_text(document_text)
            else:
                transformed_text = document_text
            
            return render_template('index.html',
                                transformed_text=transformed_text,
                                transformation_type=transformation_type)
        else:
            return 'Alleen .docx bestanden zijn toegestaan', 400

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
