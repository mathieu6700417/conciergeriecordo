import os
import uuid
from datetime import datetime
from google.cloud import storage
from PIL import Image
import io

class GCSManager:
    def __init__(self):
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
        self.bucket_name = os.environ.get('GCS_BUCKET_NAME')
        self.client = None
        self.bucket = None

        if self.project_id and self.bucket_name:
            try:
                self.client = storage.Client(project=self.project_id)
                self.bucket = self.client.bucket(self.bucket_name)
            except Exception as e:
                print(f"Warning: Could not initialize GCS client: {e}")

    def is_configured(self):
        """Check if GCS is properly configured"""
        return self.client is not None and self.bucket is not None

    def generate_filename(self, commande_id, paire_id, original_filename=None):
        """Generate a unique filename for the photo"""
        now = datetime.now()
        year = now.year
        month = now.month

        # Extract file extension
        ext = '.jpg'
        if original_filename:
            _, ext = os.path.splitext(original_filename)
            if not ext:
                ext = '.jpg'

        unique_id = uuid.uuid4().hex[:8]
        filename = f"{paire_id}_{unique_id}{ext}"

        return f"photos/{year}/{month:02d}/{commande_id}/{filename}"

    def upload_image(self, image_data, commande_id, paire_id, original_filename=None):
        """Upload image to Google Cloud Storage"""
        if not self.is_configured():
            raise Exception("Google Cloud Storage not configured")

        try:
            # Process image
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background

            # Resize if too large
            max_size = (1920, 1920)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            img_byte_arr.seek(0)

            # Generate filename
            gcs_path = self.generate_filename(commande_id, paire_id, original_filename)

            # Upload to GCS
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_file(img_byte_arr, content_type='image/jpeg')

            # With uniform bucket-level access, objects are automatically public if bucket is public
            # Generate public URL manually
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{gcs_path}"

            return {
                'gcs_path': gcs_path,
                'public_url': public_url,
                'filename': os.path.basename(gcs_path)
            }

        except Exception as e:
            raise Exception(f"Failed to upload image to GCS: {str(e)}")

    def get_signed_url(self, gcs_path, expiration_minutes=60):
        """Generate a signed URL for private access to the image"""
        if not self.is_configured():
            return None

        try:
            blob = self.bucket.blob(gcs_path)

            # Generate signed URL
            from datetime import timedelta
            url = blob.generate_signed_url(
                expiration=datetime.utcnow() + timedelta(minutes=expiration_minutes),
                method='GET'
            )

            return url
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return None

    def delete_image(self, gcs_path):
        """Delete image from Google Cloud Storage"""
        if not self.is_configured():
            return False

        try:
            blob = self.bucket.blob(gcs_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting image from GCS: {e}")
            return False

    def delete_commande_images(self, commande_id):
        """Delete all images for a specific commande"""
        if not self.is_configured():
            return False

        try:
            # List all blobs with the commande prefix
            prefix = f"photos/{datetime.now().year}/{datetime.now().month:02d}/{commande_id}/"
            blobs = self.client.list_blobs(self.bucket, prefix=prefix)

            # Delete all blobs
            for blob in blobs:
                blob.delete()

            return True
        except Exception as e:
            print(f"Error deleting commande images: {e}")
            return False

# Global instance
gcs_manager = GCSManager()