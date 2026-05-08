import os
import gradio as gr
try:
    from google.colab import userdata
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun

# Configuración Segura
def get_api_key():
    if IN_COLAB:
        return userdata.get('GOOGLE_API_KEY')
    return os.getenv('GOOGLE_API_KEY')

api_key = get_api_key()
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", temperature=0.7)
    config_error = None
else:
    llm = None
    config_error = "⚠️ Error: No se detectó GOOGLE_API_KEY."

# Herramientas
try:
    search = DuckDuckGoSearchRun()
except: search = None

def calculator(expression):
    try:
        allowed = "0123456789+-*/(). "
        clean_expr = "".join([c for c in expression if c in allowed])
        return str(eval(clean_expr, {"__builtins__": None}, {}))
    except: return "Error matemático."

# Gestión de Sesiones
class ChatSession:
    def __init__(self, id):
        self.id = id
        self.name = f"Conversación {id}"
        self.history = []
        self.gradio_format = []
        self.response_count = 0
    def add(self, role, content):
        self.history.append(f"{role}: {content}")
        if role == "Asistente": self.response_count += 1

sessions = {1: ChatSession(1)}

def predict(message, session_id):
    if config_error: 
        gr.Error(config_error)
        return "", sessions[session_id].gradio_format, sessions[session_id].response_count
    if not message.strip(): return "", sessions[session_id].gradio_format, sessions[session_id].response_count

    session = sessions[session_id]
    lower_msg = message.lower()
    context_info = ""

    if any(word in lower_msg for word in ["busca", "quien"]): 
        context_info = f"\n[Web]: {search.run(message)}" if search else ""
    elif any(char in lower_msg for char in "+-*/") and any(i.isdigit() for i in lower_msg):
        context_info = f"\n[Calc]: {calculator(message)}"

    full_prompt = f"Eres ChatMedina, un asistente avanzado.\nHistorial: {'\n'.join(session.history[-6:])}\nContexto: {context_info}\nUsuario: {message}"
    
    try:
        response = llm.invoke(full_prompt)
        answer = response.content
    except Exception as e: answer = f"Error: {e}"

    session.add("Usuario", message)
    session.add("Asistente", answer)
    session.gradio_format.append({"role": "user", "content": message})
    session.gradio_format.append({"role": "assistant", "content": answer})
    return "", session.gradio_format, session.response_count

# Interfaz
with gr.Blocks(theme=gr.themes.Soft(primary_hue='blue')) as demo:
    active_session_state = gr.State(1)
    gr.Markdown("# 🚀 ChatMedina Pro")
    with gr.Row():
        with gr.Column(scale=1):
            new_chat_btn = gr.Button("+ Nuevo Chat")
            session_list = gr.Radio(choices=[s.name for s in sessions.values()], value="Conversación 1", label="Chats")
            counter_display = gr.Number(label="Respuestas", value=0)
        with gr.Column(scale=3):
            chatbot_ui = gr.Chatbot(label="Chat", height=500)
            msg_input = gr.Textbox(label="Entrada")
            send_btn = gr.Button("Enviar", variant="primary")

    def load_session(name):
        sid = next(s.id for s in sessions.values() if s.name == name)
        return sid, sessions[sid].gradio_format, sessions[sid].response_count
    def create_new():
        new_id = max(sessions.keys()) + 1
        sessions[new_id] = ChatSession(new_id)
        return gr.update(choices=[s.name for s in sessions.values()], value=sessions[new_id].name), new_id, [], 0

    msg_input.submit(predict, [msg_input, active_session_state], [msg_input, chatbot_ui, counter_display])
    send_btn.click(predict, [msg_input, active_session_state], [msg_input, chatbot_ui, counter_display])
    session_list.change(load_session, session_list, [active_session_state, chatbot_ui, counter_display])
    new_chat_btn.click(create_new, None, [session_list, active_session_state, chatbot_ui, counter_display])

if __name__ == '__main__':
    demo.launch()