from googleapiclient.discovery import build
import pandas as pd
import time

# 🔑 Replace with your real YouTube Data API key
API_KEY = "AIzaSyAYhpxSIrGbMOFVPMbnP8BeoLFSPH2G2tA"

# Build the YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def search_channels(keyword, max_results=1000):
    channels = []
    next_page_token = None
    results_fetched = 0
    per_page = 50  # max per API call

    while results_fetched < max_results:
        request = youtube.search().list(
            q=keyword,
            type='channel',
            part='snippet',
            maxResults=per_page,
            pageToken=next_page_token
        )
        response = request.execute()
        items = response.get('items', [])

        channels.extend(items)
        results_fetched += len(items)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

        time.sleep(1)  # Pause to respect API quota

    return channels

def get_channel_details(channel_ids):
    channel_data = []
    for i in range(0, len(channel_ids), 50):
        batch_ids = channel_ids[i:i+50]
        request = youtube.channels().list(
            part='snippet,statistics',
            id=','.join(batch_ids)
        )
        response = request.execute()
        channel_data.extend(response.get('items', []))
        time.sleep(1)
    return channel_data

def filter_channels(keyword):
    print("🔍 Searching for channels...")
    search_results = search_channels(keyword, max_results=1000)

    channel_ids = [item['snippet']['channelId'] for item in search_results]
    print(f"✅ Found {len(channel_ids)} channels, fetching details...")

    all_details = get_channel_details(channel_ids)

    filtered = []
    for ch in all_details:
        title = ch['snippet']['title']
        country = ch['snippet'].get('country', 'N/A')
        subs = int(ch['statistics'].get('subscriberCount', 0))

        if 2500 <= subs <= 350000 and country == 'US':
            filtered.append({
                'Channel Name': title,
                'Subscribers': subs,
                'Country': country
            })

    df = pd.DataFrame(filtered)
    print(f"✅ Filtered {len(filtered)} matching channels")
    df.to_excel("US_Tech_Review_Channels.xlsx", index=False)
    print("📁 Data saved to US_Tech_Review_Channels.xlsx")

# 🔧 Run it with your preferred keyword
filter_channels("technology product review")