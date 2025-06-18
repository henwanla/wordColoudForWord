from PIL import Image
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# --------------------------
# 1. 配置参数
# --------------------------
# 词云使用的字体路径（确保支持中文）
font_path = "/System/Library/Fonts/STHeiti Medium.ttc"  # macOS 系统字体示例

# 输入文件路径
mask_image_path = "banner.png"      # 蒙版图片
names_file_path = "name.txt"        # 名字列表文件

# 输出文件路径
output_image_path = "wordcloud_output.png"

# --------------------------
# 2. 读取名字列表
# --------------------------
def read_names(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到名字文件: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]
    return names

names = read_names(names_file_path)
if not names:
    raise ValueError("名字文件为空")

# --------------------------
# 3. 加载蒙版图片
# --------------------------
if not os.path.exists(mask_image_path):
    raise FileNotFoundError(f"找不到蒙版图片: {mask_image_path}")

mask_image = Image.open(mask_image_path).convert("L")  # 转为灰度图
print(f"Image size: {mask_image.size}")  # 打印图像尺寸
print(f"Image mode: {mask_image.mode}")  # 打印图像模式

text_mask = np.array(mask_image)

# 添加调试信息，检查 text_mask 的值
print(f"text_mask shape: {text_mask.shape}")
print(f"text_mask unique values: {np.unique(text_mask)}")

# --------------------------
# 4. 生成词云
# --------------------------
# 构建词云文本（名字用空格分隔）
wordcloud_text = " ".join(names)

# 创建词云对象
wordcloud = WordCloud(
    font_path=font_path,
    mask=text_mask,
    background_color="white",      # 设置为 None 实现透明背景
    mode="RGBA",               # 支持透明通道
    # prefer_horizontal=1.0,       # 强制尽可能多的文字横向显示
    max_words=len(wordcloud_text.split(" ")) + 3,  # 先按空格分割 names，再计算数量并加 3
    collocations=True          # 防止重复组合词
)

# 生成词云
wordcloud.generate(wordcloud_text)

# 强制设置字体颜色为白色
# wordcloud = wordcloud.recolor(color_func=lambda *args, **kwargs: (255, 255, 255))

# --------------------------
# 5. 显示与保存结果
# --------------------------
# 显示词云
plt.figure(figsize=(12, 8))  # 修改为更大的画布 (width=12, height=8)
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# 保存高清 PNG 图片（600 dpi）
wordcloud.to_file(output_image_path)
image = wordcloud.to_image()
image.save(output_image_path, dpi=(600, 600))  # 提高 DPI 值以增强清晰度
print(f"✅ 已生成高清透明背景词云图片：{output_image_path}")

