import time
from datetime import timezone as dt_timezone
from functools import wraps

from django.conf import settings
from django.utils import timezone


def auth_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.AUTH_TOKEN is None:
            self.authorize()
        else:
            exp_ts = self.DECODED.get("exp", None)
            if not exp_ts:
                self.authorize()
            else:
                exp = timezone.datetime.fromtimestamp(
                    exp_ts,
                    tz=dt_timezone.utc if settings.USE_TZ else None,
                )
                now = timezone.now()
                if exp.tzinfo != now.tzinfo:
                    exp = exp.astimezone(tz=now.tzinfo)
                if (exp - now).total_seconds() <= 5:
                    self.authorize()
        return func(self, *args, **kwargs)

    return wrapper


def retry_on_failure(default_retry_count=3, default_sleep_time=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = kwargs.pop("retry_count", default_retry_count)
            sleep_time = kwargs.pop("sleep_time", default_sleep_time)
            last_exception = None

            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retries:
                        time.sleep(sleep_time)
            raise last_exception

        return wrapper

    return decorator
