import feedparser
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
import requests
from io import BytesIO
import re

# Define the movie posters and ratings
LETTERBOXD_USERNAME = "ashconnor"
RSS_FEED_URL = f"https://letterboxd.com/{LETTERBOXD_USERNAME}/rss/"
PROFILE_PIC_URL = "https://secure.gravatar.com/avatar/1c500c690e46d4a15a8b305b1bfedc58?rating=PG&size=220&border=&default=https%3A%2F%2Fs.ltrbxd.com%2Fstatic%2Fimg%2Favatar220.7c95524c.png"

# Fetch the latest movies from Letterboxd RSS feed
feed = feedparser.parse(RSS_FEED_URL)
movies = []


def rounded_corners_mask(image, corner_radius=60):
    """
    Apply a rounded corner mask to the given image.

    Parameters:
        image (PIL.Image): The image to which the mask will be applied.
        corner_radius (int): The radius of the rounded corners.

    Returns:
        PIL.Image: The image with rounded corners.
    """
    # Create a mask with rounded corners
    width, height = image.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(((0, 0), (width, height)), 10, fill=255)
    return image, mask


for entry in feed.entries[:4]:  # Get the latest 4 movies
    title_split = entry.title.split(" - ", 2)
    if len(title_split) > 1:
        title = title_split[0]
        rating = title_split[1]
    else:
        title = title_split[0]
        rating = ""
    poster_url = re.search(r'img src="(.*?)"', entry.summary).group(
        1
    )  # Extract poster URL
    rating_match = re.search(r"★+", rating)  # Extract star rating
    half_rating_match = re.search(r"½", rating)  # Extract half-rating
    half_rating = "½" if half_rating_match else ""
    rating = "".join(["★" for star in (rating_match.group(0) if rating_match else "")])

    liked = entry.get("letterboxd_memberlike", "").lower() == "yes"

    movies.append(
        {
            "title": title,
            "poster_url": poster_url,
            "rating": rating + half_rating,
            "liked": liked,
        }
    )

# Instagram Story dimensions
WIDTH, HEIGHT = 1080, 1920
# POSTER_WIDTH, POSTER_HEIGHT = WIDTH // 2, int(HEIGHT * 0.4)

POSTER_WIDTH, POSTER_HEIGHT = 412, 586

# Create a blank canvas
story_image = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0, 255))

# Set gradient background
with Image.open("background.png") as background:
    story_image.paste(background, (0, 0))

# x, y positions for the posters
poster_positions = [
    (83, 353),
    (575, 487),
    (83, 1103),
    (575, 1217),
]

# Load and place the movie posters
for i, movie in enumerate(movies):
    response = requests.get(movie["poster_url"])
    poster, mask = rounded_corners_mask(
        Image.open(BytesIO(response.content)).resize((POSTER_WIDTH, POSTER_HEIGHT))
    )

    # Paste the poster onto the canvas
    story_image.paste(poster, poster_positions[i], mask)

    # Add star ratings (the rest of your code remains the same)
    draw = ImageDraw.Draw(story_image)
    font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 64, encoding="unic")

    rating_text = movie["rating"] + (" ❤️" if movie["liked"] else "")

    with Pilmoji(story_image) as pilmoji:
        # Use pilmoji.getsize so emoji width is included in centering calculation
        text_width, text_height = pilmoji.getsize(rating_text, font, emoji_scale_factor=0.75)

        # Center the text horizontally and add padding at the bottom
        text_x = poster_positions[i][0] + (POSTER_WIDTH - text_width) // 2
        text_y = poster_positions[i][1] + POSTER_HEIGHT + (text_height - 50)

        pilmoji.text(
            (text_x, text_y),
            rating_text,
            fill="#00e054",
            font=font,
            emoji_scale_factor=0.75,
        )

story_image.convert("RGB").save("letterboxd_story.jpg", quality=95)
