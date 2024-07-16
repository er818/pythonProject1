import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import string
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import Akima1DInterpolator

# 设置中文字体以支持中文标签显示
st.markdown("""
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono&family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

def read_excel_and_convert_to_matrix(file_path):
    # 读取Excel文件
    data = pd.read_excel(file_path)

    # 转换为二维NumPy数组
    z_matrix = data.to_numpy()
    return z_matrix


def interpolate_surface(z_matrix, num_points=10):
    # 获取原始X和Y轴的坐标点
    x = np.arange(z_matrix.shape[1])
    y = np.arange(z_matrix.shape[0])

    # 创建插值对象
    interpolator = Akima1DInterpolator(y, z_matrix)

    # 生成新的X和Y坐标点
    new_y = np.linspace(y[0], y[-1], num=num_points * y.size)
    new_x = np.linspace(x[0], x[-1], num=num_points * x.size)

    # 使用Akima1DInterpolator进行插值
    new_z_matrix = interpolator(new_y[:, None])  # 扩展维度以匹配interp1d的要求

    # 重新网格化插值结果
    from scipy.interpolate import RectBivariateSpline
    rbf = RectBivariateSpline(y, x, z_matrix)
    new_z_matrix = rbf(new_y, new_x)

    return new_x, new_y, new_z_matrix


def generate_3d_surface(z_matrix, num_points=10, azimuth=280, elevation=30, x_label='X Axis', y_label='Y Axis', z_label='Z Values'):
    # 插值以增加点的数量
    new_x, new_y, new_z_matrix = interpolate_surface(z_matrix, num_points)

    # 创建网格
    new_x_grid, new_y_grid = np.meshgrid(new_x, new_y)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(new_x_grid, new_y_grid, new_z_matrix, cmap='Blues')

    #设置初始视角
    ax.view_init(elev=elevation, azim=azimuth)

    # 使用原始Z矩阵的尺寸设置X轴和Y轴的网格线数量
    ax.set_xticks(np.arange(z_matrix.shape[1]))  # X轴网格线数量等于列数
    ax.set_yticks(np.arange(z_matrix.shape[0]))  # Y轴网格线数量等于行数

    # 隐藏X轴和Y轴的坐标标签
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # 绘制颜色条
    plt.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.15)

    # 设置坐标轴标签为用户输入的标题
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)

    # 设置坐标轴标签
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)

    # 隐藏X轴和Y轴的坐标标签
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # 返回图形对象
    return fig


def main():
    st.title('Excel数值矩阵三维曲面图生成器')

    # 用户上传Excel文件
    uploaded_file = st.file_uploader("上传你的Excel文件，纯数列矩阵，行为X轴，列为Y轴", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # 读取Excel文件并转换为矩阵
        z_matrix = read_excel_and_convert_to_matrix(uploaded_file)

        # 用户可以调整插入点的数量
        num_points = st.sidebar.slider("调整插入点数量", 1, 20, 10)

        # 初始视角
        initial_azim = 280
        initial_elev = 30

        # 用户可以设置视角
        azimuth = st.sidebar.slider("设置方位角(0-360度)", 0, 360, initial_azim)
        elevation = st.sidebar.slider("设置仰角(-90-90度)", -90, 90, initial_elev)

        # 一键回到初始视角的按钮
        reset_button = st.button("回到初始视角")

        # 如果用户点击了重置按钮，则重置视角
        if reset_button:
            azimuth = initial_azim
            elevation = initial_elev

        # 用户输入XYZ轴标题
        x_label = st.sidebar.text_input("X轴标题", value="X Axis")
        y_label = st.sidebar.text_input("Y轴标题", value="Y Axis")
        z_label = st.sidebar.text_input("Z轴标题", value="Z Values")

        # 生成三维曲面图
        fig = generate_3d_surface(z_matrix, num_points, azimuth, elevation, x_label, y_label, z_label)

        # 显示图形
        st.pyplot(fig)

# 确保脚本作为主程序运行时才执行main函数
if __name__ == '__main__':
    main()