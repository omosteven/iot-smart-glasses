https://www.kaggle.com/code/farzadzolfaghari/yolo-v3-object-detection/notebook
https://github.com/PINTO0309/MobileNet-SSD-RealSense/blob/master/caffemodel/MobileNetSSD/MobileNetSSD_deploy.prototxt
https://bajdi.com/pixy-cmucam5/
curl -O https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
curl -O https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
Run The App On Local - uvicorn app.main:app --reload
Run yolo export model=yolov8n.pt format=onnx to load yolo onnx

sudo systemctl start nginx
sudo systemctl daemon-reload
sudo systemctl restart iot-smart-glasses.service
sudo journalctl -u iot-smart-glasses.service -f   for logs
sudo systemctl status iot-smart-glasses.service for status
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log for nginx logs
sudo tail -f /var/log/iot-smart-glasses.log for real time logs