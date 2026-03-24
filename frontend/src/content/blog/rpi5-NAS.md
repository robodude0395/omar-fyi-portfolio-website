---
title: "Making a NAS personal remote storage from an external drive and rpi 5"
description: "A quick NAS server I made in order ot easily keep all my media and content in one place."
pubDate: 2026-03-23
tags: ["personal", "diy"]
thumbnail: ""
heroImage: ""
draft: false
---

# Raspberry Pi 5 NAS Setup with NTFS USB Drive

This guide documents setting up a **personal NAS** using a Raspberry Pi 5 and an existing NTFS-formatted USB hard drive.
No formatting is required; your existing files remain intact. The NAS can be accessed from Windows, macOS, and Linux.

---

## Hardware

- Raspberry Pi 5
- USB external hard drive (NTFS, 5.5TB in this example)
- Ethernet or Wi-Fi connection

---

## 1. Connect and Verify the Drive

Plug in your USB drive and check:

```bash
lsblk
sudo blkid /dev/sda1

Example output:

/dev/sda1: LABEL="Elements" TYPE="ntfs" UUID="B6BE42BDBE427641"
2. Create Mount Point
sudo mkdir -p /mnt/nas
3. Mount the Drive

Mount with proper permissions:

sudo mount -t ntfs-3g -o uid=pi,gid=pi,umask=002 /dev/sda1 /mnt/nas
ls /mnt/nas  # confirm files are visible

If you see an “unclean file system” message, it’s normal; Linux fixes NTFS safely on mount.

4. Auto-mount on Boot

Get the UUID of your drive:

sudo blkid

Add to /etc/fstab:

sudo nano /etc/fstab

Add the line (replace UUID):

UUID=B6BE42BDBE427641 /mnt/nas ntfs-3g defaults,uid=pi,gid=pi,umask=002,nofail 0 0

Test with:

sudo mount -a
5. Install and Configure Samba

Install Samba:
```mermaid
sudo apt update
sudo apt install samba
```

Edit the config:

sudo nano /etc/samba/smb.conf

Add at the bottom:
```mermaid
[NAS]
   path = /mnt/nas
   browseable = yes
   read only = no
   guest ok = no
   valid users = pi
   force user = pi
```

6. Set Samba Password
sudo smbpasswd -a pi
7. Restart Samba
sudo systemctl restart smbd
sudo systemctl status smbd  # ensure it is active
8. Connect from Other Devices
Windows
\\<raspberry_pi_ip>\NAS
macOS

Finder → Go → Connect to Server:

smb://<raspberry_pi_ip>/NAS
Linux
smb://<raspberry_pi_ip>/NAS

Use pi and the password set with smbpasswd.

9. Notes / Troubleshooting
If macOS shows "The operation can’t be completed because the original item can’t be found", use the IP address instead of hostname.
If drive mounts read-only, run:
sudo ntfsfix /dev/sda1
Always safely eject the drive from Windows to avoid unclean NTFS errors.
For better macOS compatibility, you can add the following under [global] in smb.conf:
min protocol = SMB2
vfs objects = catia fruit streams_xattr
✅ Summary
USB NTFS drive mounted and auto-mounted on Pi 5
Shared over the network using Samba
Accessible from Windows, macOS, Linux
No data loss