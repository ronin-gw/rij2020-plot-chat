#!/bin/bash

# python3 -m pip install -r requirements.txt -r chat-replay-downloader/requirements.txt

for i in 851143541 852566392 854850147 855023645 855025272 855026609 855102497 855104836 855823913 855824916; do
    json=${i}.json
    if [ ! -f "$json" ]; then
        python3 chat-replay-downloader/chat_replay_downloader.py -o $json https://www.twitch.tv/videos/${i}
    fi
done

./main.py *.json
