from pyrogram import Client, filters
import re
import os
import asyncio
import time
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
    
    audio_path = None
    srt_path = None
    
    try:
        # Descargar el audio
        audio_path = f"{user_directory}/{file_unique_id}_{reply_to_message_id}.mp3"
        msg = await message.reply_text("📥 Descargando audio...", reply_to_message_id=reply_to_message_id)
        await app.download_media(message.audio, file_name=audio_path)
        
        # Procesar con Whisper
        await msg.edit("🔍 Generando subtítulos con Whisper...")
        
        # Construir el comando Whisper
        command = f"whisper \"{audio_path}\" --language Spanish --model small -o \"{user_directory}\" --output_format srt"
        print(f"\n\n🔥 Ejecutando Whisper: {command}\n")
        
        # Ejecutar el comando con os.system (muestra output en terminal)
        start_time = time.time()
        return_code = os.system(command)
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ Whisper completado en {elapsed_time:.2f} segundos. Código de retorno: {return_code}")
        
        # Verificar si se creó el archivo SRT
        srt_path = f"{user_directory}/{os.path.basename(audio_path).rsplit('.', 1)[0]}.srt"
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
        print(f"\n❌ Error en el proceso: {str(e)}")
    
    finally:
        # Limpiar archivos temporales
        for file_path in [audio_path, srt_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"🗑️ Archivo eliminado: {file_path}")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar {file_path}: {str(e)}")
        print("="*50 + "\n")
                
print("bot iniciado")
app.run()
