import redis
import threading
from django.conf import settings
import base64

class RedisClient:
    _client = None
    _lock = threading.Lock()

    @classmethod
    def get_client(cls):
        if cls._client is None:
            with cls._lock:
                if cls._client is None:
                    cls._client = redis.Redis(
                        connection_pool=redis.ConnectionPool(
                            host=settings.REDIS_HOST,
                            port=settings.REDIS_PORT,
                            db=settings.REDIS_DB,
                            password=settings.REDIS_PASSWORD,
                            max_connections=settings.REDIS_MAX_CONNECTIONS
                        )
                    )
        return cls._client

    @staticmethod
    def base36_encode(number):
        """Convert an integer to a base36 string."""
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        base36 = ''

        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36

        return base36 or alphabet[0]

    @classmethod
    def get_next_ticket_id(cls):
        """Generate a new 7-character ticket ID."""

        client = cls.get_client()
        if client.get('ticket:counter') is None:
            client.set('ticket:counter', 0)

        counter = client.incr('ticket:counter') 
        ticket_id = cls.base36_encode(counter)

        ticket_id = ticket_id.zfill(7)

        return ticket_id
