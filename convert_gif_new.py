#!/usr/bin/env python3
"""
GIF转换工具：将多个GIF转换为适合SSD1306 OLED显示的C数组格式
分辨率：128x64，单色位图
支持多个GIF按顺序播放
"""

from PIL import Image
import os

def process_single_gif(gif_path, width=128, height=64):
    """
    处理单个GIF文件，返回所有帧数据
    """
    print(f"处理: {gif_path}")
    img = Image.open(gif_path)
    frames = []

    try:
        while True:
            # 调整大小并居中
            frame = img.convert('L')  # 转换为灰度

            # 计算居中位置
            orig_w, orig_h = frame.size
            scale = min(width / orig_w, height / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)

            # 调整大小
            frame = frame.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # 创建黑色背景并居中粘贴
            canvas = Image.new('L', (width, height), 0)
            offset_x = (width - new_w) // 2
            offset_y = (height - new_h) // 2
            canvas.paste(frame, (offset_x, offset_y))

            # 转换为单色位图（阈值127）
            canvas = canvas.point(lambda x: 255 if x > 127 else 0, '1')

            # 转换为字节数组（水平位图格式，适合drawBitmap）
            # 每个字节表示8个水平像素，MSB在左
            frame_bytes = []
            for y in range(height):
                for x in range(0, width, 8):
                    byte = 0
                    for bit in range(8):
                        if x + bit < width:
                            pixel = canvas.getpixel((x + bit, y))
                            if pixel:
                                byte |= (0x80 >> bit)  # MSB first
                    frame_bytes.append(byte)

            frames.append(frame_bytes)
            img.seek(img.tell() + 1)  # 下一帧
    except EOFError:
        pass  # 所有帧处理完毕

    print(f"  ✓ {len(frames)} 帧")
    return frames

def gifs_to_oled_frames(gif_paths, output_path, width=128, height=64):
    """
    将多个GIF按顺序转换为OLED显示帧数组
    """
    all_frames = []
    gif_info = []  # 记录每个GIF的起始帧和帧数

    for gif_path in gif_paths:
        if not os.path.exists(gif_path):
            print(f"警告: 文件不存在 {gif_path}")
            continue

        start_frame = len(all_frames)
        frames = process_single_gif(gif_path, width, height)
        all_frames.extend(frames)
        gif_info.append({
            'path': gif_path,
            'start': start_frame,
            'count': len(frames)
        })

    total_frames = len(all_frames)
    print(f"\n总计: {total_frames} 帧 (来自 {len(gif_info)} 个GIF)")

    # 生成C代码
    with open(output_path, 'w') as f:
        f.write("// Auto-generated from multiple GIFs\n")
        f.write("// OLED Resolution: 128x64\n")
        f.write(f"// Total frames: {total_frames}\n")
        f.write(f"// GIF count: {len(gif_info)}\n\n")

        for i, info in enumerate(gif_info):
            f.write(f"// GIF {i+1}: {os.path.basename(info['path'])} - "
                   f"Frames {info['start']} to {info['start'] + info['count'] - 1} "
                   f"({info['count']} frames)\n")
        f.write("\n")

        f.write("#ifndef GIF_FRAMES_H\n")
        f.write("#define GIF_FRAMES_H\n\n")
        f.write("#include <Arduino.h>\n\n")
        f.write(f"#define FRAME_COUNT {total_frames}\n")
        f.write(f"#define FRAME_WIDTH {width}\n")
        f.write(f"#define FRAME_HEIGHT {height}\n")
        f.write(f"#define FRAME_SIZE {width * height // 8}\n")
        f.write(f"#define GIF_COUNT {len(gif_info)}\n\n")

        # GIF信息结构
        f.write("// GIF animation info\n")
        f.write("struct GifInfo {\n")
        f.write("    int startFrame;\n")
        f.write("    int frameCount;\n")
        f.write("};\n\n")

        f.write("const GifInfo gifInfo[GIF_COUNT] PROGMEM = {\n")
        for i, info in enumerate(gif_info):
            f.write(f"    {{{info['start']}, {info['count']}}}")
            if i < len(gif_info) - 1:
                f.write(",")
            f.write(f"  // GIF {i+1}: {os.path.basename(info['path'])}\n")
        f.write("};\n\n")



        # 写入每一帧数据
        for i, frame_data in enumerate(all_frames):
            f.write(f"const unsigned char PROGMEM frame_{i}[{len(frame_data)}] = {{\n")
            for j in range(0, len(frame_data), 16):
                line = ", ".join(f"0x{b:02X}" for b in frame_data[j:j+16])
                f.write(f"    {line}")
                if j + 16 < len(frame_data):
                    f.write(",")
                f.write("\n")
            f.write("};\n\n")

        # 创建帧指针数组
        f.write(f"const unsigned char* const frames[FRAME_COUNT] PROGMEM = {{\n")
        for i in range(total_frames):
            f.write(f"    frame_{i}")
            if i < total_frames - 1:
                f.write(",")
            f.write("\n")
        f.write("};\n\n")
        f.write("#endif // GIF_FRAMES_H\n")

    print(f"\n✓ 转换完成！")
    print(f"✓ 输出文件：{output_path}")

if __name__ == "__main__":
    # 定义要转换的GIF文件（按顺序）
    gif_files = [
        "assets/1.gif",
        "assets/2.gif",
        "assets/3.gif",
        "assets/4.gif",
        "assets/5.gif"
    ]

    output_path = "include/gif_frames.h"

    print("=" * 50)
    print("多GIF转OLED格式转换工具")
    print("=" * 50)

    gifs_to_oled_frames(gif_files, output_path)

    print("=" * 50)
