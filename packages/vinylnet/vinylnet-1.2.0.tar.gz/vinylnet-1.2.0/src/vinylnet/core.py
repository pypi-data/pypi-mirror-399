import librosa
import numpy as np
import cv2
import struct
import os
import soundfile as sf

# --- GEOMETRÍA (Matemáticas) ---

def _get_spiral_coords_forced(n_samples, center, radius_min, radius_max):
    """Calcula la espiral determinista (CLV)."""
    coords = np.zeros((n_samples, 2), dtype=np.int32)
    
    R2_max = radius_max**2
    R2_min = radius_min**2
    R_diff = R2_max - R2_min
    
    indices = np.arange(n_samples)
    if n_samples > 0:
        t = indices / float(n_samples)
    else:
        return coords, np.array([])

    radii = np.sqrt(R2_min + (t * R_diff))
    
    # Epsilon para evitar división por cero
    d_thetas = 1.0 / (radii + 1e-9)
    thetas = np.cumsum(d_thetas)
    
    x_vals = center[0] + radii * np.cos(thetas)
    y_vals = center[1] + radii * np.sin(thetas)
    
    coords[:, 0] = x_vals.astype(np.int32)
    coords[:, 1] = y_vals.astype(np.int32)
            
    return coords, radii

def _load_audio_data(input_path, duration, full):
    """
    Carga el audio. 
    Si full=True, ignora 'duration' en la carga y trae todo el archivo.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"El archivo no existe: {input_path}")
    
    # Si queremos todo el audio, duration debe ser None para librosa
    load_duration = None if full else duration
    
    print(f"   Leyendo audio (Full={full})...")
    y, sr = librosa.load(input_path, mono=False, duration=load_duration)
    
    if y.ndim == 1:
        y = np.vstack((y, y))
        
    return y, sr

# --- RENDERIZADO (Dibujar un solo disco) ---

def _render_frame_8bit(y_chunk, sr, output_path, img_size):
    """Dibuja un solo fragmento en 8 bits."""
    center = (img_size // 2, img_size // 2)
    radius_min = 50
    radius_max = img_size // 2
    n_samples = y_chunk.shape[1]

    # Normalización 8-bit
    def to_uint8(arr):
        arr = np.clip(arr, -1.0, 1.0)
        norm = (arr + 1.0) / 2.0
        return (norm * 255.0).astype(np.uint8)

    pixel_L = to_uint8(y_chunk[0])
    pixel_R = to_uint8(y_chunk[1])
    
    coords, radii = _get_spiral_coords_forced(n_samples, center, radius_min, radius_max)
    
    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    
    valid_mask = (coords[:, 0] >= 0) & (coords[:, 0] < img_size) & \
                 (coords[:, 1] >= 0) & (coords[:, 1] < img_size)
    
    xs = coords[valid_mask, 0]
    ys = coords[valid_mask, 1]
    r_vals = radii[valid_mask]
    
    pixel_B = ((np.sin(r_vals * 0.1) + 1) * 0.5 * 255.0).astype(np.uint8)
    
    img[ys, xs, 2] = pixel_L[valid_mask]
    img[ys, xs, 1] = pixel_R[valid_mask]
    img[ys, xs, 0] = pixel_B

    # Header
    header = struct.pack('II', n_samples, sr)
    header_pixels = np.frombuffer(header, dtype=np.uint8)
    img[0, 0:8, 0] = 0 
    img[0, 0:len(header_pixels), 0] = header_pixels
    
    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])

def _render_frame_16bit(y_chunk, sr, output_path, img_size):
    """Dibuja un solo fragmento en 16 bits."""
    center = (img_size // 2, img_size // 2)
    radius_min = 50
    radius_max = img_size // 2
    n_samples = y_chunk.shape[1]

    # Normalización 16-bit
    def to_uint16(arr):
        arr = np.clip(arr, -1.0, 1.0)
        norm = (arr + 1.0) / 2.0
        return (norm * 65535.0).astype(np.uint16)

    pixel_L = to_uint16(y_chunk[0])
    pixel_R = to_uint16(y_chunk[1])
    
    coords, radii = _get_spiral_coords_forced(n_samples, center, radius_min, radius_max)
    
    img = np.zeros((img_size, img_size, 3), dtype=np.uint16)
    
    valid_mask = (coords[:, 0] >= 0) & (coords[:, 0] < img_size) & \
                 (coords[:, 1] >= 0) & (coords[:, 1] < img_size)
    
    xs = coords[valid_mask, 0]
    ys = coords[valid_mask, 1]
    r_vals = radii[valid_mask]
    
    pixel_B = ((np.sin(r_vals * 0.1) + 1) * 0.5 * 65535.0).astype(np.uint16)
    
    img[ys, xs, 2] = pixel_L[valid_mask]
    img[ys, xs, 1] = pixel_R[valid_mask]
    img[ys, xs, 0] = pixel_B

    # Header
    header = struct.pack('II', n_samples, sr)
    header_pixels = np.frombuffer(header, dtype=np.uint16)
    img[0, 0:4, 0] = 0 
    img[0, 0:len(header_pixels), 0] = header_pixels
    
    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])

# --- FUNCIONES PÚBLICAS (Con soporte FULL) ---

def save_8bits(input_path, output_path, duration=10.3, resolution=768, full=False):
    """
    Guarda audio como PNG 8-bit.
    Si full=True, divide todo el audio en segmentos de 'duration' y guarda múltiples imágenes.
    Ej: salida_000.png, salida_001.png
    """
    print(f"VinylNet 8-bit: Procesando {input_path}...")
    y, sr = _load_audio_data(input_path, duration, full)
    
    if not full:
        # Caso Simple: Solo el primer fragmento
        _render_frame_8bit(y, sr, output_path, resolution)
        print(f"-> Guardado: {output_path}")
    else:
        # Caso Full: Bucle de segmentación
        total_samples = y.shape[1]
        chunk_samples = int(duration * sr)
        
        # Generar nombre base sin extensión
        base, ext = os.path.splitext(output_path)
        
        count = 0
        for i in range(0, total_samples, chunk_samples):
            # Cortar el pedazo (Slice)
            segment = y[:, i : i + chunk_samples]
            
            # Si el último pedazo es muy pequeño (menos de 0.1s), lo ignoramos
            if segment.shape[1] < (sr * 0.1): continue
            
            # Nombre secuencial: cancion_000.png, cancion_001.png
            current_out = f"{base}_{count:03d}{ext}"
            
            _render_frame_8bit(segment, sr, current_out, resolution)
            print(f"   -> Segmento {count}: {current_out}")
            count += 1
        print("-> Proceso masivo terminado.")

def save_16bits(input_path, output_path, duration=10.3, resolution=768, full=False):
    """
    Guarda audio como PNG 16-bit.
    Si full=True, divide todo el audio en segmentos.
    """
    print(f"VinylNet 16-bit: Procesando {input_path}...")
    y, sr = _load_audio_data(input_path, duration, full)
    
    if not full:
        _render_frame_16bit(y, sr, output_path, resolution)
        print(f"-> Guardado: {output_path}")
    else:
        total_samples = y.shape[1]
        chunk_samples = int(duration * sr)
        base, ext = os.path.splitext(output_path)
        
        count = 0
        for i in range(0, total_samples, chunk_samples):
            segment = y[:, i : i + chunk_samples]
            if segment.shape[1] < (sr * 0.1): continue
            
            current_out = f"{base}_{count:03d}{ext}"
            
            _render_frame_16bit(segment, sr, current_out, resolution)
            print(f"   -> Segmento {count}: {current_out}")
            count += 1
        print("-> Proceso masivo terminado.")

# --- DECODERS (Sin cambios, funcionan igual) ---

def load_8bits(input_img_path, output_wav_path):
    # ... (Tu código de decoder 8bits anterior va aquí igual) ...
    # Voy a resumirlo para no ocupar espacio extra, usa el mismo que tenías
    print(f"VinylNet: Decodificando {input_img_path} (8-bit)...")
    img = cv2.imread(input_img_path, cv2.IMREAD_UNCHANGED)
    if img is None: raise FileNotFoundError(f"No se encontró: {input_img_path}")
    
    img_size = img.shape[0]
    center = (img_size // 2, img_size // 2)
    radius_min = 50
    radius_max = img_size // 2

    try:
        header_pixels = img[0, 0:8, 0]
        n_samples, sr = struct.unpack('II', header_pixels.tobytes())
    except: return

    coords, _ = _get_spiral_coords_forced(n_samples, center, radius_min, radius_max)
    valid_mask = (coords[:, 0] >= 0) & (coords[:, 0] < img_size) & \
                 (coords[:, 1] >= 0) & (coords[:, 1] < img_size)
    xs, ys = coords[valid_mask, 0], coords[valid_mask, 1]

    pixel_L = img[ys, xs, 2] 
    pixel_R = img[ys, xs, 1]

    audio_L = (pixel_L.astype(np.float32) / 255.0 * 2.0) - 1.0
    audio_R = (pixel_R.astype(np.float32) / 255.0 * 2.0) - 1.0
    
    sf.write(output_wav_path, np.array([audio_L, audio_R]).T, sr)
    print(f"-> Audio reconstruido: {output_wav_path}")

def load_16bits(input_img_path, output_wav_path):
    # ... (Tu código de decoder 16bits anterior va aquí igual) ...
    print(f"VinylNet: Decodificando {input_img_path} (16-bit)...")
    img = cv2.imread(input_img_path, cv2.IMREAD_UNCHANGED)
    if img is None: raise FileNotFoundError(f"No se encontró: {input_img_path}")
    
    img_size = img.shape[0]
    center = (img_size // 2, img_size // 2)
    radius_min = 50
    radius_max = img_size // 2

    try:
        header_pixels = img[0, 0:4, 0]
        n_samples, sr = struct.unpack('II', header_pixels.tobytes())
    except: return

    coords, _ = _get_spiral_coords_forced(n_samples, center, radius_min, radius_max)
    valid_mask = (coords[:, 0] >= 0) & (coords[:, 0] < img_size) & \
                 (coords[:, 1] >= 0) & (coords[:, 1] < img_size)
    xs, ys = coords[valid_mask, 0], coords[valid_mask, 1]

    pixel_L = img[ys, xs, 2] 
    pixel_R = img[ys, xs, 1]

    audio_L = (pixel_L.astype(np.float32) / 65535.0 * 2.0) - 1.0
    audio_R = (pixel_R.astype(np.float32) / 65535.0 * 2.0) - 1.0
    
    sf.write(output_wav_path, np.array([audio_L, audio_R]).T, sr)
    print(f"-> Audio reconstruido: {output_wav_path}")