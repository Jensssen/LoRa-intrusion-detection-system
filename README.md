# Raspberry Pi 4 Model B setup

## OS setup

1. Install the rpi-imager `sudo apt install rpi-imager`
2. Go to settings and:
   1. Configure a hostname
   2. Enable ssh and allow public key usage only
   3. Paste a public key
   4. Configure wireless LAN
   5. Set your timezone
3. Finally, select your SD and flash the SD card with an operating system, such as Ubuntu Server 24.04 LTS.

## Setup ssh
1. Go to `~/.ssh` and add the following configuration entry:
    ```
    Host <your selected host name from OS setup>
         HostName <the IP address of the Raspberry Pi> <- You can get the IP by logging into your router
         User <username from OS step>
         Port 22
         IdentityFile ~/.ssh/your_private_key
    ```
2. Now run ssh <your selected host name> and enter your ssh key password
3. You should be logged into your Raspberry Pi now
4. If you get an error, our your connection does not work, mount the SD card on your system, add an empty file named `ssh` to the boot partition, and try again.
5. If it still does not work, edit the file `/etc/sshd_config` and set `PasswordAuthentication no`, `Port 22` and `PubkeyAuthentication yes`, reboot the Raspberry PI and try again.

## Enable serial port

1. Run `sudo apt install raspi-config` and run `sudo raspi-config`
2. Navigate to `Interfacing Options` -> `Serial Port` and enable the serial port. Do not make your login shell accessible over serial!

## Setup Python

1. run `sudo apt-get update && sudo apt-get upgrade`
2. run `sudo apt install python3-pip` to install the python package manager
3. run `sudo apt install python3-rpi-lgpio` to install the GPIO library

