import asyncio
import time
from radar_downloader import get_clouds_percentage
from credentials import *
import requests

def send_start_running():
    # New: Send start message to Discord
    send_discord_message("Weather Radar Bot is running")


def send_radar_report(message):
    # New: Send radar report to Discord
    send_discord_report(message)

# New: Function to send a text message to Discord
def send_discord_message(message):
    payload = {
        'content': message
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        print("Discord message sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")

# New: Function to send a radar report (text and image) to Discord
def send_discord_report(message):
    # Send text
    send_discord_message(message)

    # Send radar image
    with open("radar_tmp.jpg", 'rb') as f:
        files = {'file': ('radar_tmp.jpg', f, 'image/jpeg')}
        payload = {
            'content': "Current Radar Image" # Optional: add a caption to the image
        }
        try:
            response = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
            response.raise_for_status() # Raise an exception for HTTP errors
            print("Discord image sent successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Discord image: {e}")
            
def send_discord_message(message):
    payload = {
        'content': message,
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
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Discord message sent successfully with button.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")


async def check_radar_task():

    while(1):

        try:
            cloud_percentage = get_clouds_percentage(False)
            print(f"Percent =  {cloud_percentage}")

            if (cloud_percentage >= 5):
                delay_min = 15
                message = ""
                
                if cloud_percentage < 10:
                    message = f"## There is some chance of rain: {cloud_percentage:.1f}%"
                    delay_min = 15
                    
                elif cloud_percentage > 10 and cloud_percentage < 20:
                    message = f"## High chance of rain: {cloud_percentage:.1f}%"
                    delay_min = 30

                else :
                    message = f"## It is probably raining now: {cloud_percentage:.1f}%"
                    delay_min = 90
            
                print("Sending message")
                send_radar_report(message)
                time.sleep(delay_min *60)
            
            else: 
                time.sleep(5*60)

        except Exception:
            time.sleep(60)
            
    # user_ids = ", ".join(str(uid) for uid in context.bot_data.setdefault("user_ids", set()))


async def main() -> None:
    send_start_running()
    await check_radar_task()


if __name__ == "__main__":
    asyncio.run(main())