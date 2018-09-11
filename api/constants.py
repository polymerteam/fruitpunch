from datetime import datetime, timedelta
from django.utils import timezone

DATE_FORMAT = "%Y-%m-%d-%H-%M-%S-%f"
BEGINNING_OF_TIME = timezone.make_aware(datetime(1, 1, 1), timezone.utc)
END_OF_TIME = timezone.make_aware(datetime(3000, 1, 1), timezone.utc)
THIRTY_DAYS = timedelta(days=30)