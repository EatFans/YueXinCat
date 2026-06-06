#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "gif_frames.h"

// 硬件引脚定义
#define LED_PIN 2
#define RELAY_PIN 13

// OLED显示屏配置
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1        // 没有复位引脚
#define SCREEN_ADDRESS 0x3C  // I2C地址（大部分0.96寸OLED是0x3C，少数是0x3D）

// 创建OLED显示对象
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// GIF动画控制变量
int currentFrame = 0;
unsigned long lastFrameTime = 0;
const int FRAME_DELAY = 100; // 每帧延迟100ms（约10fps）

void setup()
{
  // 初始化串口（用于调试）
  Serial.begin(115200);
  Serial.println("CatDance OLED Display Starting...");

  // 初始化GPIO
  pinMode(LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  // 初始化OLED显示屏
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS))
  {
    Serial.println(F("SSD1306初始化失败！"));
    Serial.println(F("请检查OLED连接："));
    Serial.println(F("  SDA -> GPIO 21 (或默认I2C SDA引脚)"));
    Serial.println(F("  SCL -> GPIO 22 (或默认I2C SCL引脚)"));
    Serial.println(F("  VCC -> 3.3V"));
    Serial.println(F("  GND -> GND"));
    while (1)
      ; // 停止程序
  }

  // 显示欢迎信息
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(F("CatDance"));
  display.println(F("OLED GIF Player"));
  display.println();
  display.print(F("Frames: "));
  display.println(FRAME_COUNT);
  display.print(F("Resolution: "));
  display.print(FRAME_WIDTH);
  display.print(F("x"));
  display.println(FRAME_HEIGHT);
  display.display();

  delay(2000); // 显示欢迎信息2秒

  Serial.println(F("OLED初始化成功！"));
  Serial.print(F("GIF总帧数: "));
  Serial.println(FRAME_COUNT);
}

void loop()
{
  unsigned long currentTime = millis();

  // 检查是否需要更新帧
  if (currentTime - lastFrameTime >= FRAME_DELAY)
  {
    lastFrameTime = currentTime;

    // 从PROGMEM读取当前帧数据
    const unsigned char *frameData = (const unsigned char *)pgm_read_ptr(&frames[currentFrame]);

    // 显示当前帧
    display.clearDisplay();
    display.drawBitmap(0, 0, frameData, FRAME_WIDTH, FRAME_HEIGHT, SSD1306_WHITE);
    display.display();

    // 移动到下一帧（循环播放）
    currentFrame++;
    if (currentFrame >= FRAME_COUNT)
    {
      currentFrame = 0; // 循环回到第一帧
    }

    // LED闪烁指示（同步播放节奏）
    digitalWrite(LED_PIN, currentFrame % 2);
  }

}
