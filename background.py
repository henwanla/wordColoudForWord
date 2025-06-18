from PIL import Image, ImageDraw, ImageFont
import os

def generate_banner(output_path="banner.png", text=None):
    """生成带文字的高清 PNG 横幅图片
    
    Args:
        output_path: 输出图片路径
        text: 要绘制的文字内容
    """
    # 设置默认文本
    if text is None:
        text = "青春不散场"
        # text = "青春不散场 一起闯未来 2025我们毕业啦"

    # 设置字体路径（尝试不同系统字体）
    font_paths = [
        # "/System/Library/Fonts/STHeiti Medium.ttc",  # macOS
        "庞门正道粗书体.ttf"
    ]
    
    font_path = None
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            break
    
    if font_path is None:
        raise FileNotFoundError("未找到可用的中文字体，请手动指定字体路径")

    # 设置高清参数
    DPI = 600  # 提高DPI值
    SCALE_FACTOR = 2  # 画布尺寸放大倍数，避免缩放时模糊
    font_size = 1000  # 基础字体大小

    # 初始化字体
    try:
        font = ImageFont.truetype(font_path, size=font_size * SCALE_FACTOR, encoding="utf-8")
    except Exception as e:
        # 回退方案
        font = ImageFont.truetype(font_path, size=font_size * SCALE_FACTOR)

    # 计算文本尺寸
    dummy_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_w = right - left
    text_h = bottom - top

    # 设置画布尺寸
    padding = 60 * SCALE_FACTOR
    img_width = text_w + 2 * padding
    img_height = text_h + 2 * padding

    # 创建图像
    image = Image.new("RGBA", (img_width, img_height), color=(255, 255, 255, 255)) # 白色背景
    draw = ImageDraw.Draw(image)

    # 绘制文字（带描边）
    def draw_text_with_outline(draw, position, text, font, fill_color, outline_color, outline_width=2):
        """绘制带描边的文字"""
        for x_offset in range(-outline_width, outline_width + 1):
            for y_offset in range(-outline_width, outline_width + 1):
                if x_offset == 0 and y_offset == 0:
                    continue
                draw.text((position[0] + x_offset, position[1] + y_offset), 
                          text, font=font, fill=outline_color)
        draw.text(position, text, font=font, fill=fill_color)

    # 调用自定义描边绘制函数
    draw_text_with_outline(
        draw,
        (padding, padding),
        text,
        font,
        fill_color=(0, 0, 0),  # 黑色文字
        outline_color=(255, 255, 255),  # 白色描边
        outline_width=0
    )

    # 保存前缩小到目标尺寸
    if SCALE_FACTOR > 1:
        target_width = int(img_width / SCALE_FACTOR)
        target_height = int(img_height / SCALE_FACTOR)
        image = image.resize((target_width, target_height), resample=Image.LANCZOS)

    # 保存为PNG
    image.save(output_path, dpi=(DPI, DPI), compress_level=0)
    print(f"✅ 已生成高清横幅图：{output_path} ({DPI} DPI)")

if __name__ == "__main__":
    generate_banner()