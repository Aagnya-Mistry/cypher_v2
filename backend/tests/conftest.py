import os

from tests.utils import SECRET, SUPABASE_URL

# Set before the app is imported, and ignore any real backend/.env values.
os.environ.update(SUPABASE_URL=SUPABASE_URL, SUPABASE_JWT_SECRET=SECRET, SUPABASE_SECRET_KEY="")

from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()
