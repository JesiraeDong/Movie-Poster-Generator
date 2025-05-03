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
                    image_path: imageUrl,
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