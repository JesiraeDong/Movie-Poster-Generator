from flask import Flask, render_template, request, send_file, jsonify, session
from PIL import Image, ImageDraw, ImageFont
import os
import random
from io import BytesIO
import logging
from datetime import datetime
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import json
from sklearn.cluster import KMeans
import numpy as np
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create necessary directories
def ensure_directories():
    directories = [
        'assets/images',
        'assets/images/romance',
        'assets/images/scifi',
        'assets/images/thriller',
        'assets/images/fantasy',
        'static/generated'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Call this function when the app starts
ensure_directories()

# Database Models
class Poster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    synopsis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    layout_data = db.Column(db.Text)  # JSON string of layout information
    color_palette = db.Column(db.Text)  # JSON string of color palette

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.Integer, db.ForeignKey('poster.id'), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)  # Using session ID for simplicity
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Configuration
UPLOAD_FOLDER = 'assets/images'
GENRES = ['romance', 'scifi', 'thriller', 'fantasy']
FONT_PATH = '/System/Library/Fonts/Helvetica.ttc'  # macOS system font

# Movie description templates
DESCRIPTION_TEMPLATES = {
    'romance': [
        "A heartfelt journey of love and self-discovery in {setting}.",
        "When {character1} meets {character2}, their lives are forever changed.",
        "A story of passion, sacrifice, and the power of love.",
        "In a world where love seems impossible, {character1} finds hope.",
        "A tale of two souls destined to find each other against all odds."
    ],
    'scifi': [
        "In a future where {setting}, humanity faces its greatest challenge.",
        "A groundbreaking discovery leads to an unexpected adventure.",
        "When technology and humanity collide, {character1} must choose a side.",
        "A journey through time and space that will change everything.",
        "In a world transformed by {setting}, survival depends on adaptation."
    ],
    'thriller': [
        "When {character1} discovers {discovery}, nothing will ever be the same.",
        "A dark secret threatens to unravel everything {character1} knows.",
        "In the shadows of {setting}, a dangerous game of cat and mouse unfolds.",
        "As {character1} digs deeper into {discovery}, the truth becomes more terrifying.",
        "A race against time to prevent {discovery} from destroying everything."
    ],
    'fantasy': [
        "In a world of magic and wonder, {character1} embarks on an epic quest.",
        "When {discovery} is revealed, {character1} must embrace their destiny.",
        "A journey through enchanted realms where anything is possible.",
        "In a land where {setting}, one person can change everything.",
        "A tale of courage, magic, and the power of belief."
    ]
}

# Character and setting templates
CHARACTERS = [
    "a mysterious stranger", "an unlikely hero", "a brilliant scientist", 
    "a determined detective", "a reluctant warrior", "a gifted artist",
    "a troubled soul", "a wise mentor", "a rebellious youth", "a lost wanderer"
]

SETTINGS = {
    'romance': [
        "a bustling city", "a quiet coastal town", "a vibrant metropolis", 
        "a picturesque countryside", "a historic neighborhood", "a remote island"
    ],
    'scifi': [
        "artificial intelligence controls society", "space travel is commonplace", 
        "climate change has reshaped the planet", "virtual reality replaces reality",
        "humanity has colonized distant planets", "robots and humans coexist uneasily"
    ],
    'thriller': [
        "a corrupt government", "a powerful corporation", "a secret society", 
        "a lawless city", "a remote research facility", "a high-security prison"
    ],
    'fantasy': [
        "ancient magic still exists", "mythical creatures roam freely", 
        "gods walk among mortals", "magic and technology coexist", 
        "legendary artifacts hold immense power", "different realms are connected"
    ]
}

DISCOVERIES = [
    "a hidden truth", "an ancient artifact", "a forbidden knowledge", 
    "a mysterious signal", "a lost civilization", "a powerful secret",
    "a forgotten prophecy", "a dangerous technology", "a supernatural force",
    "a world-altering revelation"
]

# Detailed synopsis templates
SYNOPSIS_TEMPLATES = {
    'romance': [
        "In {setting}, {character1} leads a seemingly perfect life until fate intervenes. When {character2} enters the picture, everything {character1} thought they knew about love and happiness is turned upside down. As they navigate the complexities of their growing connection, they must confront their pasts, challenge their fears, and decide if love is worth the risk. Through moments of joy, heartbreak, and self-discovery, they learn that true love often requires courage, vulnerability, and the willingness to change.",
        "Set against the backdrop of {setting}, this compelling love story follows {character1} as they encounter {character2} in the most unexpected of circumstances. What begins as a chance meeting evolves into a profound connection that challenges both characters to question their life choices and personal boundaries. As they grow closer, they must overcome external obstacles and internal conflicts, discovering that the greatest journey of love is the one that leads to self-acceptance and genuine connection."
    ],
    'scifi': [
        "In a future where {setting}, {character1} stands at the crossroads of humanity's destiny. When {discovery} emerges, it becomes clear that the fate of civilization hangs in the balance. As {character1} delves deeper into this revelation, they must navigate a complex web of political intrigue, ethical dilemmas, and personal sacrifice. The journey leads to a profound understanding of what it means to be human in a world increasingly dominated by technology and artificial intelligence.",
        "The discovery of {discovery} in {setting} sets off a chain of events that will forever alter the course of human history. {character1}, thrust into the center of this paradigm shift, must grapple with the implications of this breakthrough while facing opposition from those who fear change. As the story unfolds, themes of progress, responsibility, and the human condition are explored against a backdrop of advanced technology and shifting societal norms."
    ],
    'thriller': [
        "When {character1} stumbles upon {discovery} in {setting}, they become entangled in a dangerous web of conspiracy and deception. As they dig deeper, each revelation leads to more questions, and the line between allies and enemies becomes increasingly blurred. With time running out and the stakes growing higher, {character1} must navigate a treacherous path where trust is a luxury and survival is the only priority. The truth, when finally revealed, proves to be more shocking than anyone could have imagined.",
        "In the heart of {setting}, {character1} uncovers {discovery}, setting off a chain of events that will test their limits and challenge their beliefs. As they race against time to prevent a catastrophic outcome, they must outmaneuver powerful adversaries and decipher a complex puzzle where nothing is as it seems. The journey leads to a shocking revelation that forces {character1} to question everything they thought they knew about right and wrong."
    ],
    'fantasy': [
        "In a realm where {setting}, {character1} embarks on an extraordinary journey that will determine the fate of their world. When {discovery} is revealed, it becomes clear that they are destined for a greater purpose than they ever imagined. Through trials and tribulations, {character1} must harness newfound powers, forge unlikely alliances, and confront their deepest fears. As the story unfolds, ancient prophecies are fulfilled, and the line between myth and reality becomes increasingly blurred.",
        "The discovery of {discovery} in a world where {setting} sets {character1} on a path that will challenge everything they believe in. As they navigate through enchanted realms and face increasingly difficult trials, they must learn to embrace their unique abilities and the responsibility that comes with them. The journey leads to an epic confrontation where the fate of multiple worlds hangs in the balance, and {character1} must make the ultimate sacrifice to restore balance to their realm."
    ]
}

def generate_description(title, director, genre):
    """Generate a short movie description based on the title, director, and genre."""
    template = random.choice(DESCRIPTION_TEMPLATES[genre])
    character1 = random.choice(CHARACTERS)
    character2 = random.choice([c for c in CHARACTERS if c != character1])
    setting = random.choice(SETTINGS[genre])
    discovery = random.choice(DISCOVERIES)
    
    return template.format(
        character1=character1,
        character2=character2,
        setting=setting,
        discovery=discovery
    )

def generate_synopsis(title, director, genre):
    """Generate a detailed movie synopsis based on the title, director, and genre."""
    template = random.choice(SYNOPSIS_TEMPLATES[genre])
    character1 = random.choice(CHARACTERS)
    character2 = random.choice([c for c in CHARACTERS if c != character1])
    setting = random.choice(SETTINGS[genre])
    discovery = random.choice(DISCOVERIES)
    
    return template.format(
        character1=character1,
        character2=character2,
        setting=setting,
        discovery=discovery
    )

def get_random_posters(genre, count=3):
    """Get random posters from the specified genre."""
    genre_path = os.path.join(UPLOAD_FOLDER, genre)
    posters = [f for f in os.listdir(genre_path) if f.endswith('.jpg')]
    if posters:
        selected = random.sample(posters, min(count, len(posters)))
        return [os.path.join(genre_path, poster) for poster in selected]
    return []

def extract_random_region(image, min_size=200, max_size=400):
    """Extract a random region from the image, avoiding text areas."""
    width, height = image.size
    
    # Define regions to avoid (typically where text appears)
    avoid_regions = [
        (0, 0, width, height * 0.2),  # Top area (title)
        (0, height * 0.8, width, height),  # Bottom area (credits)
        (0, 0, width * 0.2, height),  # Left edge
        (width * 0.8, 0, width, height)  # Right edge
    ]
    
    # Try to find a region that doesn't overlap with text areas
    max_attempts = 10
    for _ in range(max_attempts):
        region_width = random.randint(min_size, max_size)
        region_height = random.randint(min_size, max_size)
        
        x = random.randint(0, width - region_width)
        y = random.randint(0, height - region_height)
        
        # Check if the region overlaps with any avoid regions
        region = (x, y, x + region_width, y + region_height)
        if not any(overlaps(region, avoid) for avoid in avoid_regions):
            return image.crop(region)
    
    # If no suitable region found, return a random region
    x = random.randint(0, width - min_size)
    y = random.randint(0, height - min_size)
    return image.crop((x, y, x + min_size, y + min_size))

def overlaps(region1, region2):
    """Check if two regions overlap."""
    x1, y1, w1, h1 = region1
    x2, y2, w2, h2 = region2
    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

def create_collage_poster(background_images, title, director, genre, description):
    """Create a collage-style movie poster with the given parameters."""
    # Create a blank canvas with a gradient background
    canvas = Image.new('RGB', (600, 900), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    # Create a gradient background based on genre
    gradient_colors = {
        'romance': [(255, 192, 203), (255, 105, 180)],  # Pink gradient
        'scifi': [(0, 191, 255), (0, 0, 139)],  # Blue gradient
        'thriller': [(47, 79, 79), (0, 0, 0)],  # Dark gradient
        'fantasy': [(147, 112, 219), (75, 0, 130)]  # Purple gradient
    }
    
    # Apply gradient background
    color1, color2 = gradient_colors.get(genre, [(0, 0, 0), (0, 0, 0)])
    for y in range(900):
        r = int(color1[0] + (color2[0] - color1[0]) * y / 900)
        g = int(color1[1] + (color2[1] - color1[1]) * y / 900)
        b = int(color1[2] + (color2[2] - color1[2]) * y / 900)
        draw.line([(0, y), (600, y)], fill=(r, g, b))
    
    # Add semi-transparent overlay
    overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 100))
    canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay)
    canvas = canvas.convert('RGB')
    
    # Create a new drawing context
    draw = ImageDraw.Draw(canvas)
    
    # Extract and place random regions from each background image
    for img_path in background_images:
        try:
            img = Image.open(img_path)
            img = img.resize((600, 900), Image.LANCZOS)
            
            # Extract 2-3 random regions from each image
            num_regions = random.randint(2, 3)
            for _ in range(num_regions):
                region = extract_random_region(img)
                
                # Randomly position the region on the canvas
                x = random.randint(0, 600 - region.width)
                y = random.randint(0, 900 - region.height)
                
                # Apply a random rotation
                angle = random.randint(-30, 30)
                region = region.rotate(angle, expand=True, resample=Image.BICUBIC)
                
                # Create a mask for the region
                mask = Image.new('L', region.size, 128)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rectangle([(0, 0), region.size], fill=180)
                
                # Paste the region onto the canvas with the mask
                canvas.paste(region, (x, y), mask)
        except Exception as e:
            print(f"Error processing image {img_path}: {str(e)}")
    
    # Add a semi-transparent overlay to improve text readability
    overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 150))
    canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay)
    canvas = canvas.convert('RGB')
    
    # Create a new drawing context
    draw = ImageDraw.Draw(canvas)
    
    # Try to load custom font, fall back to default if not available
    try:
        title_font = ImageFont.truetype(FONT_PATH, 60)
        subtitle_font = ImageFont.truetype(FONT_PATH, 30)
        description_font = ImageFont.truetype(FONT_PATH, 24)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        description_font = ImageFont.load_default()
    
    # Add text
    # Title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (600 - title_width) // 2
    draw.text((title_x, 650), title, font=title_font, fill=(255, 255, 255))
    
    # Description (wrapped text)
    words = description.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), line, font=description_font)
        if bbox[2] - bbox[0] > 550:  # If line is too long
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw description lines
    y_position = 700
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=description_font)
        line_width = bbox[2] - bbox[0]
        x_position = (600 - line_width) // 2
        draw.text((x_position, y_position), line, font=description_font, fill=(255, 255, 255))
        y_position += 30
    
    # Director
    director_text = f"Directed by {director}"
    director_bbox = draw.textbbox((0, 0), director_text, font=subtitle_font)
    director_width = director_bbox[2] - director_bbox[0]
    director_x = (600 - director_width) // 2
    draw.text((director_x, 830), director_text, font=subtitle_font, fill=(255, 255, 255))
    
    # Genre
    genre_text = genre.upper()
    genre_bbox = draw.textbbox((0, 0), genre_text, font=subtitle_font)
    genre_width = genre_bbox[2] - genre_bbox[0]
    genre_x = (600 - genre_width) // 2
    draw.text((genre_x, 870), genre_text, font=subtitle_font, fill=(255, 255, 255))
    
    return canvas

@app.route('/')
def index():
    return render_template('index.html', genres=GENRES)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        logger.debug("Received generate request")
        title = request.form['title']
        director = request.form['director']
        genre = request.form['genre']
        
        logger.debug(f"Title: {title}, Director: {director}, Genre: {genre}")
        
        # Generate descriptions
        short_description = generate_description(title, director, genre)
        long_description = generate_synopsis(title, director, genre)
        
        logger.debug(f"Generated descriptions - Short: {short_description}")
        
        # Get random background images from selected genre
        background_images = get_random_posters(genre, count=3)
        logger.debug(f"Selected background images: {background_images}")
        
        if not background_images:
            logger.error("No background images available")
            return jsonify({
                'error': 'No background images available for this genre',
                'details': 'Please ensure there are images in the assets/images/{genre} directory'
            }), 400
        
        # Create the poster
        try:
            poster = create_collage_poster(background_images, title, director, genre, short_description)
            logger.debug("Poster created successfully")
        except Exception as e:
            logger.error(f"Error creating poster: {str(e)}")
            return jsonify({
                'error': 'Failed to create poster',
                'details': str(e)
            }), 500
        
        # Save to BytesIO object
        img_io = BytesIO()
        poster.save(img_io, 'JPEG')
        img_io.seek(0)
        
        # Get color palette
        try:
            color_palette = get_color_palette(poster)
        except Exception as e:
            logger.error(f"Error generating color palette: {str(e)}")
            color_palette = []
        
        # Optimize layout
        try:
            layout = optimize_layout(poster.size, title, director, genre)
        except Exception as e:
            logger.error(f"Error optimizing layout: {str(e)}")
            layout = {}
        
        # Create response with custom headers
        response = send_file(img_io, mimetype='image/jpeg')
        response.headers['X-Short-Description'] = short_description
        response.headers['X-Long-Description'] = long_description
        response.headers['X-Color-Palette'] = json.dumps(color_palette)
        response.headers['X-Layout'] = json.dumps(layout)
        
        logger.debug("Response prepared successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error generating poster: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to generate poster',
            'details': str(e)
        }), 500

@app.route('/save_poster', methods=['POST'])
def save_poster():
    try:
        data = request.json
        poster = Poster(
            title=data['title'],
            director=data['director'],
            genre=data['genre'],
            image_path=data['image_path'],
            description=data['description'],
            synopsis=data['synopsis'],
            layout_data=json.dumps(data['layout']),
            color_palette=json.dumps(data['colors'])
        )
        db.session.add(poster)
        db.session.commit()
        return jsonify({'success': True, 'poster_id': poster.id})
    except Exception as e:
        logger.error(f"Error saving poster: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    try:
        poster_id = request.json['poster_id']
        user_id = session.get('user_id', str(os.urandom(16).hex()))
        session['user_id'] = user_id
        
        favorite = Favorite.query.filter_by(
            poster_id=poster_id,
            user_id=user_id
        ).first()
        
        if favorite:
            db.session.delete(favorite)
            is_favorite = False
        else:
            favorite = Favorite(poster_id=poster_id, user_id=user_id)
            db.session.add(favorite)
            is_favorite = True
            
        db.session.commit()
        return jsonify({'success': True, 'is_favorite': is_favorite})
    except Exception as e:
        logger.error(f"Error toggling favorite: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/gallery')
def gallery():
    posters = Poster.query.order_by(Poster.created_at.desc()).all()
    return render_template('gallery.html', posters=posters)

@app.route('/favorites')
def favorites():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('favorites.html', posters=[])
    
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    poster_ids = [f.poster_id for f in favorites]
    posters = Poster.query.filter(Poster.id.in_(poster_ids)).all()
    return render_template('favorites.html', posters=posters)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 