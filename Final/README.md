# Movie Poster Generator

An interactive web application that generates unique movie posters based on user-selected genre, director, and theme. The application creates visually appealing posters by blending pre-saved movie poster assets and includes AI-generated descriptions and theme music.

## Features

- Interactive poster generation based on user inputs
- Dynamic blending of poster assets using p5.js
- AI-generated movie descriptions
- Genre-specific theme music
- Gallery view of generated posters
- Responsive design for both desktop and mobile

## Setup

1. Clone the repository
2. Create the following directory structure:
```
assets/
├── images/
│   ├── romance/
│   ├── scifi/
│   ├── thriller/
│   └── fantasy/
└── audio/
    ├── romance.mp3
    ├── scifi.mp3
    ├── thriller.mp3
    └── fantasy.mp3
```

3. Add poster images to the respective genre folders:
   - Place 4-5 poster images in each genre folder
   - Name them as `poster1.jpg`, `poster2.jpg`, etc.
   - Recommended size: 600x900 pixels

4. Add audio files:
   - Place MP3 files in the audio folder
   - Name them according to the genre (e.g., `romance.mp3`)

5. Open `index.html` in a web browser

## Usage

1. Select a genre from the dropdown menu
2. Choose a director
3. Pick a theme
4. Click "Generate" to create your poster
5. The generated poster will appear with:
   - A unique title
   - AI-generated description
   - Theme music
6. View your generated posters in the gallery below

## Technical Details

- Built with vanilla JavaScript
- Uses p5.js for image manipulation
- Responsive design using CSS Grid and Flexbox
- No external dependencies except p5.js

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Notes

- For best results, use high-quality poster images
- Audio files should be short loops (30-60 seconds)
- Poster images should be in JPG format
- Recommended image resolution: 600x900 pixels

## License

MIT License - Feel free to use and modify for your own projects. 