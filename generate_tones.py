import numpy as np
from scipy.io import wavfile

def generate_tone(frequency, duration, sample_rate=44100):
    """Generate a simple tone."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    return np.sin(2 * np.pi * frequency * t), t

def create_wav(filename, tone, sample_rate=44100):
    """Save the tone as a WAV file."""
    # Normalize to 16-bit range
    tone = np.int16(tone * 32767)
    wavfile.write(filename, sample_rate, tone)

# Generate different tones for each genre
def generate_genre_tones():
    # Romance: soft, gentle tone
    romance, t = generate_tone(440, 3)  # A4 note
    romance *= np.exp(-t/2)  # Add fade out effect
    
    # Sci-fi: futuristic sound
    t = np.linspace(0, 3, 44100 * 3)
    scifi_high, _ = generate_tone(880, 3)
    scifi_low, _ = generate_tone(440, 3)
    scifi = scifi_high * 0.5 + scifi_low * 0.5  # Mix of two frequencies
    
    # Thriller: tense tone
    thriller, t = generate_tone(466.16, 3)  # Bb4 note
    thriller *= (1 + 0.5 * np.sin(2 * np.pi * 2 * t))  # Add tremolo effect
    
    # Fantasy: mystical tone
    fantasy_base, _ = generate_tone(523.25, 3)  # C5 note
    fantasy_high, _ = generate_tone(784.96, 3)  # G5
    fantasy = fantasy_base * 0.7 + fantasy_high * 0.3  # Mix with G5
    
    # Save all files
    create_wav('assets/audio/Chill.wav', romance)
    create_wav('assets/audio/Drama.wav', scifi)
    create_wav('assets/audio/Fantasy.wav', fantasy)

if __name__ == '__main__':
    generate_genre_tones() 