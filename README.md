# 🚀 ChatMedina Pro

ChatMedina es un agente conversacional avanzado desarrollado con **Python** y **LangChain**, integrado con la API de **Google Gemini**.

## ✨ Características
- **Memoria de Conversación**: Gestiona múltiples sesiones independientes.
- **Búsqueda Web**: Capacidad de consultar información en tiempo real vía DuckDuckGo.
- **Calculadora Segura**: Resuelve expresiones matemáticas directamente desde el chat.
- **Interfaz Pro**: Diseño 'Light Blue' optimizado con Gradio.

## 🛠️ Tecnologías
- **Modelo**: Gemini Flash 1.5 (Google Generative AI)
- **Framework**: LangChain
- **Interfaz**: Gradio
- **Herramientas**: DuckDuckGo Search

## 🚀 Instalación y Uso Local

1. Clona el repositorio:
```bash
git clone <tu-url-de-github>
cd mi-app
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura tu API Key:
Crea una variable de entorno llamada `GOOGLE_API_KEY` o configúrala en tus secretos.

4. Ejecuta la app:
```bash
python app.py
```