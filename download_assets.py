import os
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import time
import random

# Create directories if they don't exist
def create_directories():
    genres = ['romance', 'scifi', 'thriller', 'fantasy']
    for genre in genres:
        os.makedirs(f'assets/images/{genre}', exist_ok=True)
    os.makedirs('assets/audio', exist_ok=True)

# Movies directed by female directors with their IMDb IDs
MOVIES = {
    'romance': [
        {'title': 'Little Women', 'director': 'Greta Gerwig', 'imdb_id': 'tt3281548'},
        {'title': 'Clueless', 'director': 'Amy Heckerling', 'imdb_id': 'tt0112697'},
        {'title': 'Lady Bird', 'director': 'Greta Gerwig', 'imdb_id': 'tt4925292'},
        {'title': 'Lost in Translation', 'director': 'Sofia Coppola', 'imdb_id': 'tt0335266'},
        {'title': 'The Virgin Suicides', 'director': 'Sofia Coppola', 'imdb_id': 'tt0159097'},
        {'title': 'Booksmart', 'director': 'Olivia Wilde', 'imdb_id': 'tt1489887'},
        {'title': 'The Farewell', 'director': 'Lulu Wang', 'imdb_id': 'tt8637428'},
        {'title': 'The Half of It', 'director': 'Alice Wu', 'imdb_id': 'tt9683478'},
        {'title': 'Portrait of a Lady on Fire', 'director': 'Céline Sciamma', 'imdb_id': 'tt8613070'},
        {'title': 'Water Lilies', 'director': 'Céline Sciamma', 'imdb_id': 'tt0869990'},
        {'title': 'Girlhood', 'director': 'Céline Sciamma', 'imdb_id': 'tt3697020'},
        {'title': 'The Bling Ring', 'director': 'Sofia Coppola', 'imdb_id': 'tt2132285'},
        {'title': 'Somewhere', 'director': 'Sofia Coppola', 'imdb_id': 'tt1421051'},
        {'title': 'Marie Antoinette', 'director': 'Sofia Coppola', 'imdb_id': 'tt0422720'},
        {'title': 'The Beguiled', 'director': 'Sofia Coppola', 'imdb_id': 'tt5592248'}
    ],
    'scifi': [
        {'title': 'The Matrix', 'director': 'Lana & Lilly Wachowski', 'imdb_id': 'tt0133093'},
        {'title': 'The Old Guard', 'director': 'Gina Prince-Bythewood', 'imdb_id': 'tt7556122'},
        {'title': 'Cloud Atlas', 'director': 'Lana & Lilly Wachowski', 'imdb_id': 'tt1371111'},
        {'title': 'Sense8', 'director': 'Lana & Lilly Wachowski', 'imdb_id': 'tt2431438'},
        {'title': 'The Handmaid\'s Tale', 'director': 'Reed Morano', 'imdb_id': 'tt5834204'},
        {'title': 'The Power', 'director': 'Reed Morano', 'imdb_id': 'tt14209916'},
        {'title': 'Honey Boy', 'director': 'Alma Har\'el', 'imdb_id': 'tt8151874'},
        {'title': 'The Nightingale', 'director': 'Jennifer Kent', 'imdb_id': 'tt3836954'},
        {'title': 'The Babadook', 'director': 'Jennifer Kent', 'imdb_id': 'tt2321549'},
        {'title': 'Bound', 'director': 'Lana & Lilly Wachowski', 'imdb_id': 'tt0115685'},
        {'title': 'Speed Racer', 'director': 'Lana & Lilly Wachowski', 'imdb_id': 'tt0811080'},
        {'title': 'Jupiter Ascending', 'director': 'Lana & Lilly Wachowski', 'imdb_id': 'tt1617661'},
        {'title': 'The Matrix Reloaded', 'director': 'Lana & Lilly Wachowski', 'imdb_id': 'tt0234215'},
        {'title': 'The Matrix Revolutions', 'director': 'Lana & Lilly Wachowski', 'imdb_id': 'tt0245429'},
        {'title': 'The Matrix Resurrections', 'director': 'Lana Wachowski', 'imdb_id': 'tt10838180'}
    ],
    'thriller': [
        {'title': 'American Psycho', 'director': 'Mary Harron', 'imdb_id': 'tt0144084'},
        {'title': "Jennifer's Body", 'director': 'Karyn Kusama', 'imdb_id': 'tt1131734'},
        {'title': 'Near Dark', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt0093605'},
        {'title': 'Zero Dark Thirty', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt1790885'},
        {'title': 'The Hurt Locker', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt0887912'},
        {'title': 'The Nightingale', 'director': 'Jennifer Kent', 'imdb_id': 'tt3836954'},
        {'title': 'The Babadook', 'director': 'Jennifer Kent', 'imdb_id': 'tt2321549'},
        {'title': 'Raw', 'director': 'Julia Ducournau', 'imdb_id': 'tt4954522'},
        {'title': 'Titane', 'director': 'Julia Ducournau', 'imdb_id': 'tt10944760'},
        {'title': 'The Weight of Water', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt0245429'},
        {'title': 'Strange Days', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt0114558'},
        {'title': 'Point Break', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt0102685'},
        {'title': 'The Loveless', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt0084280'},
        {'title': 'Near Dark', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt0093605'},
        {'title': 'Blue Steel', 'director': 'Kathryn Bigelow', 'imdb_id': 'tt0099165'}
    ],
    'fantasy': [
        {'title': 'A Wrinkle in Time', 'director': 'Ava DuVernay', 'imdb_id': 'tt1620680'},
        {'title': 'Frozen', 'director': 'Jennifer Lee', 'imdb_id': 'tt2294629'},
        {'title': 'Wonder Woman', 'director': 'Patty Jenkins', 'imdb_id': 'tt0451279'},
        {'title': 'Wonder Woman 1984', 'director': 'Patty Jenkins', 'imdb_id': 'tt7126948'},
        {'title': 'Monster', 'director': 'Patty Jenkins', 'imdb_id': 'tt0340855'},
        {'title': 'The Power of the Dog', 'director': 'Jane Campion', 'imdb_id': 'tt10293406'},
        {'title': 'The Piano', 'director': 'Jane Campion', 'imdb_id': 'tt0107822'},
        {'title': 'Bright Star', 'director': 'Jane Campion', 'imdb_id': 'tt0810784'},
        {'title': 'Tomboy', 'director': 'Céline Sciamma', 'imdb_id': 'tt1847731'},
        {'title': 'Selma', 'director': 'Ava DuVernay', 'imdb_id': 'tt1020072'},
        {'title': 'A Wrinkle in Time', 'director': 'Ava DuVernay', 'imdb_id': 'tt1620680'},
        {'title': 'Frozen II', 'director': 'Jennifer Lee', 'imdb_id': 'tt4520988'},
        {'title': 'Zootopia', 'director': 'Jennifer Lee', 'imdb_id': 'tt2948356'},
        {'title': 'Wreck-It Ralph', 'director': 'Jennifer Lee', 'imdb_id': 'tt1772341'},
        {'title': 'Frozen Fever', 'director': 'Jennifer Lee', 'imdb_id': 'tt4007502'}
    ]
}

def get_poster_url(imdb_id):
    try:
        # Add a random delay between requests to be polite
        time.sleep(random.uniform(1, 3))
        
        # Make the request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = f'https://www.imdb.com/title/{imdb_id}/'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find the poster image
        poster_div = soup.find('div', class_='ipc-poster')
        if poster_div:
            img = poster_div.find('img')
            if img and 'src' in img.attrs:
                # Get the highest resolution version
                poster_url = img['src']
                if '@' in poster_url:
                    poster_url = poster_url.split('@')[0] + '@.jpg'
                return poster_url
        
        # Alternative method if the first one fails
        poster_div = soup.find('div', class_='poster')
        if poster_div:
            img = poster_div.find('img')
            if img and 'src' in img.attrs:
                return img['src']
                
    except Exception as e:
        print(f"Error getting poster URL: {str(e)}")
    return None

def download_and_resize_image(url, save_path):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        img = Image.open(BytesIO(response.content))
        # Resize image to 600x900
        img = img.resize((600, 900), Image.Resampling.LANCZOS)
        img.save(save_path, 'JPEG')
        print(f"Downloaded and saved: {save_path}")
        return True
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False

def create_placeholder_image(save_path, genre):
    # Create a colored placeholder image with text
    img = Image.new('RGB', (600, 900), color=get_genre_color(genre))
    img.save(save_path, 'JPEG')
    print(f"Created placeholder image: {save_path}")

def get_genre_color(genre):
    colors = {
        'romance': (255, 192, 203),  # Pink
        'scifi': (0, 191, 255),      # Deep Sky Blue
        'thriller': (47, 79, 79),    # Dark Slate Gray
        'fantasy': (147, 112, 219)   # Medium Purple
    }
    return colors.get(genre, (128, 128, 128))

def download_posters():
    for genre, movies in MOVIES.items():
        for i, movie_info in enumerate(movies, 1):
            save_path = f'assets/images/{genre}/poster{i}.jpg'
            print(f"\nProcessing {movie_info['title']} directed by {movie_info['director']}...")
            
            poster_url = get_poster_url(movie_info['imdb_id'])
            if poster_url:
                if not download_and_resize_image(poster_url, save_path):
                    create_placeholder_image(save_path, genre)
            else:
                print(f"No poster found for {movie_info['title']}")
                create_placeholder_image(save_path, genre)

def create_placeholder_audio():
    # Create empty audio files
    genres = ['romance', 'scifi', 'thriller', 'fantasy']
    for genre in genres:
        with open(f'assets/audio/{genre}.mp3', 'wb') as f:
            f.write(b'')  # Empty file
        print(f"Created placeholder audio file: {genre}.mp3")

def main():
    print("Creating directories...")
    create_directories()
    
    print("Downloading posters from female-directed movies...")
    download_posters()
    
    print("Creating placeholder audio files...")
    create_placeholder_audio()
    
    print("\nDone! Assets have been created.")
    print("\nMovie posters included:")
    for genre, movies in MOVIES.items():
        print(f"\n{genre.title()} movies:")
        for movie in movies:
            print(f"- {movie['title']} (Dir. {movie['director']})")

if __name__ == "__main__":
    main() 