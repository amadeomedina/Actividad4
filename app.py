import os
import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', '')
llm = ChatGoogleGenerativeAI(model='models/gemini-flash-latest', temperature=0.7)

class ChatSession:
    def __init__(self, id):
        self.id, self.name, self.history, self.gradio_format, self.response_count = id, f'Chat {id}', [], [], 0
    def add(self, role, content):
        self.history.append(f'{role}: {content}')
        if role == 'Asistente': self.response_count += 1

sessions = {1: ChatSession(1)}

def predict(message, session_id):
    if not message.strip(): return '', sessions[session_id].gradio_format, sessions[session_id].response_count
    session = sessions[session_id]
    history_text = '\n'.join(session.history[-6:])
    prompt = f'Eres ChatMedina Pro.\n{history_text}\nUsuario: {message}\nRespuesta:'
    try:
        res = llm.invoke(prompt)
        ans = res.content if hasattr(res, 'content') else str(res)
        if isinstance(ans, list):
            ans = " ".join([part['text'] if isinstance(part, dict) and 'text' in part else str(part) for part in ans])
    except Exception as e: 
        ans = "⚠️ Límite de cuota alcanzado (429). Reintente en un momento." if "429" in str(e) else f"Error: {str(e)[:50]}"

    session.add('Usuario', message)
    session.add('Asistente', ans)
    session.gradio_format.append({'role': 'user', 'content': message})
    session.gradio_format.append({'role': 'assistant', 'content': ans})
    return '', session.gradio_format, session.response_count

with gr.Blocks() as demo:
    sid = gr.State(1)
    gr.Markdown('# 🚀 ChatMedina Pro')
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown('### 📁 Sesiones')
            session_list = gr.Radio(choices=[s.name for s in sessions.values()], value='Chat 1', label='Historial')
            counter = gr.Number(label='Respuestas', value=0, interactive=False)
        with gr.Column(scale=3):
            chat = gr.Chatbot(height=500)
            txt = gr.Textbox(placeholder='Escribe aquí...')
            txt.submit(predict, [txt, sid], [txt, chat, counter])

if __name__ == '__main__':
    demo.launch(theme=gr.themes.Soft(primary_hue='blue'))
