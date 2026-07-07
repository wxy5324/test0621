from PIL import Image
from omniparser import OmniParser

# 1. 加载模型（自动下载权重，首次稍慢）
parser = OmniParser()

# 2. 打开截图（支持 PNG/JPG）
image = Image.open("C:\\Users\\wxy\\Downloads\\桌面.png")

# 3. 执行解析（核心一行）
result = parser.parse(image)

# 4. 输出结果（所有可交互 UI 元素）
print("识别到的界面元素：")
for idx, elem in enumerate(result["elements"]):
    print(f"[{idx+1}] 类型: {elem['type']:10} | 文本: {elem['text'][:20]} | 坐标: {elem['bbox']}")