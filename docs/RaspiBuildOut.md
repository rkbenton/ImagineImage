# Deploying to Raspi

# Overview

- Add necessary credentials for git, aws, OpenAI
- Clone the repository
  - create .venv
  - update pip
  - install dependencies
  - set up `.env` with OpenAI credential
  - set up config_local.json as needed
- Manual test of the app
- Create systemd service to auto-run the app
- Configure journalctl logging

# Automatically Launching ImagineImage
It's pretty easy to get the ImagineImage program to run automatically when your Raspberry Pi 5 boots up. This can be done using systemd, which is the standard service manager on modern Linux systems.

First, create a systemd service file:
```
sudo nano /etc/systemd/system/imagineimage.service
```

Add this content to the file (modify the paths and user as needed):
```
[Unit]
Description=ImagineImage Service
# Ensures this service starts after the graphical environment is ready
After=graphical.target
# Prevent excessive restarts
# Defines a 5-minute (300 seconds) window for tracking restarts
StartLimitIntervalSec=300
# Allows up to 5 restarts within the 5-minute window before disabling further attempts
StartLimitBurst=5

[Service]
Type=simple
User=becky
# Ensures the service runs in the correct display environment
Environment=DISPLAY=:0
WorkingDirectory=/home/becky/ImagineImage
# Command to start the service
ExecStart=/home/becky/ImagineImage/.venv/bin/python /home/becky/ImagineImage/ImagineImage.py

# Waits n seconds before restarting to avoid excessive quick restarts
RestartSec=5s
Restart=always

# disabling output buffering forces Python to print everything immediately
Environment="PYTHONUNBUFFERED=1"

# Log output; read with journalctl
# StandardOutput=journal
# StandardError=journal

# Ensure clean exit
# Sends SIGINT instead of SIGTERM to allow graceful shutdown
KillSignal=SIGINT
# Waits up to 20 seconds for the process to stop before forcefully killing it
TimeoutStopSec=20

[Install]
# Ensures the service starts on boot
WantedBy=default.target
```

# Managing the ImagineImage Startup Service

Enable and start the service:
```
sudo systemctl stop imagineimage.service
sudo systemctl daemon-reload
sudo systemctl enable imagineimage.service
sudo systemctl start imagineimage.service
```

Check the status:
```
sudo systemctl status imagineimage.service
```

Useful commands for managing the service:

- Stop: `sudo systemctl stop imagineimage.service`
- Restart: `sudo systemctl restart imagineimage.service`
- View logs: `journalctl -u imagineimage.service`
- View only last 10 mins of log

 ```
journalctl -u imagineimage.service --no-pager --since "10 minutes ago"
journalctl -u imagineimage.service --no-pager --since "5 minutes ago"
journalctl -u imagineimage.service --no-pager --since "30 seconds ago"
```
# Prevent logging from choking the disk
Our print statements go to the system-maintained logs managed by journalctl. The default journalctl logs can grow and consume disk space. Here's how to manage it:

Check current disk usage:
```
journalctl --disk-usage
```

View current settings:
```
sudo journalctl --vacuum-size=1G
sudo journalctl --vacuum-time=1weeks
```

You can set persistent limits by editing the journal configuration:
```
sudo nano /etc/systemd/journald.conf
```

Add or modify these lines:
```
SystemMaxUse=1G
SystemMaxFileSize=100M
MaxRetentionSec=1week
```

Then restart the journal service:
```
sudo systemctl restart systemd-journald
```
Common settings:

- SystemMaxUse: Maximum disk space used
- MaxRetentionSec: How long to keep logs
- SystemMaxFileSize: Maximum size per file

For a Raspberry Pi, you might want to use smaller values like:
```
SystemMaxUse=100M
MaxRetentionSec=3days
```


