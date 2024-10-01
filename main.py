import json
import os
import PyPDF2
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from flask import Flask, jsonify, request, send_file, send_from_directory

os.environ["GOOGLE_API_KEY"] = "AIzaSyALSMnAZqXJKQJaLwx72p-vtEhnYPiS0DI"

app = Flask(__name__)

# Simulação de um banco de dados de documentos (texto simples)
DOCUMENTS = [
    {"id": 1, "content": "O clima hoje está ensolarado."},
    {"id": 2, "content": "A previsão do tempo para amanhã é de chuva."},
]

# Função para ler texto de um arquivo PDF
def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# Exemplo de como você pode carregar documentos PDF
PDF_PATHS = ['/home/user/my-gemini-app/Artigo-cientifico-Vitoria.pdf', '/home/user/my-gemini-app/ArtigoCientifico.pdf']
for pdf_path in PDF_PATHS:
    text = read_pdf(pdf_path)
    DOCUMENTS.append({"id": len(DOCUMENTS) + 1, "content": text})

def retrieve_documents(query):
    results = []
    for doc in DOCUMENTS:
        if query.lower() in doc["content"].lower():
            results.append(doc["content"])
    return results

@app.route("/")
def index():
    return send_file('web/index.html')

@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if os.environ["GOOGLE_API_KEY"] == 'TODO':
            return jsonify({ "error": "API key not set." })
        try:
            req_body = request.get_json()
            content = req_body.get("contents")
            retrieved_docs = retrieve_documents(content)
            augmented_content = content + "\n\n" + "\n".join(retrieved_docs)

            model = ChatGoogleGenerativeAI(model=req_body.get("model"))
            message = HumanMessage(content=augmented_content)
            response = model.stream([message])
            
            def stream():
                for chunk in response:
                    yield 'data: %s\n\n' % json.dumps({ "text": chunk.content })

            return stream(), {'Content-Type': 'text/event-stream'}

        except Exception as e:
            return jsonify({ "error": str(e) })

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))
