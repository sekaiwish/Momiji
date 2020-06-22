import requests
import time
from pathlib import Path

valid = {"png", "jpg", "jpeg", "gif", "webm", "mov", "mp4"}

while True:
    with open("queue", "r+") as fp:
        line = fp.readline()[:-1]
        if line:
            data = fp.read()
            fp.seek(0)
            fp.write(data)
            fp.truncate()
            fp.close()
            try:
                file = line.split(" ")
                # Format: url channel_id message_id
                if file[0].split(".")[-1] in valid:
                    channel_path = Path("./guild/" + file[1])
                    if not channel_path.exists():
                        channel_path.mkdir()
                    file_path = Path("./guild/{}/{}.{}".format(file[1], file[2], file[0].split(".")[-1]))
                    if not file_path.exists():
                        r = requests.get(file[0], stream=True)
                        with open(file_path, "wb") as fd:
                            for chunk in r.iter_content(chunk_size=128):
                                fd.write(chunk)
            except:
                print("Queue error: " + str(file))
        else:
            fp.close()
            time.sleep(1)
