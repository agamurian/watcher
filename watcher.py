import time
import json
import utils
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from multiprocessing.pool import ThreadPool

CONFIG = "/home/agamurian/gits/watcher/config.json"
def get_from_json(key: str):
    """load any data by key from storage by key"""
    with open(CONFIG, encoding="UTF8") as json_data:
        data = json.loads(json_data.read())
        requested_data = data[key]
        return requested_data
folders_to_watch = get_from_json("folders_to_watch")
folders = folders_to_watch

stop_watching_flag = False

def block_watching(timeout):
    @utils.debounce(0.1)
    def start_watching(timeout):
        global stop_watching_flag
        stop_watching_flag = True
        time.sleep(timeout)
        stop_watching_flag = False

@utils.debounce(3)
def start_watching():
    global stop_watching_flag
    time.sleep(1)
    stop_watching_flag = False

def stop_watching(timeout):
    global stop_watching_flag
    stop_watching_flag = True
    time.sleep(timeout)

class MyHandler(FileSystemEventHandler):

    currentQueue = []

    @utils.debounce(1)
    @staticmethod
    def do_on_event(*args, **kwargs):
        global stop_watching_flag
        start_watching()
        MyHandler.currentQueue = utils.no_doubles(MyHandler.currentQueue)
        folders_to_watch = get_from_json("folders_to_watch")
        print(".",end='')
        print(folders_to_watch)
        if not stop_watching_flag:
            print(f'Watching enabled: {not stop_watching_flag}')
            for folder_action in folders_to_watch:
                for arg in args:
                    for ignored in folder_action['ignore']:
                        if ignored in str(arg):
                            block_watching(4)
                            return
                    print(f"{arg}\n\t{folder_action['folder']}")
                    if folder_action['folder'] in str(arg):
                        print(folder_action['folder'])
                        print(folder_action['action'])
                        stop_watching(2)
                        subprocess.call(folder_action["action"], cwd=folder_action["folder"], shell=True)

    def on_modified(self, event):
        if event.is_directory:
            return
        print(f'{utils.sep}\n\t{event.src_path}\n\t\t has been modified')
        MyHandler.currentQueue.append(event.src_path)
        print(event.src_path)
        self.do_on_event(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        # print(f'File \n\t{event.src_path}\n\t\t has been created')
        MyHandler.currentQueue.append(event.src_path)
        self.do_on_event(event.src_path) 

    def on_deleted(self, event):
        if event.is_directory:
            return
        # print(f'File \n\t{event.src_path}\n\t\t has been deleted')
        self.do_on_event(event.src_path)

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

tp = ThreadPool(8)
if __name__ == "__main__":
    for folder_action in folders_to_watch:
        folder = folder_action['folder']
        print(folder)
        tp.apply_async(watch_folder, (folder,))

    tp.close()
    tp.join()
