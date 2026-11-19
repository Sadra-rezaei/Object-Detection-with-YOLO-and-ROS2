# مستند فنی پروژه تشخیص اشیا با ROS 2 و YOLO

## 1. معرفی پروژه

هدف این پروژه پیاده‌سازی یک سیستم تشخیص اشیا با استفاده از مدل YOLO و چارچوب ROS 2 است.

در این پروژه، تصویر زنده از دوربین تلفن همراه دریافت شده و پس از انتقال به محیط ROS 2، توسط مدل YOLO پردازش می‌شود. در نهایت، اشیای شناسایی‌شده به همراه اطلاعات مربوط به آن‌ها در قالب پیام روی یک Topic منتشر می‌شوند.

سیستم در محیط Ubuntu روی WSL2 ویندوز پیاده‌سازی شده است.

## 2. ابزارها و فناوری‌های استفاده‌شده

|ابزار|کاربرد|
|---|---|
|ROS 2 Humble|مدیریت ارتباط بین Nodeها و انتقال پیام‌ها|
|Python|زبان برنامه‌نویسی پروژه|
|Ultralytics YOLO|تشخیص و شناسایی اشیا در تصاویر|
|YOLO11n|مدل مورد استفاده برای تشخیص اشیا|
|OpenCV|پردازش و مدیریت تصاویر|
|cv_bridge|تبدیل پیام‌های تصویری ROS به فرمت قابل استفاده در OpenCV|
|Android IP Webcam|دریافت تصویر زنده از دوربین تلفن همراه|
|Ubuntu / WSL2|محیط اجرای پروژه|
|colcon|ساخت و مدیریت پکیج ROS 2|

## 3. معماری پروژه

پروژه از دو Node اصلی تشکیل شده است:

### 3.1. Camera Node

این Node وظیفه دریافت تصویر زنده از دوربین تلفن همراه را بر عهده دارد.

تصاویر دریافتی از طریق IP Webcam به سیستم منتقل شده و در قالب پیام تصویری ROS 2 منتشر می‌شوند.

- نام Node: `camera_node`
    
- Topic خروجی: `/camera/image_raw`
    
- نوع پیام: `sensor_msgs/msg/Image`
    

### 3.2. Detection Node

این Node تصاویر منتشرشده توسط Camera Node را دریافت کرده و با استفاده از مدل YOLO11n عملیات تشخیص اشیا را انجام می‌دهد.

اطلاعات مربوط به اشیای شناسایی‌شده شامل موارد زیر است:

- شناسه کلاس شیء (`class_id`)
    
- نام شیء (`class_name`)
    
- میزان اطمینان تشخیص (`confidence`)
    
- مختصات محدوده شیء در تصویر (`bbox`)
    

نتایج پردازش در قالب JSON و داخل پیام `std_msgs/msg/String` منتشر می‌شوند.

- نام Node: `detection_node`
    
- Topic ورودی: `/camera/image_raw`
    
- Topic خروجی: `/yolo/detections`
    
- نوع پیام خروجی: `std_msgs/msg/String`
    

### 3.3. ساختار ارتباطی

```
Android Phone Camera
        |
        v
    IP Webcam
        |
        v
   Camera Node
        |
        | /camera/image_raw
        v
  Detection Node
        |
        | YOLO11n
        v
 Object Detection
        |
        | /yolo/detections
        v
   ROS 2 Subscriber
        |
        v
  Terminal Output
```

## 4. مراحل راه‌اندازی پروژه

### 4.1. آماده‌سازی دوربین تلفن همراه

1. برنامه IP Webcam را روی تلفن همراه اجرا کنید.
    
2. تلفن همراه و سیستم اجراکننده Ubuntu باید به شبکه‌ای دسترسی داشته باشند که ارتباط بین آن‌ها برقرار باشد.
    
3. آدرس و پورت سرور IP Webcam را بررسی کنید.
    
4. آدرس تصویر زنده را در تنظیمات یا کد Camera Node قرار دهید.
    

نمونه آدرس:

```
http://PHONE_IP:8080/video
```

توجه: در صورت تغییر IP تلفن همراه، آدرس جدید باید در پروژه تنظیم شود.

### 4.2. آماده‌سازی محیط ROS 2

در هر ترمینال ابتدا محیط ROS 2 را فعال کنید:

```
source /opt/ros/humble/setup.bash
```

سپس محیط مجازی Python را فعال کنید:

```
source ~/yolo_env/bin/activate
```

در نهایت محیط کاری پروژه را بارگذاری کنید:

```
source ~/ros-ws-clean/install/setup.bash
```

### 4.3. تنظیم اجرای Detection Node

کتابخانه Ultralytics در محیط مجازی `yolo_env` نصب شده است. به همین دلیل، فایل اجرایی Detection Node باید از Python همین محیط استفاده کند.

در صورت بازسازی پکیج و بازگشت Shebang به Python سیستمی، دستور زیر را اجرا کنید:

```
sed -i '1c\#!/home/'"$USER"'/yolo_env/bin/python3' \
~/ros-ws-clean/install/yolo_ros/lib/yolo_ros/detection_node
```

برای بررسی مسیر Python:

```
head -n 1 ~/ros-ws-clean/install/yolo_ros/lib/yolo_ros/detection_node
```

خروجی باید به Python محیط مجازی اشاره کند.

## 5. نحوه اجرای پروژه

برای اجرای کامل سیستم، به سه ترمینال نیاز است.

### ترمینال اول: اجرای Camera Node

ابتدا دستورات آماده‌سازی محیط را اجرا کنید:

```
source /opt/ros/humble/setup.bash
source ~/yolo_env/bin/activate
source ~/ros-ws-clean/install/setup.bash
```

سپس Camera Node را اجرا کنید:

```
ros2 run yolo_ros camera_node
```

این ترمینال باید هنگام اجرای پروژه باز بماند.

### ترمینال دوم: اجرای Detection Node

ابتدا محیط ROS 2 و Python را فعال کنید:

```
source /opt/ros/humble/setup.bash
source ~/yolo_env/bin/activate
source ~/ros-ws-clean/install/setup.bash
```

سپس Node تشخیص اشیا را اجرا کنید:

```
ros2 run yolo_ros detection_node
```

پس از اجرا، مدل YOLO بارگذاری شده و تصاویر دریافتی پردازش می‌شوند.

### ترمینال سوم: مشاهده نتایج تشخیص

برای مشاهده خروجی Node تشخیص، دستورات آماده‌سازی محیط را اجرا کنید:

```
source /opt/ros/humble/setup.bash
source ~/yolo_env/bin/activate
source ~/ros-ws-clean/install/setup.bash
```

سپس دستور زیر را اجرا کنید:

```
ros2 topic echo /yolo/detections --field data
```

با اجرای این دستور، محتوای فیلد `data` پیام‌های منتشرشده روی Topic خروجی نمایش داده می‌شود.

## 6. بررسی خروجی پروژه

خروجی Detection Node به‌صورت یک رشته JSON منتشر می‌شود.

نمونه‌ای از خروجی:

```
{
  "stamp": {
    "sec": 123456,
    "nanosec": 123456789
  },
  "frame_id": "camera",
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.9231,
      "bbox": {
        "x1": 100,
        "y1": 80,
        "x2": 300,
        "y2": 450
      }
    }
  ]
}
```

مقادیر بالا صرفاً نمونه هستند و خروجی واقعی به تصویر دوربین و نتایج مدل بستگی دارد.

در صورتی که هیچ شیئی شناسایی نشود، آرایه `detections` خالی خواهد بود.

## 7. دستورات کاربردی ROS 2

برای بررسی Topicهای فعال:

```
ros2 topic list
```

برای مشاهده اطلاعات یک Topic:

```
ros2 topic info /camera/image_raw
```

برای بررسی نرخ انتشار تصاویر دوربین:

```
ros2 topic hz /camera/image_raw
```

برای مشاهده ساختار پیام خروجی:

```
ros2 topic echo /yolo/detections
```

برای مشاهده فقط محتوای خروجی JSON:

```
ros2 topic echo /yolo/detections --field data
```

برای مشاهده Nodeهای فعال:

```
ros2 node list
```

## 8. نکات اجرایی

- پیش از اجرای پروژه، سرور IP Webcam باید روی تلفن همراه فعال باشد.
    
- هر سه ترمینال باید به یک محیط ROS 2 متصل باشند.
    
- برای اجرای Detection Node، محیط مجازی Python باید فعال باشد و Shebang فایل اجرایی به مفسر همان محیط اشاره کند.
    
- آستانه اطمینان تشخیص به‌صورت پیش‌فرض در کد تعیین شده و در صورت نیاز می‌توان آن را تغییر داد.
    
- اجرای مجدد `colcon build` ممکن است فایل اجرایی را بازسازی کند؛ در این صورت Shebang باید دوباره بررسی شود.
    
- برای توقف هر Node می‌توان از کلیدهای `Ctrl + C` در ترمینال مربوطه استفاده کرد.