# ImagineImage

<img style="float: right;width:200px; padding: 0px 0px 20px 20px;" src="docs/read_me_top_image.png" alt="drawing"/>
The vision for this project springboards from the [InkyPi](https://www.youtube.com/watch?v=ZsEpd-VwJCs) project. 
The idea here is to generate interesting images for our 
[Samsung Frame](https://www.reddit.com/r/TheFrame/comments/17tjy87/honest_opinion_about_the_frame_tv/). 

To accomplish this, we have a Python program running on a Raspberry Pi. It uses an AI to augment and 
embellish textual prompts for image-generation, and then directs [another AI](https://cookbook.openai.com/articles/what_is_new_with_dalle_3) 
to generate images based on those prompts. The image is then displayed.

Note that on the Raspberry Pi (Raspi,) we use `systemd` to run our app on startup, and automatically
recover from crashes. It also allows us to it easy to start, stop, or restart the app. When run
Under systemd, the app's logs are managed by a mechanism known as `journalctl`.
See [ImagineImage Systemd Service](#ImagineImage-Systemd-Service) for specifics.

For brevity, we sometimes shorten *ImagineImage* to *ImIm*.

Each image generated is also stored on disk, along with the prompt that was used to create it.
This gives us a pool to draw from when the app starts up so we can immediately show an image.
The images and prompts are also [saved to S3](#s3-image-store) because why not, right? :)

The image directory on disk is purged regularly so that only a maximum number of files may
exist in the local output directory. This maximum is governed by the configuration file,
i.e. `"max_num_saved_files": 200`.

The Options dialog, triggered by hitting the `O` key, will allow you to modify values
in the `app_config.json` file interactively. You may have to quit the app (`Q`) and
start or let the app restart for some of the values to take effect. (See
[Keyboard Commands](#keyboard-commands) for more shortcuts.)

The project is [available on GitHub](https://github.com/rkbenton/ImagineImage)


# Keyboard Commands

| Key    | Effect          |
|--------|-----------------|
| `o, O` | Options dialog  |
| `f, F` | Full screen     |
| `s, S` | Small Window    |
| `q, Q` | Quit            |


# Deployment
Deploying to a Raspberry Pi is rather manual, but not too odious.

See **[RaspiBuildOut.md](docs/RaspiBuildOut.md)** for a detailed guide.


# Operational Notes

## SSH
At Malden, the Raspi is on the SparkleKitten network; at the cabin, it's on Lair Loft.

You can ssh in from Becky's laptop with:
```
ssh becky@irving.local
```

## Remote Access
Turn on _Raspberry Pi Connect_ on the Raspi. It's usually on the menubar to the right.

Screen sharing from the RPi much like Remote Desktop Connection; simply 
use [Raspberry Pi Connect](https://connect.raspberrypi.com/devices). Login with Becky's 
credentials while on the SparkleKitten network and then look for the device tagged "Irving".
## Setting Up AWS Credentials
You'll need these on the Raspi and on your dev machine.
```bash
mkdir ~/.aws/

cat << EOF > ~/.aws/credentials
[default]
aws_access_key_id = [see AWS Access Key in Bitwarden]
aws_secret_access_key = [see AWS Access Key in Bitwarden]
EOF

cat << EOF > ~/.aws/config
[default]
region=us-east-1
EOF
```

## ImagineImage Systemd Service
This service starts the app and keeps it going through crashes and reboots. It also
allows you to start, stop, and restart the service.
### Checking Service Status
```
sudo systemctl status imagineimage.service
```
### Viewing Logs
Browse journalctl logs for ImIm, which includes stdout and errout:
```
journalctl -u imagineimage.service
```
Perhaps more useful for troubleshooting is seeing the last 10 minutes-worth of logging:
```
journalctl -u imagineimage.service --no-pager --since "10 minutes ago"
```
### Enabling and Starting the Service:
```
sudo systemctl daemon-reload
sudo systemctl enable imagineimage.service
sudo systemctl start imagineimage.service
```
### Restarting the Service
```
sudo systemctl restart imagineimage.service
```
Useful commands for managing the service:
### Stopping the Service
```
sudo systemctl stop imagineimage.service
```
### Disabling the Service
```
sudo systemctl disable imagineimage.service
```
### S3 Image Store
Each image is stored on S3 along with a text file of the prompt
used to create it. They are stored in the [im-im-images](https://us-east-1.console.aws.amazon.com/s3/buckets/im-im-images?bucketType=general&region=us-east-1&tab=objects#)
bucket.

## Checking Raspi CPU Temp
```
vcgencmd measure_temp
```
You can get by-the-second temp with:
```
watch -n 1 vcgencmd measure_temp
```
**Throttling Limits:**
- Raspberry Pi boards throttle the processor at 80°C.
- At 85°C, further throttling occurs to prevent damage.
**Observations without Cooling:**
- Without cooling, the idle temperature of Raspberry Pi 5 is approximately 65°C.
- During intense activities, such as the stress test, the temperature can climb and stabilize just above the 85°C thermal limit, causing sustained thermal throttling.

<img style="display: block; margin: 0 auto;width:400px;" src="docs/read_me_bottom_image.png" alt="drawing"/>

# Capturing Git Logs
For convenience, I note here an easy way to get a simple list of git commit messages
from some date to now: 
```bash
git log --after="2025-2-18"  --oneline > git_log.txt
```
You can then upload `git_log.txt` to, say, ChatGPT and then tell it to:
```
create a reasonable changelog from these git commits; produce the results using markdown format
```