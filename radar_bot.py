import asyncio
import time
import json  # Import the json library
from radar_downloader import get_clouds_percentage
from credentials import *
import requests

def send_start_running():
    # Send start message to Discord
    send_discord_message("Weather Radar Bot is running")

def send_discord_message(message):
    # This is a general function for sending simple text messages
    payload = {
        'content': message
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Discord message sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")

# This function will only send the text part of the report
def send_text_radar_report(cloud_percentage):
    if cloud_percentage < 10:
        status_text = f"## 🌧 There is some chance of rain: **__{cloud_percentage:.1f}%__**"
    elif 10 <= cloud_percentage < 20:
        status_text = f"## 🌦 High chance of rain: **__{cloud_percentage:.1f}%__**"
    else:
        status_text = f"## ⛈ It is probably raining now: **__{cloud_percentage:.1f}%__**"

    # Send the combined text as a single message
    send_discord_message(f"{status_text}\n> Current Radar Image")

# This new function will handle sending the image and buttons
def send_radar_image_and_buttons():
    # 1. Prepare the payload for the request
    # The 'content' is an empty string because this message is just the image and buttons
    payload = {
        'content': '',
        'components': [
            {
                'type': 1,
                'components': [
                    {
                        'type': 2,
                        'style': 5,
                        'label': 'Nongchok Radar',
                        'url': 'https://weather.bangkok.go.th/Radar/RadarHighResolution.aspx'
                    },
                    {
                        'type': 2,
                        'style': 5,
                        'label': 'Nongkhaem Radar',
                        'url': 'https://weather.bangkok.go.th/Radar/RadarHighResolutionNk.aspx'
                    }
                ]
            }
        ]
    }

    # 2. Open the image file and prepare the files payload
    try:
        with open("radar_tmp.jpg", 'rb') as f:
            files = {
                'file': ('radar_tmp.jpg', f, 'image/jpeg')
            }
            # 3. Send the combined request with the payload converted to a JSON string
            response = requests.post(
                DISCORD_WEBHOOK_URL, 
                data={'payload_json': json.dumps(payload)}, 
                files=files
            )
            response.raise_for_status()
            print("Discord radar image and buttons sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")
    except FileNotFoundError:
        print("Error: radar_tmp.jpg not found. Cannot send report.")

# The check_radar_task now calls two separate functions
async def check_radar_task():
    while(1):
        try:
            cloud_percentage = get_clouds_percentage(False) 
            print(f"Percent = {cloud_percentage}")

            if cloud_percentage >= 5:
                # 1. Send the text message first
                send_text_radar_report(cloud_percentage)
                # 2. Then, send the image and buttons in a separate message
                send_radar_image_and_buttons()
                
                if cloud_percentage < 10:
                    delay_min = 15
                elif 10 <= cloud_percentage < 20:
                    delay_min = 30
                else:
                    delay_min = 45
                
                time.sleep(delay_min * 60)
            else:
                time.sleep(5 * 60)
        except Exception as e:
            print(f"An error occurred in check_radar_task: {e}")
            time.sleep(60)

async def main() -> None:
    send_start_running()
    await check_radar_task()

if __name__ == "__main__":
    asyncio.run(main())