https://www.kaggle.com/code/farzadzolfaghari/yolo-v3-object-detection/notebook
https://github.com/PINTO0309/MobileNet-SSD-RealSense/blob/master/caffemodel/MobileNetSSD/MobileNetSSD_deploy.prototxt
https://bajdi.com/pixy-cmucam5/
curl -O https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
curl -O https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/northern_english_male/medium/en_GB-northern_english_male-medium.onnx
libcamera-still -o /tmp/frame.jpg
libcamera-still -o /tmp/frame.jpg --autofocus-on-capture -q 95 -n

scp toor@raspberrypi.local:~/Documents/image.jpg ~/Downloads/

scp toor@raspberrypi.local:/tmp/frame.jpg ~/Downloads/
sudo nano /etc/systemd/system/auto_start_python.service
 journalctl -u auto_start_python.service -f
journalctl -u auto_start_python.service -n 50 --no-pager
sudo tail -f /var/log/auto_start_python.log

sudo systemctl daemon-reload
sudo systemctl enable auto_start_python.service
sudo systemctl restart auto_start_python.service
sudo systemctl status auto_start_python.service

[Unit]
Description=My Python Script
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/toor/Documents/iot-smart-glasses/app/main.py
WorkingDirectory=/home/toor
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target