import asyncio
import time
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

# Renamed and modified function to send the full report
def send_full_radar_report(cloud_percentage):
    # 1. Prepare the text content
    if cloud_percentage < 10:
        status_text = f"**There is some chance of rain: {cloud_percentage:.1f}%**"
    elif 10 <= cloud_percentage < 20:
        status_text = f"**High chance of rain: {cloud_percentage:.1f}%**"
    else:
        status_text = f"**It is probably raining now: {cloud_percentage:.1f}%**"

    # 2. Prepare the payload for the request
    payload = {
        # This is the main text content, which now includes the bold status
        'content': f"{status_text}\nCurrent Radar Image",
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
    
    # 3. Open the image file and prepare the files payload
    try:
        with open("radar_tmp.jpg", 'rb') as f:
            files = {
                'file': ('radar_tmp.jpg', f, 'image/jpeg')
            }
            # 4. Send the combined request
            response = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
            response.raise_for_status()
            print("Discord radar report sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord radar report: {e}")
    except FileNotFoundError:
        print("Error: radar_tmp.jpg not found. Cannot send report.")


async def check_radar_task():
    while(1):
        try:
            # The get_clouds_percentage function should handle downloading the image and saving it
            cloud_percentage = get_clouds_percentage(False) 
            print(f"Percent = {cloud_percentage}")

            if cloud_percentage >= 5:
                # Call the new combined function
                send_full_radar_report(cloud_percentage)
                
                # Determine the delay
                if cloud_percentage < 10:
                    delay_min = 15
                elif 10 <= cloud_percentage < 20:
                    delay_min = 30
                else:
                    delay_min = 90
                
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