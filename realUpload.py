import os
import random
import requests
import time
from datetime import datetime
from requests.exceptions import RequestException

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

file_handler = logging.FileHandler('/opt/Real-Update/real-upload.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def download_file(url, destination, max_speed=102400, timeout=180):
    try:
        logger.error(f"Downloading {url} to {destination}")
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        start_time = time.time()  # Start time of the download
        time.sleep(1)
        try:
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        elapsed_time = time.time() - start_time
                        download_speed = downloaded_size / elapsed_time  # Instant download speed
                        download_speed_MB = download_speed / (1024 * 1024)  # Convert to megabytes per second
                        progress = (downloaded_size / total_size) * 100
                        print(f"Downloading... {progress:.2f}% completed, Download Speed: {download_speed_MB:.2f} MB/s", end='\r')
                        # Control download speed
                        if download_speed > max_speed:
                            remaining_time = (downloaded_size / max_speed) - elapsed_time
                            if remaining_time > 0:
                                time.sleep(remaining_time)
                        # Check timeout
                        if elapsed_time > timeout:
                            raise TimeoutError("Download timed out")
        except TimeoutError:
            logger.error(f"Download timed out!")
            os.remove(destination)  # Remove the partially downloaded file if the download times out
        finally:
            print("\nDownload completed!")
    except RequestException as e:
         logger.error(f"Failed to download file from {url}: {e}") # Remove the partially downloaded file if the download times out



def main():
    while True:
        try:
            current_time = datetime.now().time()
            start_time = datetime.strptime("23:00:00", "%H:%M:%S").time()
            end_time = datetime.strptime("08:00:00", "%H:%M:%S").time()
            
            # if current_time >= start_time or current_time <= end_time:
            file_path = "urls.txt"
            with open(file_path, "r") as file:
                urls = file.readlines()
            random_url = random.choice(urls).strip()  # Randomly select one URL from the list
            file_name = random_url.split("/")[-1]
            
            if current_time >= datetime.strptime("01:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("07:30:00", "%H:%M:%S").time():
                max_speed = 120000 * 1024  
            else:
                max_speed = 60000 * 1024  

            print(f"Downloading file from: {random_url}")
            random_timeout = random.randint(180, 300)
            download_file(random_url, file_name, max_speed=max_speed, timeout=random_timeout)  # Max speed in bytes per second, timeout in seconds
            try:
                os.remove(file_name)  # Remove the downloaded file
                print(f"File {file_name} removed!\n")
            except FileNotFoundError:
                print(f"File {file_name} not found!\n")
            random_sleep = random.randint(10, 120)
            time.sleep(random_sleep)
        except Exception as e:
            logger.error(f" {e}")

if __name__ == "__main__":
    main()

