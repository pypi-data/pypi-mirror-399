from django.conf import settings

# Khalti API URL
khalti_base_url_from_settings = getattr(settings, "KHALTI_BASE_URL", None)
if not khalti_base_url_from_settings:
    KHALTI_BASE_URL = "https://khalti.com/api/v2/"
else:
    KHALTI_BASE_URL = khalti_base_url_from_settings + (
        "/" if not khalti_base_url_from_settings.endswith("/") else ""
    )

# Khalti Live Secret Key
LIVE_SECRET_KEY = getattr(settings, "KHALTI_LIVE_SECRET_KEY", "")

# Khalti Return URL View Name
RETURN_VIEW_NAME = getattr(settings, "KHALTI_RETURN_VIEW_NAME", "khalti_return")
