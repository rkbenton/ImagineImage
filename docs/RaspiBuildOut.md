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


#### Update everything, all the time, always
https://www.raspberrypi.com/documentation/computers/os.html#update-software
```
sudo apt-get update -y
sudo apt full-upgrade -y
sudo apt dist-upgrade -y
sudo rpi-update
sudo reboot
```

#### Setting up SSH for GitHub
On your Mac:
Check if you have an rsa key already:
```
ls -lha ~/.ssh/id_rsa*
```
If not:
- Run `ssh-keygen -t rsa`
- `ssh-keygen -t rsa -b 4096 -C "becky@beckybenton.com"`
- passphrase: **read more books**

you should get back something like:
```
Your identification has been saved in /home/becky/.ssh/id_rsa
Your public key has been saved in /home/becky/.ssh/id_rsa.pub
```
Add the SSH Key to Your GitHub Account:

```
cat ~/.ssh/id_rsa.pub
```
- Go to GitHub and log in to your account.
- In the upper-right corner of any page, click your profile photo, then click Settings.
- In the user settings sidebar, click SSH and GPG keys.
- Click New SSH key or Add SSH key.
- In the "Title" field, add a descriptive label for the new key.
- Paste your key into the "Key" field.
- Click Add SSH key.

Test the SSH Connection:

```
ssh -T git@github.com
```
You should see a successful communication with GH!

## Remote GUI with Raspberry Pi Connect
Optional GUI remoting with Raspberry Pi Connect: 
[Raspberry Pi Connect](https://www.raspberrypi.com/documentation/services/connect.html)

ssh into the box and install the remoting app:

```
sudo apt install rpi-connect
```
## Associate your device with your Connect account.
```
rpi-connect on
rpi-connect signin
Complete sign in by visiting https://connect.raspberrypi.com/verify/XXXX-XXXX
```
## GUI


After installation, use the rpi-connect command line interface to start Connect for your current user:

```
rpi-connect on
```
If you’re using the Connect plugin for the menu bar, clicking "Turn On Raspberry Pi Connect" for the first time will open your browser, prompting you to sign in with your Raspberry Pi ID.
## Finish linking your Raspberry Pi

After authenticating, assign a name to your device. Choose a name that uniquely identifies the device. Click the **Create device and sign in** button to continue.


# Set up AWS creds

```
mkdir ~/.aws/
cat << EOF > ~/.aws/credentials
[default]
aws_access_key_id = {access key}
aws_secret_access_key = {secret access key
EOF

cat << EOF > ~/.aws/config
[default]
region=us-east-1
EOF
```

# Clone the Repo
```
cd ~
git clone git@github.com:rkbenton/ImagineImage.git
cd ImagineImage
ls -lha
```

### Create Python .venv and pull in dependencies

```bash
cd ~/ImagineImage
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

# Set up your .env
```
nano .env
```
and copy in the OpenAPI key.

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

# Seed the `image_out` directories
On your MacBook, copy some images to seed the `image_out` directory on the Raspi

```
rsync -av /Users/becky/Library/CloudStorage/Dropbox/PythonStuff/ImagineImage/image_out becky@lincoln.local:~/ImagineImage/
```

