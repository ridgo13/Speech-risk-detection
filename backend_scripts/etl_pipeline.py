import librosa
import numpy as np
import scipy.signal
import soundfile as sf
import os

# --- CONFIGURATION (Matches Report & Governance Rules) ---
TARGET_SAMPLE_RATE = 16000  # Standard for ML Model
SILENCE_THRESHOLD_DB = 20   # Threshold to cut silence
MIN_SNR_DB = 10             # Governance Rule: SNR > 10dB (Chapter 4)
MIN_DURATION_SEC = 1.5      # Governance Rule: Duration > 1.5s (Chapter 3 Fail-Fast)

class AudioETL:
    def __init__(self):
        print(f"Initializing SpeakTrum ETL Engine...")
        print(f"   - SNR Threshold: {MIN_SNR_DB} dB")
        print(f"   - Min Duration:  {MIN_DURATION_SEC} sec")

    def ingest_audio(self, file_path):
        """
        STEP 1: Ingestion
        Loads audio, resamples to 16kHz, converts to Mono.
        """
        try:
            # librosa loads as mono by default
            audio_data, sr = librosa.load(file_path, sr=TARGET_SAMPLE_RATE)
            return audio_data
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def calculate_snr(self, audio_data):
        """
        STEP 2: SNR Quality Check
        """
        # 1. Get energy of every frame
        S = np.abs(librosa.stft(audio_data))
        power = np.mean(S**2, axis=0)
        
        # 2. Signal Power (Top 10% loudest frames)
        signal_power = np.mean(np.sort(power)[-int(len(power)*0.1):])
        
        # 3. Noise Power (Bottom 10% quietest frames)
        noise_power = np.mean(np.sort(power)[:int(len(power)*0.1)]) + 1e-10
        
        # 4. Calculate dB
        snr = 10 * np.log10(signal_power / noise_power)
        return snr

    def apply_wiener_filter(self, audio_data):
        """
        STEP 3: Noise Reduction (Wiener Filter)
        Only applied if audio passes SNR check.
        """
        return scipy.signal.wiener(audio_data, mysize=15)

    def remove_silence(self, audio_data):
        """
        STEP 4: VAD (Silence Removal)
        """
        trimmed_audio, index = librosa.effects.trim(audio_data, top_db=SILENCE_THRESHOLD_DB)
        return trimmed_audio

    def run_pipeline(self, input_path, output_path):
        """
        MASTER PIPELINE FLOW:
        Ingest -> Duration Check -> SNR Check -> Wiener Filter -> VAD -> Save
        """
        # 1. Load
        raw_audio = self.ingest_audio(input_path)
        if raw_audio is None: return False

        # --- GATE 1: DURATION CHECK (Chapter 3 Governance) ---
        duration = len(raw_audio) / TARGET_SAMPLE_RATE
        if duration < MIN_DURATION_SEC:
            print(f"⚠️ REJECTED: Too short ({duration:.2f}s < {MIN_DURATION_SEC}s)")
            return False

        # --- GATE 2: SNR CHECK (Chapter 4 Quality Control) ---
        snr = self.calculate_snr(raw_audio)
        
        if snr < MIN_SNR_DB:
            # REJECT: Stop immediately. Do not clean. Do not save.
            print(f"⚠️ REJECTED: SNR too low ({snr:.2f} dB < {MIN_SNR_DB} dB)")
            return False 
        
        print(f"✅ Accepted: SNR {snr:.2f} dB | Dur {duration:.2f}s")

        # 3. Clean (Wiener Filter)
        denoised_audio = self.apply_wiener_filter(raw_audio)

        # 4. Trim (VAD)
        final_audio = self.remove_silence(denoised_audio)

        # 5. Save (Always as .wav)
        sf.write(output_path, final_audio, TARGET_SAMPLE_RATE)
        return True

# --- BATCH PROCESSING BLOCK ---
if __name__ == "__main__":
    processor = AudioETL()
    
    # Folders
    input_root = "raw_data"
    output_root = "processed_data"

    print(f"🚀 Starting ETL Pipeline...")
    
    accepted_count = 0
    rejected_count = 0

    # Recursive Walk (finds PD/Patient_01/etc.)
    for root, dirs, files in os.walk(input_root):
        
        # --- FOLDER LOGIC (Moved here for optimization) ---
        # 1. Calculate path relative to 'raw_data'
        relative_path = os.path.relpath(root, input_root)
        
        # 2. Create output folder structure
        final_output_dir = os.path.join(output_root, relative_path)
        if not os.path.exists(final_output_dir):
            os.makedirs(final_output_dir)

        for filename in files:
            if filename.lower().endswith(('.wav', '.mp3', '.m4a')):
                
                input_path = os.path.join(root, filename)

                # 3. Force .wav Extension (Standardization)
                filename_stem = os.path.splitext(filename)[0]
                output_path = os.path.join(final_output_dir, f"clean_{filename_stem}.wav")
                
                # Run Pipeline
                print(f"Processing: {relative_path}/{filename}...", end=" ")
                success = processor.run_pipeline(input_path, output_path)
                
                if success:
                    accepted_count += 1
                else:
                    rejected_count += 1

    print(f"\n📊 FINAL REPORT:")
    print(f"   - Total Accepted: {accepted_count}")
    print(f"   - Total Rejected: {rejected_count}")
    print("Check 'processed_data' - All files are now standard .wav")