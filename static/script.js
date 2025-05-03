document.getElementById('posterForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const loading = document.querySelector('.loading');
    const result = document.querySelector('.result-container');
    
    // Show loading
    loading.style.display = 'block';
    result.style.display = 'none';
    
    try {
        const formData = new FormData(form);
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.details || errorData.error || 'Failed to generate poster');
        }
        
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        
        // Get the poster ID from the response headers
        const posterId = response.headers.get('X-Poster-ID');
        const posterPath = `generated/${posterId}.jpg`;
        
        // Update the UI
        document.getElementById('posterImage').src = imageUrl;
        document.getElementById('movieTitle').textContent = formData.get('title');
        document.getElementById('movieDirector').textContent = `Directed by ${formData.get('director')}`;
        document.getElementById('movieGenre').textContent = formData.get('genre').toUpperCase();
        
        // Get the description from the response headers
        const shortDescription = response.headers.get('X-Short-Description');
        const longDescription = response.headers.get('X-Long-Description');
        
        document.getElementById('movieDescription').textContent = shortDescription;
        document.getElementById('movieSynopsis').textContent = longDescription;

        // Handle theme music
        const genre = formData.get('genre');
        const themeMusic = document.getElementById('themeMusic');
        const volumeSlider = document.getElementById('volumeSlider');
        const audioContainer = document.querySelector('.audio-controls');
        
        // Create play button if it doesn't exist
        let playButton = document.createElement('button');
        playButton.className = 'play-button';
        playButton.innerHTML = '<i class="fas fa-play"></i> Play Theme';
        audioContainer.insertBefore(playButton, audioContainer.firstChild);

        // Reset audio player state
        themeMusic.pause();
        themeMusic.currentTime = 0;
        playButton.innerHTML = '<i class="fas fa-play"></i> Play Theme';
        
        // Set up audio with error handling
        const audioUrl = `/audio/${genre}`;  // Use the Flask route
        console.log('Loading audio from:', audioUrl);
        
        // Remove the default controls since we're using custom controls
        themeMusic.removeAttribute('controls');
        themeMusic.src = audioUrl;
        themeMusic.volume = volumeSlider.value;
        themeMusic.preload = 'auto';

        // Add detailed event listeners for debugging
        themeMusic.addEventListener('loadstart', () => {
            console.log('Audio loading started');
            playButton.disabled = true;
            playButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        });

        themeMusic.addEventListener('loadedmetadata', () => {
            console.log('Audio metadata loaded:', {
                duration: themeMusic.duration,
                type: themeMusic.type
            });
        });

        themeMusic.addEventListener('canplay', () => {
            console.log('Audio can start playing');
            playButton.disabled = false;
            playButton.innerHTML = '<i class="fas fa-play"></i> Play Theme';
        });

        themeMusic.addEventListener('loadeddata', () => {
            console.log('Audio loaded successfully');
            playButton.disabled = false;
        });

        themeMusic.addEventListener('error', (e) => {
            const error = themeMusic.error;
            console.error('Error loading audio:', {
                code: error.code,
                message: error.message,
                details: {
                    MEDIA_ERR_ABORTED: error.MEDIA_ERR_ABORTED,
                    MEDIA_ERR_NETWORK: error.MEDIA_ERR_NETWORK,
                    MEDIA_ERR_DECODE: error.MEDIA_ERR_DECODE,
                    MEDIA_ERR_SRC_NOT_SUPPORTED: error.MEDIA_ERR_SRC_NOT_SUPPORTED
                }
            });
            playButton.disabled = true;
            playButton.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error';
            alert('Error loading audio. Please try again.');
        });
        
        // Add volume control
        volumeSlider.addEventListener('input', (e) => {
            themeMusic.volume = e.target.value;
            console.log('Volume changed to:', e.target.value);
        });

        // Handle play/pause with better error handling
        let isPlaying = false;

        playButton.addEventListener('click', async () => {
            console.log('Play button clicked');
            try {
                if (!isPlaying) {
                    playButton.disabled = true; // Prevent multiple clicks
                    console.log('Attempting to play audio...');
                    await themeMusic.play();
                    console.log('Audio playing successfully');
                    isPlaying = true;
                    playButton.innerHTML = '<i class="fas fa-pause"></i> Pause';
                } else {
                    console.log('Pausing audio...');
                    themeMusic.pause();
                    isPlaying = false;
                    playButton.innerHTML = '<i class="fas fa-play"></i> Play Theme';
                }
            } catch (error) {
                console.error('Error playing audio:', error);
                isPlaying = false;
                playButton.innerHTML = '<i class="fas fa-play"></i> Play Theme';
                alert('Error playing audio. Please try again.');
            } finally {
                playButton.disabled = false;
            }
        });

        // Update play button state when audio ends
        themeMusic.addEventListener('ended', () => {
            console.log('Audio playback ended');
            isPlaying = false;
            playButton.innerHTML = '<i class="fas fa-play"></i> Play Theme';
        });
        
        // Show the result
        result.style.display = 'block';
        
        // Save the poster to the database
        try {
            const saveResponse = await fetch('/save_poster', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: formData.get('title'),
                    director: formData.get('director'),
                    genre: formData.get('genre'),
                    image_path: posterPath,
                    description: shortDescription,
                    synopsis: longDescription,
                    layout: JSON.parse(response.headers.get('X-Layout') || '{}'),
                    colors: JSON.parse(response.headers.get('X-Color-Palette') || '[]')
                })
            });
            
            if (!saveResponse.ok) {
                console.error('Failed to save poster to database');
            }
        } catch (error) {
            console.error('Error saving poster:', error);
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Failed to generate poster. Please try again.');
    } finally {
        loading.style.display = 'none';
    }
}); 