import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION (From Report Section 2: Generation Logic) ---
SAMPLE_RATE = 16000     # 16 kHz
N_FFT = 2048            # Window Length (approx 128ms)
HOP_LENGTH = 512        # 75% Overlap
N_MELS = 128            # Frequency Bands
F_MIN = 0               # Lowest Frequency
F_MAX = 8000            # Nyquist Frequency (half of SR)

def generate_mel_spectrogram(input_path, output_folder, filename_stem):
    """
    Converts Clean Audio -> Mel Spectrogram
    """
    try:
        # 1. Load Clean Audio
        y, sr = librosa.load(input_path, sr=SAMPLE_RATE)

        # 2. STFT Transformation (The Math)
        mel_spect = librosa.feature.melspectrogram(
            y=y, 
            sr=sr, 
            n_fft=N_FFT, 
            hop_length=HOP_LENGTH, 
            n_mels=N_MELS,
            fmin=F_MIN,
            fmax=F_MAX
        )

        # 3. Log-Scale Conversion (Decibels)
        mel_spect_db = librosa.power_to_db(mel_spect, ref=np.max)

        # --- SAVE OPTION 1: FOR AI MODEL (Tensor/Numpy) ---
        # This is the actual data Brighton needs for TensorFlow
        npy_path = os.path.join(output_folder, f"{filename_stem}.npy")
        np.save(npy_path, mel_spect_db.astype(np.float32))

        # --- SAVE OPTION 2: FOR REPORT/DEBUGGING (PNG Image) ---
        # This generates the visual "Figure 3.10.3" from your report
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(mel_spect_db, sr=sr, hop_length=HOP_LENGTH, 
                                 x_axis='time', y_axis='mel', fmax=F_MAX, cmap='magma')
        plt.colorbar(format='%+2.0f dB')
        plt.title(f'Mel-Spectrogram: {filename_stem}')
        plt.tight_layout()
        
        png_path = os.path.join(output_folder, f"{filename_stem}.png")
        plt.savefig(png_path)
        plt.close() # Close memory to prevent crashing

        return True

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

# --- BATCH PROCESSING ---
if __name__ == "__main__":
    input_root = "processed_data"  # <--- Reads your CLEAN data
    output_root = "spectrograms"   # <--- New Folder for Features

    print(f"🚀 Starting Feature Extraction...")
    print(f"   - Config: {N_MELS} Mels, {N_FFT} Window")

    count = 0

    # Recursive Walk (Preserves PD/Patient structure)
    for root, dirs, files in os.walk(input_root):
        
        # Mirror the folder structure in the output
        relative_path = os.path.relpath(root, input_root)
        final_output_dir = os.path.join(output_root, relative_path)
        
        if not os.path.exists(final_output_dir):
            os.makedirs(final_output_dir)

        for filename in files:
            if filename.endswith(".wav"):
                
                input_path = os.path.join(root, filename)
                filename_stem = os.path.splitext(filename)[0]
                
                print(f"Generating features for: {filename}...", end=" ")
                success = generate_mel_spectrogram(input_path, final_output_dir, filename_stem)
                
                if success:
                    print("✅ Done")
                    count += 1
                else:
                    print("❌ Failed")

    print(f"\n✨ Extraction Complete. {count} spectrograms generated in '{output_root}'.")