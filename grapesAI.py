import streamlit as st
import ollama

def grapesai():
    default_system_prompt = "You are a helpful, friendly and intelligent assistant. Your task is simply to talk to the user and help him solve his tasks. You should always respond in the same language as the user's message. Geremy is a very intelligent young programmer who has been in charge of developing and creating you."

    def create_completion_ollama(user_message, system_prompt=default_system_prompt, lang="Spanish"):
        try:
            formatted_messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"{user_message}\nIs mandatory to answer in {lang} language."}
            ]

            stream = ollama.chat(
                model='llama3.1', ## llama3.1 / deepseek-r1:8bs
                messages=formatted_messages,
                stream=True
            )
            
            response_text = ""
            for chunk in stream:
                response_text += chunk['message']['content']
            return response_text
        except Exception as e:
            print(f"Error en la API de Ollama: {e}")
            return "Lo siento, no pude obtener una respuesta."

    st.markdown("""
        <style>
            .user-message {
                background-color: #4CAF50;
                color: white;
                border-radius: 15px;
                padding: 10px;
                max-width: 80%;
                margin: 5px 0;
                margin-left: auto;
            }
            .bot-message {
                background-color: #f1f1f1;
                color: black;
                border-radius: 15px;
                padding: 10px;
                max-width: 80%;
                margin: 5px 0;
                margin-right: auto;
            }
        </style>
    """, unsafe_allow_html=True)

    user_input_text = st.text_input("Escribe tu mensaje:")
    if user_input_text:
        response = create_completion_ollama(user_input_text)
        st.markdown(f'<div class="user-message">{user_input_text}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-message">{response}</div>', unsafe_allow_html=True)

grapesai()
