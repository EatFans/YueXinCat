# YueXinCat - 月薪喵 OLED GIF播放器

这是一个基于ESP32的OLED显示器GIF动画播放项目。

## 展示视频

<iframe src="/doc/1.mp4" width="100%" height="100%" controls="controls"></iframe>

## 硬件要求

- **ESP32开发板** (mhetesp32devkit)
- **0.96寸OLED显示屏** (SSD1306驱动, 128x64分辨率, I2C接口)
- LED (GPIO 2, 板载)
- 继电器 (GPIO 13, 可选)

## 接线说明

### OLED显示屏连接 (I2C接口)
| OLED引脚 | ESP32引脚 | 说明 |
|---------|----------|------|
| VCC     | 3.3V     | 电源 |
| GND     | GND      | 地线 |
| SCL     | GPIO 22  | I2C时钟线 |
| SDA     | GPIO 21  | I2C数据线 |

> 注意：大部分0.96寸OLED的I2C地址是`0x3C`，少数是`0x3D`。如果显示不工作，请在代码中修改`SCREEN_ADDRESS`。

## 功能说明

1. **GIF循环播放**：在OLED屏幕上循环播放转换后的GIF动画
2. **LED指示**：板载LED随帧闪烁，指示播放状态
3. **串口调试**：通过串口监视器查看运行状态（波特率115200）

## 使用方法

### 1. 安装依赖
```bash
pio lib install
```

### 2. 替换GIF文件（可选）
如果要显示自己的GIF：
1. 将GIF文件放入 `assets/` 目录
2. 编辑 `convert_gif.py` 中的文件路径
3. 运行转换脚本：
   ```bash
   python3 convert_gif.py
   ```
4. 这将生成新的 `include/gif_frames.h` 文件

### 3. 编译并上传
```bash
# 编译
pio run

# 编译并上传到ESP32
pio run --target upload

# 查看串口输出
pio device monitor
```

## 当前配置

- **GIF文件**：`assets/1321321.gif` (120x120像素, 28帧)
- **显示分辨率**：128x64 (居中显示)
- **帧率**：约10 FPS (每帧100ms)
- **I2C地址**：0x3C

## 调整参数

### 修改播放速度
在 `src/main.cpp` 中找到：
```cpp
const int FRAME_DELAY = 100; // 每帧延迟100ms
```
- 减小数值 = 播放更快
- 增大数值 = 播放更慢

### 修改I2C地址
如果OLED不显示，尝试修改：
```cpp
#define SCREEN_ADDRESS 0x3C  // 改为 0x3D 试试
```

### 扫描I2C设备
可以使用I2C扫描工具确认OLED地址：
```cpp
// 在setup()中添加I2C扫描代码
Wire.begin();
for(byte address = 1; address < 127; address++) {
  Wire.beginTransmission(address);
  if(Wire.endTransmission() == 0) {
    Serial.print("I2C device found at 0x");
    Serial.println(address, HEX);
  }
}
```

## 文件说明

```
CatDance/
├── assets/
│   └── 1.gif          # 原始GIF文件
├── include/
│   └── gif_frames.h         # 自动生成的C数组帧数据
├── src/
│   └── main.cpp             # 主程序
├── convert_gif.py           # GIF转换脚本
├── platformio.ini           # PlatformIO配置
└── README.md                # 本文件
```

## 故障排查

### OLED不显示
1. 检查接线是否正确
2. 确认OLED工作电压（应为3.3V）
3. 尝试修改I2C地址（0x3C或0x3D）
4. 查看串口输出的错误信息

### 显示异常
1. 确认GIF转换正确（查看 `include/gif_frames.h` 是否存在）
2. 检查电源供电是否足够（USB供电可能不稳定）

### 编译错误
1. 确保安装了PlatformIO
2. 运行 `pio lib install` 安装依赖库

## 依赖库

- Adafruit SSD1306 (^2.5.7)
- Adafruit GFX Library (^1.11.3)

## 开发环境

- PlatformIO
- Arduino框架
- ESP32平台

## 许可

MIT License

