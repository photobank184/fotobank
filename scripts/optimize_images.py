import os
from PIL import Image
from django.conf import settings

def create_thumbnails():
    media_root = settings.MEDIA_ROOT
    photos_dir = os.path.join(media_root, 'photos')
    thumbs_dir = os.path.join(media_root, 'photos', 'thumbnails')
    os.makedirs(thumbs_dir, exist_ok=True)
    
    count = 0
    for filename in os.listdir(photos_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            img_path = os.path.join(photos_dir, filename)
            thumb_path = os.path.join(thumbs_dir, filename)
            if not os.path.exists(thumb_path):
                try:
                    with Image.open(img_path) as img:
                        img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        img.save(thumb_path, 'JPEG', quality=85, optimize=True)
                        count += 1
                        print(f"[{count}] {filename}")
                except Exception as e:
                    print(f"Error {filename}: {e}")
    print(f"\nTotal: {count} thumbnails")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photobank.settings')
    import django
    django.setup()
    create_thumbnails()
