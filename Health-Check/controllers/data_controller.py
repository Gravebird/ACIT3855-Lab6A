import json

class Data_Controller:
    def __init__(self, data_file_path):
        self._data_file_path = data_file_path
        with open(self._data_file_path, 'r') as f:
            self._data = json.loads(f.read())

    
    def update_data(self, new_json):
        self._data = new_json

        self.save_data_file()


    def get_latest_data(self):
        return self._data

    
    def save_data_file(self):
        with open(self._data_file_path, 'w') as f:
            json.dump(self._data, f, indent=4, default=str)