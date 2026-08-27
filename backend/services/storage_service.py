from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from config import Config


def _local_store(data: bytes, relative_path: str) -> tuple[str, str]:
    base = Path(Config.LOCAL_UPLOAD_DIR)
    target = base / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    public_id = relative_path.replace('\\', '/')
    return f'{Config.API_BASE_URL}/media/{public_id}', public_id


def add_access_code(url: str | None, access_code: str | None) -> str | None:
    """Attach the event access code to local media URLs after authorisation.

    Local media is served through the Flask /media route, which independently validates
    the event access code. Cloud URLs are returned unchanged because their delivery
    policy is configured at the storage provider.
    """
    if not url or Config.STORAGE_BACKEND != 'local' or '/media/' not in url:
        return url
    if not access_code:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query['access_code'] = access_code
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def store_event_image(event_id: str, image_id: str, optimized_bytes: bytes, thumbnail_bytes: bytes) -> dict:
    if Config.STORAGE_BACKEND == 'cloudinary':
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=Config.CLOUDINARY_CLOUD_NAME,
                api_key=Config.CLOUDINARY_API_KEY,
                api_secret=Config.CLOUDINARY_API_SECRET,
                secure=True,
            )
            folder = f'smart-media-manager/events/{event_id}'
            image_result = cloudinary.uploader.upload(
                optimized_bytes,
                public_id=f'{folder}/{image_id}',
                overwrite=True,
                resource_type='image',
                format='jpg',
                quality='auto:good',
                fetch_format='auto',
            )
            thumb_result = cloudinary.uploader.upload(
                thumbnail_bytes,
                public_id=f'{folder}/thumbnails/{image_id}',
                overwrite=True,
                resource_type='image',
                format='jpg',
                quality='auto:eco',
                fetch_format='auto',
            )
            return {
                'public_id': image_result['public_id'],
                'url': image_result['secure_url'],
                'thumbnail_url': thumb_result['secure_url'],
            }
        except Exception as exc:
            raise RuntimeError('Cloud media upload failed. Check the Cloudinary configuration.') from exc

    image_url, public_id = _local_store(optimized_bytes, f'events/{event_id}/{image_id}.jpg')
    thumbnail_url, _ = _local_store(thumbnail_bytes, f'events/{event_id}/thumbnails/{image_id}.jpg')
    return {'public_id': public_id, 'url': image_url, 'thumbnail_url': thumbnail_url}


def delete_asset(public_id: str) -> bool:
    if not public_id:
        return True
    if Config.STORAGE_BACKEND == 'cloudinary':
        try:
            import cloudinary
            import cloudinary.uploader
            result = cloudinary.uploader.destroy(public_id, resource_type='image')
            parts = public_id.rsplit('/', 1)
            if len(parts) == 2:
                cloudinary.uploader.destroy(f'{parts[0]}/thumbnails/{parts[1]}', resource_type='image')
            return result.get('result') in ('ok', 'not found')
        except Exception:
            return False

    target = Path(Config.LOCAL_UPLOAD_DIR) / public_id
    if target.exists():
        target.unlink()
    thumb = target.parent / 'thumbnails' / target.name
    if thumb.exists():
        thumb.unlink()
    return True
