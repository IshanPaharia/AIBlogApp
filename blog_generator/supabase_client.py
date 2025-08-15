import os
from supabase import create_client, Client

# Get the Supabase URL and Key from environment variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# Create the Supabase client
supabase: Client = create_client(url, key)