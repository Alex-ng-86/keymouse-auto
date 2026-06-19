from PIL import Image, ImageDraw

def create_icon():
    # 尺寸
    size = 256
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # 颜色
    bg_color = "#3B8ED0"  # CustomTkinter 标志性蓝色
    c_color = "#FFFFFF"   # 白色
    
    # 背景：圆角矩形
    padding = 20
    radius = 60
    d.rounded_rectangle(
        [(padding, padding), (size - padding, size - padding)], 
        radius=radius, 
        fill=bg_color
    )
    
    # 外圈
    c_padding = 70
    c_thickness = 40
    
    # 上横
    d.rounded_rectangle([(c_padding, c_padding), (size - c_padding, c_padding + c_thickness)], radius=10, fill=c_color)
    # 下横
    d.rounded_rectangle([(c_padding, size - c_padding - c_thickness), (size - c_padding, size - c_padding)], radius=10, fill=c_color)
    # 左竖
    d.rounded_rectangle([(c_padding, c_padding), (c_padding + c_thickness, size - c_padding)], radius=10, fill=c_color)
    
    # 上右端点
    d.rounded_rectangle([(size - c_padding - c_thickness, c_padding), (size - c_padding, c_padding + c_thickness)], radius=10, fill=c_color)
    # 下右端点
    d.rounded_rectangle([(size - c_padding - c_thickness, size - c_padding - c_thickness), (size - c_padding, size - c_padding)], radius=10, fill=c_color)

    
    # 清除之前的绘制
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(padding, padding), (size - padding, size - padding)], radius=radius, fill=bg_color)
    
    # C 的参数
    c_left = 70
    c_top = 70
    c_right = 186
    c_bottom = 186
    thickness = 45
    
    # 左竖条
    d.rectangle([(c_left, c_top), (c_left + thickness, c_bottom)], fill=c_color)
    # 上横条
    d.rectangle([(c_left, c_top), (c_right, c_top + thickness)], fill=c_color)
    # 下横条
    d.rectangle([(c_left, c_bottom - thickness), (c_right, c_bottom)], fill=c_color)
    
    # 保存
    img.save('app_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

if __name__ == "__main__":
    create_icon()
