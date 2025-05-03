let canvas;
let posterElements = {
    colors: [],
    fonts: ['Arial', 'Georgia', 'Impact'],
    layouts: ['vertical', 'horizontal', 'grid'],
    images: [] // Will store our scraped images
};

function setup() {
    canvas = createCanvas(800, 600);
    canvas.parent('posterCanvas');
    
    // Set up initial colors
    posterElements.colors = [
        color(255, 0, 0),
        color(0, 255, 0),
        color(0, 0, 255),
        color(255, 255, 0),
        color(255, 0, 255)
    ];

    // Initial generation
    generatePoster();

    // Add event listeners
    document.getElementById('generateBtn').addEventListener('click', generatePoster);
    document.getElementById('saveBtn').addEventListener('click', savePoster);
    document.getElementById('colorPicker').addEventListener('change', updateColor);
    document.getElementById('fontSelect').addEventListener('change', updateFont);
}

function generatePoster() {
    background(255);
    
    // Random layout selection
    const layout = random(posterElements.layouts);
    
    // Generate based on layout
    switch(layout) {
        case 'vertical':
            generateVerticalLayout();
            break;
        case 'horizontal':
            generateHorizontalLayout();
            break;
        case 'grid':
            generateGridLayout();
            break;
    }
}

function generateVerticalLayout() {
    const mainColor = random(posterElements.colors);
    fill(mainColor);
    noStroke();
    
    // Background
    rect(0, 0, width, height);
    
    // Title area
    fill(255);
    textSize(48);
    textAlign(CENTER, CENTER);
    text('GENERATED FILM', width/2, height/3);
    
    // Director name
    textSize(24);
    text('Directed by', width/2, height/2);
}

function generateHorizontalLayout() {
    const mainColor = random(posterElements.colors);
    fill(mainColor);
    noStroke();
    
    // Split design
    rect(0, 0, width/2, height);
    fill(255);
    rect(width/2, 0, width/2, height);
    
    // Add text
    fill(255);
    textSize(36);
    textAlign(CENTER, CENTER);
    text('FILM', width/4, height/2);
    
    fill(0);
    text('2024', 3*width/4, height/2);
}

function generateGridLayout() {
    const gridSize = 4;
    const cellWidth = width/gridSize;
    const cellHeight = height/gridSize;
    
    for(let i = 0; i < gridSize; i++) {
        for(let j = 0; j < gridSize; j++) {
            fill(random(posterElements.colors));
            rect(i*cellWidth, j*cellHeight, cellWidth, cellHeight);
        }
    }
}

function savePoster() {
    saveCanvas(canvas, 'generated-poster', 'jpg');
}

function updateColor(e) {
    const newColor = color(e.target.value);
    posterElements.colors.push(newColor);
    generatePoster();
}

function updateFont(e) {
    textFont(e.target.value);
    generatePoster();
} 