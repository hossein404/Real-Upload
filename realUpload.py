import os
import random
import requests
import time
from datetime import datetime
from requests.exceptions import RequestException, Timeout
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Set to DEBUG to capture all levels of logs

file_handler = logging.FileHandler('/opt/Real-Update/real-upload.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable logging to stdout/stderr
logging.getLogger().handlers.clear()
logging.getLogger().addHandler(file_handler)

def download_file(url, destination, max_speed=102400, timeout=180):
    try:
        logger.info(f"Starting download: {url} to {destination}")
        response = requests.get(url, stream=True, timeout=timeout)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        start_time = time.time()  # Start time of the download

        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    elapsed_time = time.time() - start_time
                    download_speed = downloaded_size / elapsed_time  # Download speed in bytes per second

                    # Control download speed
                    if download_speed > max_speed:
                        remaining_time = (downloaded_size / max_speed) - elapsed_time
                        if remaining_time > 0:
                            time.sleep(remaining_time)
                    
                    # Print progress
                    progress = (downloaded_size / total_size) * 100
                    download_speed_MB = download_speed / (1024 * 1024)  # Convert to megabytes per second
                    # print(f"Downloading... {progress:.2f}% completed, Download Speed: {download_speed_MB:.2f} MB/s", end='\r')

                    # Check timeout
                    if elapsed_time > timeout:
                        raise Timeout(f"Download timed out after {timeout} seconds")

        # print("\nDownload completed!")
        logger.info(f"Download completed: {url} to {destination}")

    except (RequestException, Timeout) as e:
        logger.error(f"Failed to download file from {url}: {e}")
        if os.path.exists(destination):
            os.remove(destination)  # Remove the partially downloaded file if an error occurs
            logger.info(f"Partially downloaded file {destination} removed due to error")

def main():
    logger.info("Starting the download script")
    while True:
        try:
            current_time = datetime.now().time()
            file_path = "urls.txt"
            
            with open(file_path, "r") as file:
                urls = file.readlines()
            
            for url in urls: # Randomly select one URL from the list
                file_name = url.strip().split("/")[-1]
                if os.path.exists(file_name):
                    os.remove(file_name)  # Remove the partially downloaded file if an error occurs
                    logger.info(f"Partially downloaded file {file_name} removed due to error")
            random_url = random.choice(urls).strip()  # Randomly select one URL from the list
            file_name = random_url.split("/")[-1]
            
            if datetime.strptime("02:00:00", "%H:%M:%S").time() <= current_time <= datetime.strptime("07:30:00", "%H:%M:%S").time():
                max_speed = 70000 * 1024  
            else:
                max_speed = 20000 * 1024  

            logger.info(f"Selected URL: {random_url} with max speed {max_speed} bytes/s")
            random_timeout = random.randint(180, 300)
            download_file(random_url, file_name, max_speed=max_speed, timeout=random_timeout)  # Max speed in bytes per second, timeout in seconds

            if os.path.exists(file_name):
                os.remove(file_name)  # Remove the downloaded file
                logger.info(f"File {file_name} removed after download")
                # print(f"File {file_name} removed!\n")
            else:
                logger.warning(f"File {file_name} not found for removal")

            random_sleep = random.randint(10, 60)
            logger.info(f"Sleeping for {random_sleep} seconds")
            time.sleep(random_sleep)

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
