from geopy.geocoders import Nominatim

def get_coordinates(address):
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        location = geolocator.geocode(address, timeout=10)  # 增加超时时间到10秒
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except:
        print("无法获取坐标。请检查地址或网络连接。")
        return None

# 使用示例
address = "1600 Amphitheatre Parkway, Mountain View, CA"
coordinates = get_coordinates(address)
if coordinates:
    print(f"坐标为：{coordinates}")
else:
    print("无法找到该地点的坐标。")