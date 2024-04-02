import pygame
import requests
import os
from io import BytesIO


def reproducir_cancion(spotify_url, sp):
    # Obtiene el ID de la pista de Spotify desde el enlace proporcionado
    track_id = spotify_url.split('/')[-1]

    # Obtiene la información de la pista de Spotify
    track_info = sp.track(track_id)

    # Obtiene la URL de la vista previa de la pista
    preview_url = track_info['preview_url']

    # Descarga la vista previa de la pista
    audio_data = requests.get(preview_url).content

    # Obtiene la ruta del directorio actual
    current_directory = os.getcwd()

    # Define el nombre de la carpeta donde se guardará el archivo temporal
    temp_folder_name = 'temp'

    # Construye la ruta completa para la carpeta temporal
    temp_folder_path = os.path.join(
        f"{current_directory}/src/testing/spotify_play/", temp_folder_name)

    # Crea la carpeta temporal si no existe
    if not os.path.exists(temp_folder_path):
        os.makedirs(temp_folder_path)

    # Construye la ruta completa para el archivo de audio temporal dentro de la carpeta temporal
    audio_file_path = os.path.join(temp_folder_path, 'temp_audio.mp3')

    # Guarda la vista previa de la pista como un archivo temporal
    with open(audio_file_path, 'wb') as f:
        f.write(audio_data)

    # Reproduce la canción
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file_path)
    pygame.mixer.music.play()

    # Espera hasta que la canción termine de reproducirse
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Espera 10 milisegundos

    # Detiene la reproducción de música
    pygame.mixer.music.stop()

    # Elimina el archivo de audio una vez que la reproducción haya terminado
    os.remove('temp_audio.mp3')
