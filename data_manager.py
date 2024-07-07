import json
import redis
import os

class DataManager:
    def __init__(self):
        self.redis_client = self._connect_redis()
        self.file_path = self._get_file_path()

    def _connect_redis(self):
        try:
            client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            client.ping()
            print("Successfully connected to Redis")
            return client
        except redis.ConnectionError:
            print("Failed to connect to Redis. Will use file-based storage.")
            return None

    def _get_file_path(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_directory, 'expenses.json')

    def load_data(self):
        if self.redis_client:
            data = self.redis_client.get('expenses')
            if data:
                return json.loads(data)

        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)

        return []

    def save_data(self, data):
        if self.redis_client:
            self.redis_client.set('expenses', json.dumps(data))

        with open(self.file_path, 'w') as file:
            json.dump(data, file)

data_manager = DataManager()