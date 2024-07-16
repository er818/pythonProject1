import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.interpolate import RectBivariateSpline
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

# 设置matplotlib使用支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 给定的项目和月份
projects = ['学校', '酒店', '充电桩', '明厨亮灶', '快递', '智慧社区', '商铺']
months = ['23.01', '23.02', '23.03', '23.04', '23.05', '23.06',
          '23.07', '23.08', '23.09', '23.10', '23.11', '23.12',
          '24.01', '24.02', '24.03', '24.04', '24.05', '24.06', '24.07']
# 转换月份格式
formatted_months = [f"{m.split('.')[0]}年{int(m.split('.')[1])}月" for m in months]

# 给定的数据
data = {
    '学校': [1,0,1,0,0,0,0,0,0,0,45,0,1,1,0,0,20,0,0],
    '酒店': [0,0,0,0,0,0,0,1,0,0,0,0,0,9,0,0,0,0,0],
    '充电桩': [0,0,0,1,0,0,0,0,0,17,0,17,34,0,0,0,0,0,0],
    '明厨亮灶': [0,0,0,0,0,0,0,15,4,16,0,0,0,0,0,2,0,0,0],
    '快递': [0,0,0,0,0,0,0,0,0,0,12,27,5,0,0,0,0,0,0],
    '智慧社区': [21,61,64,82,24,47,20,15,25,19,30,8,13,2,17,21,38,15,20],
    '商铺': [20,33,85,15,11,191,84,19,13,49,348,249,9,12,9,34,35,12,1]
}

# 将数据字典转换为二维数组
data_array = np.array([[data[project][month_index] if month_index < len(data[project]) else 0
                        for month_index in range(len(months))] for project in projects])

# 为插值准备 x 和 y 的值
x_values = np.arange(len(months))
y_values = np.arange(len(projects))

# 创建插值函数
interp_func = RectBivariateSpline(x_values, y_values, data_array.T)

# 在矩形网格上生成更多的点以进行平滑
xi = np.linspace(x_values.min(), x_values.max(), 100)
yi = np.linspace(y_values.min(), y_values.max(), 100)
X, Y = np.meshgrid(xi, yi)

# 使用插值函数计算新网格上的值
Z = interp_func.ev(X, Y)

# 定义自定义的蓝色渐变颜色列表
RGB = [(1, 1, 1),  # 浅蓝色
       (0.6, 0.7, 1),  # 适中的蓝色
       (0.2, 0.3, 0.5)]  # 深蓝色

# 创建自定义的色图
my_cmap = LinearSegmentedColormap.from_list('RGB', RGB)

# 创建归一化对象
norm = Normalize(vmin=Z.min(), vmax=Z.max())

# 创建ScalarMappable对象
mappable = ScalarMappable(norm=norm, cmap=my_cmap)

# 绘制3D曲面图
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 使用自定义颜色映射绘制曲面图
surf = ax.plot_surface(X, Y, Z, facecolors=mappable.to_rgba(Z), shade=False)

# 设置轴标签
ax.set_xlabel('Months')
ax.set_ylabel('Projects', rotation=0)
ax.set_zlabel('Quantity')

# 设置X轴的刻度标签
ax.set_xticks(x_values)
ax.set_xticklabels(months, rotation=45)

# 设置Y轴的刻度标签为项目名称
ax.set_yticks(y_values)
ax.set_yticklabels(projects)

# 添加颜色条
fig.colorbar(mappable, ax=ax)

# 显示图表
plt.show()