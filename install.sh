#!/bin/bash

# Exit on any error
set -e

# Function to check if a command exists
command_exists () {
    type "$1" &> /dev/null ;
}

# Update package list and install necessary packages
sudo apt-get update

# Check if Python is installed
if ! command_exists python3 ; then
    echo "Python3 is not installed. Installing Python3..."
    sudo apt-get install -y python3
fi

# Check if pip is installed
if ! command_exists pip3 ; then
    echo "pip3 is not installed. Installing pip3..."
    sudo apt-get install -y python3-pip
fi

# Clone the GitHub repository
REPO_URL="https://github.com/mtashani/real-upload.git"
CLONE_DIR="/opt/Real-Update"

if [ -d "$CLONE_DIR" ] ; then
    echo "Directory $CLONE_DIR already exists. Removing the old directory..."
    sudo rm -rf "$CLONE_DIR"
fi

echo "Cloning the repository..."
sudo git clone "$REPO_URL" "$CLONE_DIR"

cd "$CLONE_DIR"

# Install requirements
echo "Installing requirements..."
sudo pip3 install -r requirements.txt

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/realUpload.service"

if [ -f "$SERVICE_FILE" ] ; then
    echo "Service file already exists. Removing the old service file..."
    sudo systemctl stop realUpload.service
    sudo systemctl disable realUpload.service
    sudo rm "$SERVICE_FILE"
fi

echo "Creating new systemd service file..."

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Run Python script at startup
After=network.target

[Service]
User=$USER
WorkingDirectory=$CLONE_DIR
ExecStart=/usr/bin/python3 $CLONE_DIR/realUpload.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd manager configuration
echo "Reloading systemd manager configuration..."
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling the service to start on boot..."
sudo systemctl enable realUpload.service

# Start the service immediately
echo "Starting the service..."
sudo systemctl start realUpload.service

# Check the status of the service
sudo systemctl status realUpload.service
