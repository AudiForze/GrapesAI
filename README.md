# 🍇 GrapesAI

**GrapesAI** es una aplicación web impulsada por inteligencia artificial que permite **subir y analizar archivos de cualquier tipo** mediante un **chat interactivo**.  
El sistema está diseñado para comprender profundamente los documentos gracias a una memoria vectorizada, ofreciendo respuestas precisas, contextuales y continuas a lo largo de la conversación.

---

## 🚀 Descripción General

GrapesAI combina una **interfaz moderna e intuitiva** con un potente **backend inteligente** que integra:
- **Flask** como servidor principal.
- **n8n** para el flujo de procesamiento y orquestación de IA.
- **Google Gemini (PaLM)** como modelo de lenguaje y embeddings.
- **Supabase** como base de datos vectorial.
- **PostgreSQL** para la memoria conversacional persistente.
- **Google Drive** para almacenamiento seguro de archivos.

El resultado es un asistente capaz de **leer, entender y razonar** sobre cualquier documento que el usuario suba, recordando el contexto completo de la conversación.

---

## 🧠 Arquitectura de Inteligencia

El flujo de IA está diseñado para ofrecer **comprensión real y persistente del conocimiento**:

1. **Subida de archivo:**  
   Los archivos se envían desde el frontend a través del endpoint `/api/upload`, donde son validados y codificados en base64.

2. **Procesamiento en n8n:**  
   El flujo de trabajo (`My workflow 4.json`) decodifica el archivo, lo almacena en Google Drive, y genera **embeddings con Google Gemini**, que luego se guardan en **Supabase** como vectores semánticos.

3. **Memoria de conversación:**  
   GrapesAI utiliza un **módulo de memoria en PostgreSQL** para recordar todo lo que el usuario ha dicho, creando una experiencia de chat continua e inteligente.

4. **Agente conversacional:**  
   El modelo **Gemini 2.0 Flash** actúa como el cerebro de la IA, utilizando la memoria y los vectores para responder con contexto.

---

## 💡 Características Principales

### 🗂️ Soporte para múltiples formatos
Admite archivos de texto, documentos, hojas de cálculo, presentaciones, imágenes, y más:
> `.txt, .pdf, .png, .jpg, .jpeg, .gif, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .csv, .json, .xml, .zip`

### 💬 Chat con memoria
Cada sesión conserva la conversación y los datos procesados para ofrecer continuidad en las respuestas.

### 🧩 Memoria vectorial
Los documentos se **vectorizan** para crear una representación semántica que permite a la IA entender su contenido y responder de forma contextual.

### ☁️ Integración con n8n y Google Drive
Automatiza la carga, procesamiento y almacenamiento seguro de archivos sin intervención manual.

### 🔐 Backend escalable y seguro
El backend con Flask valida el tamaño, tipo y contenido de los archivos antes de procesarlos, asegurando estabilidad y protección de datos.

### 🌈 Interfaz moderna y adaptable
Diseño limpio, responsivo y animado con soporte para Markdown, bloques de código, indicadores de escritura y carga progresiva.

---

## 🧰 Tecnologías Utilizadas

| Componente | Tecnología |
|-------------|-------------|
| **Frontend** | HTML5, CSS3, JavaScript (ES6) |
| **Backend** | Flask (Python) |
| **Automatización** | n8n |
| **Base de datos** | Supabase (vector store) + PostgreSQL |
| **Modelo de IA** | Google Gemini 2.0 Flash |
| **Almacenamiento** | Google Drive |
| **Comunicación** | Webhooks + API REST |

---

## ⚙️ Instalación y Ejecución

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tuusuario/GrapesAI.git
   cd GrapesAI
   ```

2. **Instala dependencias:**
   ```bash
   pip install flask flask-cors requests
   ```

3. **Configura las URLs de n8n en `app.py`:**
   ```python
   N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/webhook-chatbot"
   N8N_FILE_WEBHOOK_URL = "http://localhost:5678/webhook/upload-file2"
   ```

4. **Ejecuta la aplicación:**
   ```bash
   python app.py
   ```

5. **Abre en el navegador:**
   ```
   http://localhost:5000
   ```

---

## 🧩 Flujo de Trabajo en n8n

El flujo `My workflow 4.json` contiene la lógica principal de IA:

- **Webhook**: recibe los mensajes y archivos.
- **Google Gemini Model**: genera respuestas y embeddings.
- **Vector Store (Supabase)**: almacena representaciones vectoriales.
- **Postgres Chat Memory**: guarda el contexto conversacional.
- **Respond to Webhook**: devuelve respuestas al chatbot en tiempo real.

---

## 🧠 Usos Potenciales

- Asistente de estudio que entiende apuntes, PDFs o libros.  
- Analizador de reportes, presentaciones o documentos empresariales.  
- Buscador inteligente de información corporativa.  
- Chat de soporte con memoria semántica.  
- Herramienta de investigación que combina múltiples fuentes documentales.

---

## 🌍 Ventajas de GrapesAI

✅ Interacción natural y contextual con tus propios documentos.  
✅ Capacidad para **recordar conversaciones anteriores**.  
✅ Integración fácil con servicios en la nube y APIs externas.  
✅ Arquitectura modular basada en **IA + n8n + vectorización**.  
✅ Diseñado para escalar y adaptarse a distintos casos de uso.  

---

## 🧑‍💻 Autor

**GrapesAI** ha sido creado con pasión y visión de futuro por **Geremy Gomez**,  
buscando unir la automatización inteligente con la comprensión profunda de datos.

---

## 📜 Licencia

Este proyecto se distribuye bajo la licencia **MIT**, lo que permite su uso, modificación y redistribución libremente, siempre que se mantenga la atribución correspondiente.

---

> 🍇 *“El conocimiento florece cuando la IA puede recordar y comprender.” — GrapesAI*
