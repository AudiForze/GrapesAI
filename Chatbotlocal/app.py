from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json
import logging
from datetime import datetime
import os
import base64
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Formatos permitidos y configuración

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/webhook-chatbot"
N8N_FILE_WEBHOOK_URL = "http://localhost:5678/webhook/upload-file2"  
PORT = int(os.environ.get('PORT', 5000))

UPLOAD_FOLDER = 'temp_uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
    'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'json', 'xml', 'zip'
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ChatbotService:
    def __init__(self, n8n_webhook_url, n8n_file_webhook_url):
        self.n8n_webhook_url = n8n_webhook_url
        self.n8n_file_webhook_url = n8n_file_webhook_url
        
    def send_to_n8n(self, message, session_id):
        """
        Envía un mensaje al webhook de n8n y obtiene la respuesta
        """
        try:
            payload = {
                "message": message,
                "sessionId": session_id
            }
            
            logger.info(f"Enviando mensaje a n8n para sesión {session_id}: {message[:50]}...")
            
            response = requests.post(
                self.n8n_webhook_url, 
                json=payload, 
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=60
            )
            
            response.raise_for_status()
            
            response_data = response.json()
            logger.info(f"Respuesta de n8n: {response_data}")
            
            bot_message = response_data.get('message', 'Lo siento, no pude obtener una respuesta de n8n.')
            
            return {
                'success': True,
                'message': bot_message
            }
            
        except requests.exceptions.Timeout:
            logger.error("Error de conexión a n8n: Tiempo de espera agotado.")
            return {
                'success': False,
                'message': 'Lo siento, el servicio está tardando demasiado en responder. Por favor, intenta de nuevo.'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al conectar con n8n: {e}")
            return {
                'success': False,
                'message': f'Lo siento, ha ocurrido un error de conexión: {e}'
            }
            
    def send_file_to_n8n(self, file_data, session_id, message):
        """
        Envía el archivo y el mensaje al webhook de n8n y obtiene la respuesta
        """
        try:
            payload = {
                "filename": file_data['filename'],
                "filesize": file_data['filesize'],
                "filetype": file_data['filetype'],
                "file_base64": file_data['file_base64'],
                "message": message,
                "sessionId": session_id,
                "timestamp": datetime.now().isoformat(),
                "action": "file_upload"
            }
            
            logger.info(f"Enviando archivo y mensaje a n8n: {file_data['filename']} ({file_data['filesize']} bytes)")
            
            response = requests.post(
                self.n8n_file_webhook_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=60  
            )

            response.raise_for_status()
            
            response_data = response.json()
            logger.info(f"Respuesta de n8n para archivo: {response_data}")
            
            bot_message = response_data.get('message', f'Archivo {file_data["filename"]} y mensaje recibidos correctamente.')
            
            return {
                'success': True,
                'message': bot_message
            }
            
        except requests.exceptions.Timeout:
            logger.error("Error de conexión a n8n (file): Tiempo de espera agotado.")
            return {
                'success': False,
                'message': 'Lo siento, el servicio de subida está tardando demasiado en responder.'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al conectar con n8n (file): {e}")
            return {
                'success': False,
                'message': f'Lo siento, ha ocurrido un error de conexión: {e}'
            }


chatbot_service = ChatbotService(N8N_WEBHOOK_URL, N8N_FILE_WEBHOOK_URL)


@app.route('/')
def home():
    """
    Sirve el archivo HTML principal
    """
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return render_template_string(html_content)
    except FileNotFoundError:
        return "El archivo index.html no se encuentra. Asegúrate de que esté en el mismo directorio.", 404
    except Exception as e:
        logger.error(f"Error al servir index.html: {str(e)}")
        return "Error interno del servidor.", 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint para el chat regular
    """
    try:
        data = request.json
        message = data.get('message')
        session_id = data.get('sessionId', '')
        
        if not message:
            return jsonify({'error': 'Mensaje no proporcionado'}), 400
        
        if not session_id:
            return jsonify({'error': 'SessionId es requerido'}), 400
            
        logger.info(f"Mensaje recibido de sesión {session_id}: {message}")
        
        result = chatbot_service.send_to_n8n(message, session_id)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'sessionId': session_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'message': result['message'],
                'sessionId': session_id,
                'timestamp': datetime.now().isoformat()
            }), 200
            
    except Exception as e:
        logger.error(f"Error en endpoint /api/chat: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Lo siento, ha ocurrido un error. Por favor intenta de nuevo.'
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Endpoint para subir archivos y mensajes combinados
    """
    try:
        # Validar que hay un archivo en la petición
        if 'file' not in request.files:
            return jsonify({
                'error': 'No se ha enviado ningún archivo'
            }), 400
        
        file = request.files['file']
        session_id = request.form.get('sessionId', '')
        message = request.form.get('message', '') # Nuevo: Obtiene el mensaje del formulario
        
        if file.filename == '':
            return jsonify({
                'error': 'No se ha seleccionado ningún archivo'
            }), 400
        
        if not session_id:
            return jsonify({
                'error': 'SessionId es requerido'
            }), 400
        
        # Validar tipo de archivo
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Tipo de archivo no permitido. Tipos permitidos: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Leer el archivo
        file_content = file.read()
        file_size = len(file_content)
        
        # Validar tamaño
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'El archivo es demasiado grande. Tamaño máximo: {MAX_FILE_SIZE / (1024*1024):.1f}MB'
            }), 400
        
        # Preparar datos del archivo
        filename = secure_filename(file.filename)
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        file_data = {
            'filename': filename,
            'filesize': file_size,
            'filetype': file.content_type or 'application/octet-stream',
            'file_base64': file_base64
        }
        
        logger.info(f"Procesando archivo para sesión {session_id}: {filename} ({file_size} bytes)")
        
        # Enviar datos a n8n
        result = chatbot_service.send_file_to_n8n(file_data, session_id, message)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'filename': filename,
                'filesize': file_size,
                'sessionId': session_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'message': result['message'],
                'sessionId': session_id,
                'timestamp': datetime.now().isoformat()
            }), 200
        
    except Exception as e:
        logger.error(f"Error en endpoint /api/upload: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Lo siento, ha ocurrido un error al procesar el archivo. Por favor intenta de nuevo.'
        }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """
    Proporciona información básica (sin datos sensibles)
    """
    return jsonify({
        'n8n_configured': bool(N8N_WEBHOOK_URL and N8N_WEBHOOK_URL != "https://tu-instancia-n8n.com/webhook/webhook-chatbot"),
        'file_upload_configured': bool(N8N_FILE_WEBHOOK_URL),
        'version': '1.0.0',
        'max_file_size': MAX_FILE_SIZE,
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': f'El archivo es demasiado grande. Tamaño máximo: {MAX_FILE_SIZE / (1024*1024):.1f}MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint no encontrado'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Método no permitido'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno del servidor: {str(error)}")
    return jsonify({
        'error': 'Error interno del servidor'
    }), 500

if __name__ == '__main__':
    app.run(port=PORT, debug=True)