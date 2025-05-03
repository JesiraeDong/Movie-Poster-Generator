console.log('Script starting...');

let posterElements = {
    movies: [
        {
            title: "Lost in Translation",
            director: "Sofia Coppola",
            year: "2003",
            image: "https://picsum.photos/800/600?random=1"
        },
        {
            title: "Lady Bird",
            director: "Greta Gerwig",
            year: "2017",
            image: "https://picsum.photos/800/600?random=2"
        },
        {
            title: "The Piano",
            director: "Jane Campion",
            year: "1993",
            image: "https://picsum.photos/800/600?random=3"
        },
        {
            title: "Portrait of a Lady on Fire",
            director: "Céline Sciamma",
            year: "2019",
            image: "https://picsum.photos/800/600?random=4"
        }
    ],
    layouts: ['classic', 'modern', 'minimal', '3d'],
    currentFont: 'Arial',
    dominantColor: '#000000',
    rotation: 0,
    currentLayout: 'classic'
};

let words = [
    'Lost in Translation', 'Sofia Coppola', '2003',
    'Lady Bird', 'Greta Gerwig', '2017',
    'The Piano', 'Jane Campion', '1993',
    'Portrait of a Lady on Fire', 'Céline Sciamma', '2019',
    'Director', 'Film', 'Cinema', 'Art', 'Story', 'Vision',
    'Female', 'Perspective', 'Narrative', 'Voice', 'Power'
];

let wordCount = 40;
let hue;
let floatingWords = [];
let currentMovie;
let currentPoster;
let themes = {
    rebirth: ["awakening", "transformation", "new beginning", "metamorphosis"],
    revenge: ["betrayal", "justice", "retribution", "vengeance"],
    sisterhood: ["unity", "friendship", "support", "connection"],
    isolation: ["solitude", "loneliness", "separation", "disconnect"]
};

let settings = {
    romance: ["a moonlit garden", "a charming bookstore", "a Parisian cafe"],
    scifi: ["a neon-lit metropolis", "an AI-dominated world", "a distant galaxy"],
    thriller: ["an abandoned hospital", "a foggy street", "a mysterious mansion"],
    fantasy: ["an enchanted forest", "a magical kingdom", "ancient ruins"]
};

let particles = [];
let posterImages = {};
let backgroundMusic = {};

// Preload images and sounds
function preload() {
    // Load sample poster images for each genre
    posterImages = {
        romance: [
            loadImage('assets/images/romance/poster1.jpg'),
            loadImage('assets/images/romance/poster2.jpg')
        ],
        scifi: [
            loadImage('assets/images/scifi/poster1.jpg'),
            loadImage('assets/images/scifi/poster2.jpg')
        ],
        thriller: [
            loadImage('assets/images/thriller/poster1.jpg'),
            loadImage('assets/images/thriller/poster2.jpg')
        ],
        fantasy: [
            loadImage('assets/images/fantasy/poster1.jpg'),
            loadImage('assets/images/fantasy/poster2.jpg')
        ]
    };

    // Load audio files
    backgroundMusic = {
        romance: loadSound('assets/audio/romance.mp3'),
        scifi: loadSound('assets/audio/scifi.mp3'),
        thriller: loadSound('assets/audio/thriller.mp3'),
        fantasy: loadSound('assets/audio/fantasy.mp3')
    };
}

// Class for floating words
class FloatingWord {
    constructor() {
        this.x = random(width);
        this.y = random(height);
        this.word = random(words);
        this.size = random(12, 36);
        this.speedX = random(-1, 1);
        this.speedY = random(-1, 1);
        this.rotation = random(-0.3, 0.3);
    }

    move() {
        this.x += this.speedX;
        this.y += this.speedY;
        
        // Bounce off edges
        if (this.x < 0 || this.x > width) this.speedX *= -1;
        if (this.y < 0 || this.y > height) this.speedY *= -1;
    }

    display() {
        push();
        translate(this.x, this.y);
        rotate(this.rotation);
        textSize(this.size);
        text(this.word, 0, 0);
        pop();
    }
}

function setup() {
    console.log('Setup running...');
    let canvas = createCanvas(800, 600);
    canvas.parent('canvasContainer');
    
    // Set text properties
    textAlign(CENTER, CENTER);
    colorMode(HSB);
    textFont('Space Mono');
    
    // Initialize floating words
    for (let i = 0; i < wordCount; i++) {
        floatingWords.push(new FloatingWord());
    }
    
    // Initialize particles
    for (let i = 0; i < 50; i++) {
        particles.push(new Particle());
    }
    
    // Add event listeners
    document.getElementById('generateBtn').addEventListener('click', function() {
        console.log('Generate button clicked');
        stopAllSounds();
        generatePoster();
    });
    
    // Initial generation
    generatePoster();
    
    // Only add these if the elements exist
    const colorPicker = document.getElementById('colorPicker');
    if (colorPicker) {
        colorPicker.addEventListener('input', function(e) {
            hue = map(parseInt(e.target.value.substr(1), 16), 0, 16777215, 0, 360);
            generatePoster();
        });
    }
    
    const fontSelect = document.getElementById('fontSelect');
    if (fontSelect) {
        fontSelect.addEventListener('change', function(e) {
            textFont(e.target.value);
            generatePoster();
        });
    }
}

function draw() {
    // Get current genre
    let genre = document.getElementById('genreSelect').value;
    
    // Draw base image
    if (posterImages[genre] && posterImages[genre][0]) {
        // Draw the base poster image with a blend mode
        push();
        tint(255, 200); // Slightly transparent
        image(posterImages[genre][0], 0, 0, width, height);
        pop();
    }

    // Add overlay
    fill(0, 0, 20, 0.3);
    rect(0, 0, width, height);

    // Draw particles
    particles.forEach(p => {
        p.move();
        p.display();
    });

    // Draw floating words
    floatingWords.forEach(word => {
        word.move();
        word.display();
    });

    // Draw poster content
    if (currentMovie) {
        // Draw shimmering overlay
        drawShimmer();
        
        // Draw central content area
        fill(0, 0, 20, 0.7);
        rectMode(CENTER);
        rect(width/2, height/2, width * 0.8, height * 0.6);
        
        // Draw title
        push();
        textSize(48);
        fill(255);
        let yOffset = sin(frameCount * 0.02) * 10;
        text(currentMovie.title, width/2, height/2 - 50 + yOffset);
        
        // Draw director
        textSize(24);
        text(`Directed by ${currentMovie.director}`, width/2, height/2 + 20 + yOffset);
        
        // Draw description
        textSize(16);
        text(currentMovie.description, width/2, height/2 + 80, width * 0.7);
        pop();
    }
}

function generatePoster() {
    let genre = document.getElementById('genreSelect').value;
    let theme = document.getElementById('themeSelect').value;
    
    // Generate movie data
    currentMovie = {
        title: generateTitle(theme),
        director: document.getElementById('directorSelect').options[
            document.getElementById('directorSelect').selectedIndex
        ].text,
        genre: genre,
        description: generateDescription(genre, theme),
        year: 2024
    };

    // Play theme music
    playThemeMusic(genre);

    // Generate new floating words
    generateFloatingWords();

    // Add to gallery
    addToGallery(currentMovie);
}

function generateDescription(genre, theme) {
    const settings = {
        romance: ["a moonlit garden", "a charming bookstore", "a Parisian cafe"],
        scifi: ["a neon-lit metropolis", "an AI-dominated world", "a distant galaxy"],
        thriller: ["an abandoned hospital", "a foggy street", "a mysterious mansion"],
        fantasy: ["an enchanted forest", "a magical kingdom", "ancient ruins"]
    };

    const themes = {
        rebirth: ["awakening", "transformation", "new beginning"],
        revenge: ["betrayal", "justice", "retribution"],
        sisterhood: ["unity", "friendship", "support"],
        isolation: ["solitude", "loneliness", "separation"]
    };

    return `In ${random(settings[genre])}, a story of ${random(themes[theme])} unfolds...`;
}

function generateTitle(theme) {
    const adjectives = {
        rebirth: ["Eternal", "Rising", "New", "Reborn"],
        revenge: ["Dark", "Cold", "Silent", "Hidden"],
        sisterhood: ["Sacred", "Eternal", "Unbreakable", "Divine"],
        isolation: ["Lost", "Alone", "Silent", "Empty"]
    };
    
    const nouns = {
        rebirth: ["Dawn", "Phoenix", "Spring", "Light"],
        revenge: ["Shadow", "Justice", "Vengeance", "Night"],
        sisterhood: ["Sisters", "Bond", "Circle", "Hearts"],
        isolation: ["Echo", "Island", "Walls", "Distance"]
    };
    
    return `${random(adjectives[theme])} ${random(nouns[theme])}`;
}

function playThemeMusic(genre) {
    stopAllSounds();
    if (backgroundMusic[genre]) {
        backgroundMusic[genre].loop();
    }
}

function stopAllSounds() {
    Object.values(backgroundMusic).forEach(sound => {
        if (sound.isPlaying()) {
            sound.stop();
        }
    });
}

function addToGallery(movie) {
    const gallery = document.getElementById('gallery');
    const item = document.createElement('div');
    item.className = 'gallery-item';
    item.innerHTML = `
        <h3>${movie.title}</h3>
        <p>${movie.description}</p>
        <p><small>Directed by ${movie.director}</small></p>
        <button onclick="playThemeMusic('${movie.genre}')">▶ Play Theme</button>
    `;
    gallery.prepend(item);
}

// Genre-specific drawing functions
function drawRomanticElements() {
    // Soft, curved lines and hearts
    stroke(0, 0, 100, 0.5);
    noFill();
    for(let i = 0; i < 5; i++) {
        bezier(
            random(width), random(height),
            random(width), random(height),
            random(width), random(height),
            random(width), random(height)
        );
    }
}

function drawSciFiElements() {
    // Grid and geometric shapes
    stroke(0, 0, 100, 0.5);
    for(let i = 0; i < 20; i++) {
        line(random(width), 0, random(width), height);
        line(0, random(height), width, random(height));
    }
}

function drawThrillerElements() {
    // Sharp angles and dark elements
    stroke(0, 0, 100, 0.3);
    for(let i = 0; i < 10; i++) {
        let x1 = random(width);
        let y1 = random(height);
        line(x1, y1, x1 + random(-100, 100), y1 + random(-100, 100));
    }
}

function drawFantasyElements() {
    // Swirls and stars
    stroke(0, 0, 100, 0.5);
    for(let i = 0; i < 20; i++) {
        let x = random(width);
        let y = random(height);
        let size = random(2, 5);
        star(x, y, size);
    }
}

function star(x, y, size) {
    push();
    translate(x, y);
    rotate(random(TWO_PI));
    for(let i = 0; i < 5; i++) {
        line(0, 0, 0, size);
        rotate(TWO_PI/5);
    }
    pop();
}

function drawDecorations() {
    stroke(hue, 100, 90);
    noFill();
    
    // Draw circles
    for (let i = 0; i < 8; i++) {
        let size = random(100, 300);
        let x = random(width);
        let y = random(height);
        circle(x, y, size);
    }
    
    // Draw lines
    for (let i = 0; i < 15; i++) {
        let x1 = random(width);
        let y1 = random(height);
        let x2 = x1 + random(-200, 200);
        let y2 = y1 + random(-200, 200);
        line(x1, y1, x2, y2);
    }
}

function drawPoster(img, movie, layout) {
    if (layout === '3d') {
        if (currentImage) {
            graphics.background(250, 180, 200);
            graphics.image(currentImage, 0, 0, width, height);
        }
        return;
    }
    
    graphics.background(255);
    graphics.textFont(posterElements.currentFont);
    
    switch(layout) {
        case 'classic':
            drawClassicLayout(img, movie);
            break;
        case 'modern':
            drawModernLayout(img, movie);
            break;
        case 'minimal':
            drawMinimalLayout(img, movie);
            break;
    }
}

function drawClassicLayout(img, movie) {
    // Draw image with tint of selected color
    let c = color(posterElements.dominantColor);
    graphics.tint(red(c), green(c), blue(c), 150);
    graphics.image(img, 0, 0, width, height);
    graphics.noTint();
    
    // Add gradient overlay
    for(let y = 0; y < height; y++) {
        let alpha = map(y, 0, height, 0, 150);
        graphics.fill(red(c), green(c), blue(c), alpha);
        graphics.noStroke();
        graphics.rect(0, y, width, 1);
    }
    
    // Add text
    graphics.fill(255);
    graphics.textSize(64);
    graphics.textAlign(CENTER, CENTER);
    graphics.text(movie.title, width/2, height/2);
    graphics.textSize(32);
    graphics.text(movie.director, width/2, height/2 + 60);
    graphics.textSize(24);
    graphics.text(movie.year, width/2, height/2 + 100);
}

function drawModernLayout(img, movie) {
    // Split screen design
    graphics.image(img, 0, 0, width/2, height);
    graphics.fill(posterElements.dominantColor);
    graphics.rect(width/2, 0, width/2, height);
    
    // Add text
    graphics.fill(255);
    graphics.textSize(48);
    graphics.textAlign(LEFT, CENTER);
    graphics.text(movie.title, width/2 + 30, height/2);
    graphics.textSize(24);
    graphics.text(movie.director, width/2 + 30, height/2 + 50);
    graphics.text(movie.year, width/2 + 30, height/2 + 80);
}

function drawMinimalLayout(img, movie) {
    // Background with dominant color
    graphics.background(posterElements.dominantColor);
    
    // Smaller image
    let imgSize = min(width, height) * 0.6;
    let imgX = (width - imgSize) / 2;
    let imgY = (height - imgSize) / 2;
    graphics.image(img, imgX, imgY, imgSize, imgSize);
    
    // Text below
    graphics.fill(255);
    graphics.textAlign(CENTER, CENTER);
    graphics.textSize(32);
    graphics.text(movie.title, width/2, imgY + imgSize + 40);
    graphics.textSize(20);
    graphics.text(`${movie.director}, ${movie.year}`, width/2, imgY + imgSize + 70);
}

function draw3DPoster() {
    background(250, 180, 200);
    orbitControl();
    
    // Draw the movie image as background
    if (currentImage) {
        push();
        translate(0, 0, -500);
        texture(currentImage);
        plane(width, height);
        pop();
    }
    
    // Create a sphere of floating movie images
    for (let zAngle = 0; zAngle < 180; zAngle += 45) {
        for (let xAngle = 0; xAngle < 360; xAngle += 45) {
            push();
            
            rotateZ(zAngle + posterElements.rotation);
            rotateX(xAngle + posterElements.rotation);
            translate(0, 200, 0);
            
            // Draw movie image as a textured plane
            if (currentImage) {
                push();
                texture(currentImage);
                noStroke();
                // Make the floating images smaller
                plane(100, 75);
                pop();
            }
            
            pop();
        }
    }

    // Increment rotation for animation
    posterElements.rotation += 0.5;

    // Draw movie title in 3D space with better visibility
    if (currentMovie) {
        push();
        translate(0, 0, 200);
        // Add a background rectangle for better text visibility
        push();
        fill(250, 180, 200, 200);
        noStroke();
        translate(0, 20, -10);
        plane(400, 100);
        pop();
        
        textSize(32);
        textAlign(CENTER, CENTER);
        fill(32, 8, 64);
        text(currentMovie.title, 0, 0);
        translate(0, 40, 0);
        textSize(16);
        text(currentMovie.director + ', ' + currentMovie.year, 0, 0);
        pop();
    }
} 