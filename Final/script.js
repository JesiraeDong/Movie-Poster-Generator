// Constants for movie generation
const THEMES = {
    rebirth: {
        settings: ["a neon-lit city", "the ruins of an ancient temple", "an AI-dominated world"],
        themes: ["redemption", "second chances", "transformation"]
    },
    revenge: {
        settings: ["a dark metropolis", "a forgotten island", "a corporate dystopia"],
        themes: ["vengeance", "justice", "betrayal"]
    },
    sisterhood: {
        settings: ["a mystical forest", "a coastal town", "an underground sanctuary"],
        themes: ["bonding", "loyalty", "strength in unity"]
    },
    isolation: {
        settings: ["a remote space station", "a deserted island", "a frozen wilderness"],
        themes: ["solitude", "self-discovery", "survival"]
    }
};

// DOM Elements
const genreSelect = document.getElementById('genre');
const directorSelect = document.getElementById('director');
const themeSelect = document.getElementById('theme');
const generateBtn = document.getElementById('generateBtn');
const posterCanvas = document.getElementById('posterCanvas');
const movieTitle = document.getElementById('movieTitle');
const movieDescription = document.getElementById('movieDescription');
const themeAudio = document.getElementById('themeAudio');
const posterGallery = document.getElementById('posterGallery');

// Store generated posters
let generatedPosters = [];

// Initialize p5.js sketch
let posterSketch = function(p) {
    let posterImages = [];
    let currentPoster = null;

    p.setup = function() {
        const canvas = p.createCanvas(600, 900);
        canvas.parent('posterCanvas');
        p.background(255);
    };

    p.draw = function() {
        if (currentPoster) {
            p.image(currentPoster, 0, 0, p.width, p.height);
        }
    };

    window.generatePoster = async function(genre, director, theme) {
        // Clear previous poster
        p.clear();
        p.background(255);

        // Load and blend poster images
        try {
            const imageCount = 2 + Math.floor(Math.random() * 2); // 2-3 images
            posterImages = [];

            for (let i = 0; i < imageCount; i++) {
                const img = await loadPosterImage(genre, i + 1);
                posterImages.push(img);
            }

            // Create collage
            currentPoster = p.createGraphics(p.width, p.height);
            currentPoster.background(255);

            posterImages.forEach((img, index) => {
                const x = p.random(-100, 100);
                const y = p.random(-100, 100);
                const scale = 0.8 + p.random(0.4);
                
                currentPoster.push();
                currentPoster.translate(x, y);
                currentPoster.scale(scale);
                currentPoster.image(img, 0, 0, p.width, p.height);
                currentPoster.pop();
            });

            // Add text overlay
            currentPoster.textSize(40);
            currentPoster.textAlign(p.CENTER);
            currentPoster.fill(255);
            currentPoster.stroke(0);
            currentPoster.strokeWeight(2);
            currentPoster.text(generateTitle(theme), p.width/2, p.height - 200);
            
            currentPoster.textSize(24);
            currentPoster.text(`Directed by ${director}`, p.width/2, p.height - 150);
            
            currentPoster.textSize(20);
            currentPoster.text(genre.toUpperCase(), p.width/2, p.height - 100);

            // Update display
            p.image(currentPoster, 0, 0);
        } catch (error) {
            console.error('Error generating poster:', error);
        }
    };
};

// Helper function to load poster images
async function loadPosterImage(genre, index) {
    return new Promise((resolve, reject) => {
        const img = new p5.Image();
        img.load(`assets/images/${genre}/poster${index}.jpg`, 
            () => resolve(img),
            () => reject(new Error(`Failed to load image: poster${index}.jpg`))
        );
    });
}

// Generate movie title based on theme
function generateTitle(theme) {
    const themeData = THEMES[theme];
    const setting = themeData.settings[Math.floor(Math.random() * themeData.settings.length)];
    const themeText = themeData.themes[Math.floor(Math.random() * themeData.themes.length)];
    
    return `${setting.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}: ${themeText.charAt(0).toUpperCase() + themeText.slice(1)}`;
}

// Generate movie description
function generateDescription(genre, director, theme) {
    const themeData = THEMES[theme];
    const setting = themeData.settings[Math.floor(Math.random() * themeData.settings.length)];
    const themeText = themeData.themes[Math.floor(Math.random() * themeData.themes.length)];
    
    return `In ${setting}, a compelling story of ${themeText} unfolds under the visionary direction of ${director}. This ${genre} masterpiece explores the depths of human emotion and the boundaries of imagination.`;
}

// Event Listeners
generateBtn.addEventListener('click', async () => {
    const genre = genreSelect.value;
    const director = directorSelect.value;
    const theme = themeSelect.value;

    if (!genre || !director || !theme) {
        alert('Please select all options');
        return;
    }

    // Generate poster
    await window.generatePoster(genre, director, theme);

    // Update movie info
    const title = generateTitle(theme);
    const description = generateDescription(genre, director, theme);
    
    movieTitle.textContent = title;
    movieDescription.textContent = description;

    // Update audio
    themeAudio.src = `assets/audio/${genre}.mp3`;
    themeAudio.play();

    // Add to gallery
    addToGallery(title, description, genre);
});

// Add poster to gallery
function addToGallery(title, description, genre) {
    const posterElement = document.createElement('div');
    posterElement.className = 'gallery-item';
    
    const posterData = {
        title,
        description,
        genre,
        timestamp: new Date().toISOString()
    };
    
    generatedPosters.unshift(posterData);
    
    posterElement.innerHTML = `
        <h3>${title}</h3>
        <p>${description}</p>
        <audio controls>
            <source src="assets/audio/${genre}.mp3" type="audio/mpeg">
        </audio>
    `;
    
    posterGallery.insertBefore(posterElement, posterGallery.firstChild);
}

// Initialize p5.js sketch
new p5(posterSketch); 