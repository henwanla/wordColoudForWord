#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
毕业词云生成器
实现从文字蒙版生成到名字词云的全流程自动化
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import random


class TextMaskGenerator:
    """文字蒙版生成器"""
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        初始化蒙版生成器
        
        Args:
            width: 画布宽度
            height: 画布高度
        """
        self.width = width
        self.height = height
    
    def generate_mask(self, 
                     text: str, 
                     font_size: int = 80,
                     font_path: Optional[str] = None,
                     output_path: str = "text_mask.png") -> str:
        """
        生成文字蒙版 - 白色文字作为词云填充区域
        
        Args:
            text: 要生成蒙版的文字
            font_size: 字体大小
            font_path: 字体文件路径，None使用默认字体
            output_path: 输出文件路径
            
        Returns:
            生成的蒙版文件路径
        """
        # 创建白色背景图像（WordCloud中白色区域不会放置文字，黑色区域会放置文字）
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)
        
        # 设置字体
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 尝试使用常见的中文字体
                font_paths = [
                    "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
                    "C:/Windows/Fonts/msyh.ttf",    # Windows 微软雅黑
                    "C:/Windows/Fonts/simsun.ttc",  # Windows 宋体
                    "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 黑体
                    "/System/Library/Fonts/Songti.ttc",  # macOS 宋体
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux 中文
                ]
                
                font = None
                for path in font_paths:
                    if os.path.exists(path):
                        font = ImageFont.truetype(path, font_size)
                        print(f"使用字体: {path}")
                        break
                
                if font is None:
                    font = ImageFont.load_default()
                    print("警告：未找到合适的字体文件，使用默认字体")
        except Exception as e:
            print(f"字体加载失败，使用默认字体: {e}")
            font = ImageFont.load_default()
        
        # 计算文字位置（居中）
        # 对于多行文字，按换行符分割
        lines = text.split('\n') if '\n' in text else [text]
        
        # 计算每行的尺寸
        line_heights = []
        line_widths = []
        
        for line in lines:
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
            except:
                # 兼容旧版本PIL
                try:
                    width, height = draw.textsize(line, font=font)
                except:
                    # 如果textsize也不可用，使用估算
                    width = len(line) * font_size * 0.6
                    height = font_size
            
            line_widths.append(width)
            line_heights.append(height)
        
        # 计算行间距和总高度
        line_spacing = max(20, font_size // 4)  # 根据字体大小调整行间距
        total_height = sum(line_heights) + (len(lines) - 1) * line_spacing
        
        # 起始y坐标（垂直居中）
        start_y = (self.height - total_height) // 2
        
        # 绘制每一行（黑色文字，这样WordCloud会在这些区域放置词语）
        current_y = start_y
        for i, line in enumerate(lines):
            if line.strip():  # 跳过空行
                x = (self.width - line_widths[i]) // 2  # 水平居中
                draw.text((x, current_y), line, fill='black', font=font)
            current_y += line_heights[i] + line_spacing
        
        # 保存蒙版
        img.save(output_path)
        print(f"文字蒙版已生成: {output_path}")
        print(f"蒙版说明: 黑色文字区域将被学生名字填充")
        return output_path


class GraduationWordCloud:
    """毕业词云生成器"""
    
    def __init__(self):
        """初始化词云生成器"""
        self.mask_generator = None
    
    def set_mask_generator(self, mask_generator: TextMaskGenerator):
        """设置蒙版生成器"""
        self.mask_generator = mask_generator
    
    def generate_wordcloud(self,
                          names: List[str],
                          mask_path: str,
                          output_path: str = "graduation_wordcloud.png",
                          background_color: str = 'white',
                          colormap: str = 'plasma',
                          font_path: Optional[str] = None,
                          max_words: int = 300,
                          relative_scaling: float = 0.8,
                          min_font_size: int = 12,
                          prefer_horizontal: float = 0.9) -> str:
        """
        基于蒙版生成名字词云
        
        Args:
            names: 毕业生名字列表
            mask_path: 蒙版文件路径
            output_path: 输出文件路径
            background_color: 背景颜色
            colormap: 颜色方案
            font_path: 字体文件路径
            max_words: 最大词数
            relative_scaling: 相对缩放
            min_font_size: 最小字体大小
            prefer_horizontal: 水平文字比例
            
        Returns:
            生成的词云文件路径
        """
        # 读取蒙版
        if not os.path.exists(mask_path):
            raise FileNotFoundError(f"蒙版文件不存在: {mask_path}")
        
        mask_img = Image.open(mask_path)
        mask_array = np.array(mask_img)
        
        # 转换为灰度数组（WordCloud需要）
        if len(mask_array.shape) == 3:
            mask_array = np.mean(mask_array, axis=2)
        
        # WordCloud会在mask中值为0（黑色）的地方放置文字
        # 所以我们需要反转蒙版：让文字区域为0，背景区域为255
        mask_array = 255 - mask_array
        
        # 创建词频字典
        word_freq = {}
        
        # 确保有足够的名字来填充形状
        extended_names = names.copy()
        while len(extended_names) < max_words and len(names) > 0:
            extended_names.extend(names)
        
        # 为每个名字分配权重，让分布更自然
        for i, name in enumerate(extended_names[:max_words]):
            # 给不同的名字不同权重，创造大小变化
            base_weight = random.randint(3, 15)
            # 给原始名字列表中的名字更高权重
            if name in names:
                weight = base_weight + random.randint(2, 8)
            else:
                weight = base_weight
            
            # 避免重复名字权重累加
            if name in word_freq:
                word_freq[name] = max(word_freq[name], weight)
            else:
                word_freq[name] = weight
        
        print(f"生成词云，使用 {len(word_freq)} 个名字")
        
        # 设置字体路径
        font_path_to_use = None
        if font_path and os.path.exists(font_path):
            font_path_to_use = font_path
        else:
            # 尝试使用系统字体
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/msyh.ttf",
                "C:/Windows/Fonts/simsun.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/Songti.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    font_path_to_use = path
                    print(f"词云使用字体: {path}")
                    break
        
        # 创建WordCloud对象
        wordcloud = WordCloud(
            width=mask_img.width,
            height=mask_img.height,
            background_color=background_color,
            mask=mask_array,
            font_path=font_path_to_use,
            max_words=max_words,
            relative_scaling=relative_scaling,
            min_font_size=min_font_size,
            colormap=colormap,
            prefer_horizontal=prefer_horizontal,  # 偏好水平文字
            max_font_size=100,
            random_state=42,  # 固定随机种子以获得一致的结果
            collocations=False,  # 避免词语重复组合
            repeat=True  # 允许重复使用词语填充形状
        )
        
        # 生成词云
        wordcloud.generate_from_frequencies(word_freq)
        
        # 保存词云
        wordcloud.to_file(output_path)
        print(f"名字词云已生成: {output_path}")
        print(f"效果说明: 学生名字按照标语文字形状排列")
        return output_path
    
    def create_complete_wordcloud(self,
                                 slogan: str,
                                 names: List[str],
                                 canvas_size: Tuple[int, int] = (1200, 900),
                                 font_size: int = 120,
                                 mask_font_path: Optional[str] = None,
                                 wordcloud_font_path: Optional[str] = None,
                                 background_color: str = 'white',
                                 colormap: str = 'plasma',
                                 output_dir: str = "output") -> Tuple[str, str]:
        """
        完整流程：生成蒙版并创建词云
        让学生名字按照标语文字的形状排列
        
        Args:
            slogan: 标语文本（学生名字将按此文字形状排列）
            names: 毕业生名字列表
            canvas_size: 画布尺寸 (宽, 高)
            font_size: 蒙版字体大小
            mask_font_path: 蒙版字体文件路径
            wordcloud_font_path: 词云字体文件路径
            background_color: 背景颜色
            colormap: 颜色方案
            output_dir: 输出目录
            
        Returns:
            (蒙版文件路径, 词云文件路径)
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"开始生成毕业词云...")
        print(f"标语内容: {slogan.replace(chr(30), ' | ')}")
        print(f"学生人数: {len(names)}")
        print(f"画布尺寸: {canvas_size[0]} x {canvas_size[1]}")
        
        # 初始化蒙版生成器
        self.mask_generator = TextMaskGenerator(canvas_size[0], canvas_size[1])
        
        # 生成蒙版
        mask_path = os.path.join(output_dir, "text_mask.png")
        self.mask_generator.generate_mask(
            text=slogan,
            font_size=font_size,
            font_path=mask_font_path,
            output_path=mask_path
        )
        
        # 生成词云
        wordcloud_path = os.path.join(output_dir, "graduation_wordcloud.png")
        self.generate_wordcloud(
            names=names,
            mask_path=mask_path,
            output_path=wordcloud_path,
            background_color=background_color,
            colormap=colormap,
            font_path=wordcloud_font_path,
            max_words=min(300, len(names) * 3),  # 根据学生人数调整
            relative_scaling=0.8,
            min_font_size=12,
            prefer_horizontal=0.9
        )
        
        print(f"\n🎉 毕业词云生成完成！")
        print(f"📁 蒙版文件: {mask_path}")
        print(f"🎨 词云文件: {wordcloud_path}")
        print(f"💡 效果说明: 学生名字组成了 '{slogan.replace(chr(10), ' ')}'的文字形状")
        
        return mask_path, wordcloud_path


def main():
    """主函数示例"""
    # 标语文本 - 学生名字将按照这些文字的形状排列
    slogan = "青春不散场\n一起闯未来\n2025\n我们毕业啦"
    
    # 示例毕业生名字 - 这些名字将组成上面的文字形状
    names = [
        "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
        "郑十一", "王十二", "冯十三", "陈十四", "褚十五", "卫十六", "蒋十七", "沈十八",
        "韩十九", "杨二十", "朱二一", "秦二二", "尤二三", "许二四", "何二五", "吕二六",
        "施二七", "张二八", "孔二九", "曹三十", "严三一", "华三二", "金三三", "魏三四",
        "陶三五", "姜三六", "戚三七", "谢三八", "邹三九", "喻四十", "柏四一", "水四二",
        "窦四三", "章四四", "云四五", "苏四六", "潘四七", "葛四八", "奚四九", "范五十",
        "彭五一", "郎五二", "鲁五三", "韦五四", "昌五五", "马五六", "苗五七", "凤五八",
        "花五九", "方六十", "俞六一", "任六二", "袁六三", "柳六四", "酆六五", "鲍六六",
        "史六七", "唐六八", "费六九", "廉七十", "岑七一", "薛七二", "雷七三", "贺七四"
    ]
    
    # 创建词云生成器
    generator = GraduationWordCloud()
    
    try:
        print("🎓 毕业词云生成器")
        print("=" * 50)
        
        # 生成完整的词云
        mask_path, wordcloud_path = generator.create_complete_wordcloud(
            slogan=slogan,  # 这是名字要组成的文字形状
            names=names,    # 这些名字将填充到文字形状中
            canvas_size=(1600, 1200),  # 更大的画布获得更好效果
            font_size=150,              # 更大的字体让形状更清晰
            background_color='white',   # 白色背景更清晰
            colormap='plasma',          # 炫彩色彩方案
            output_dir="graduation_output"
        )
        
        print("\n" + "=" * 50)
        print("🎉 生成成功！")
        print(f"📄 蒙版文件: {mask_path}")
        print(f"🎨 词云文件: {wordcloud_path}")
        print(f"💡 查看 {wordcloud_path} 可以看到名字组成的文字效果")
        
        # 额外提示
        print("\n📝 使用说明:")
        print("- 蒙版文件显示了文字轮廓")
        print("- 词云文件中，学生名字按照标语文字形状排列")
        print("- 可以调整字体大小、颜色方案等参数优化效果")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()