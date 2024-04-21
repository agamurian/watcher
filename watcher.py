import time
import json
import utils
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG = "/home/agamurian/gits/watcher/config.json"
def get_from_json(key: str):
    """load any data by key from storage by key"""
    with open(CONFIG, encoding="UTF8") as json_data:
        data = json.loads(json_data.read())
        requested_data = data[key]
        return requested_data
folders = get_from_json("folders_to_watch")


class MyHandler(FileSystemEventHandler):

    currentQueue = []

    @utils.debounce(0.4)
    @staticmethod
    def do_on_event(*args, **kwargs):
        MyHandler.currentQueue = utils.no_doubles(MyHandler.currentQueue)
        folders = get_from_json("folders_to_watch")
        print(folders)
        print("")
        print('just updated files, which are py, html, or pyc:')
        utils.do_in_list(MyHandler.currentQueue, utils.find_by_ext, "py", "html", "pyc")
        MyHandler.currentQueue = []
        print("")
        print("files in watched folders, which are gltf:")
        for folder in folders:
            utils.do_in_dir(folder,utils.find_by_ext, "gltf")

    def on_modified(self, event):
        if event.is_directory:
            return
        print(f'{utils.sep}\n\t{event.src_path}\n\t\t has been modified')
        MyHandler.currentQueue.append(event.src_path)
        self.do_on_event()

    def on_created(self, event):
        if event.is_directory:
            return
        # print(f'File \n\t{event.src_path}\n\t\t has been created')
        MyHandler.currentQueue.append(event.src_path)
        self.do_on_event() 

    def on_deleted(self, event):
        if event.is_directory:
            return
        # print(f'File \n\t{event.src_path}\n\t\t has been deleted')
        self.do_on_event()

def watch_folder(folder_path):
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    for folder in folders:
        print(folder)
        watch_folder(folder)

