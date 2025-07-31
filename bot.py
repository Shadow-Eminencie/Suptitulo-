from pyrogram import Client, filters
import re
import os
import asyncio
from datetime import datetime

api_id = "29358405" 
api_hash = "aecf6fb613297b3e3d8fe3f6c9bbd241"
bot_token = "8442539810:AAFr0JoA1XB2npLJK60Vo7V1KLzDtRzRUNU" 

app = Client("Converting_Bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

USER_DIRECTORY = "Download_Converting"

def create_user_directory():
    os.makedirs(USER_DIRECTORY, exist_ok=True)
    return USER_DIRECTORY

def generate_file_unique_id(prefix="audio"):
    now = datetime.now()
    return f"{prefix}_{now.strftime('%Y-%m-%d_%H-%M-%S')}"

@app.on_message(filters.audio)
async def handle_audio(client, message):
    user_directory = create_user_directory()
    file_unique_id = generate_file_unique_id()
    reply_to_message_id = message.id
    chat_id = message.chat.id
    
    try:
        # Descargar el audio
        audio_path = f"{user_directory}/{file_unique_id}_{reply_to_message_id}.mp3"
        msg = await message.reply_text("📥 Descargando audio...", reply_to_message_id=reply_to_message_id)
        await app.download_media(message.audio, file_name=audio_path)
        
        # Procesar con Whisper
        await msg.edit("🔍 Generando subtítulos con Whisper...")
        srt_path = f"{user_directory}/{file_unique_id}_{reply_to_message_id}.srt"
        
        # Ejecutar Whisper de forma asíncrona
        command = f"whisper \"{audio_path}\" --language Spanish --model small -o \"{user_directory}\" --output_format srt"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Esperar a que termine el proceso
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error = stderr.decode().strip() if stderr else "Error desconocido"
            raise Exception(f"Whisper falló: {error}")
        
        # Verificar si se creó el archivo SRT
        if not os.path.exists(srt_path):
            raise Exception("No se generó el archivo de subtítulos")
        
        # Enviar subtítulos a Telegram
        await msg.edit("📤 Enviando subtítulos...")
        await app.send_document(
            chat_id=chat_id,
            document=srt_path,
            caption="Subtítulos generados con Whisper",
            reply_to_message_id=reply_to_message_id
        )
        
        await msg.edit("✅ Proceso completado!")
        
    except Exception as e:
        error_msg = f"💢 Error: {str(e)}"
        if 'msg' in locals():
            await msg.edit(error_msg)
        else:
            await message.reply_text(error_msg, reply_to_message_id=reply_to_message_id)
    
    finally:
        # Limpiar archivos temporales
        for file_path in [audio_path, srt_path]:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
                
print("bot iniciado")
app.run()