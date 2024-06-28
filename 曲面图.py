import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import string
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import Akima1DInterpolator


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


def generate_3d_surface(z_matrix, num_points=10):
    # 插值以增加点的数量
    new_x, new_y, new_z_matrix = interpolate_surface(z_matrix, num_points)

    # 创建网格
    new_x_grid, new_y_grid = np.meshgrid(new_x, new_y)

    # 绘制三维曲面图
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(new_x_grid, new_y_grid, new_z_matrix, cmap='Blues')

    # 设置X轴和Y轴的刻度位置和标签
    ax.set_xticks(new_x)
    ax.set_xticklabels(new_x)
    ax.set_yticks(new_y)
    ax.set_yticklabels(new_y)

    # 隐藏X轴和Y轴的坐标标签
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    # 绘制颜色条
    plt.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

    # 设置坐标轴标签
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_zlabel('Z Values')

    return fig


def main():
    st.title('Excel数值矩阵三维曲面图生成器')

    # 用户上传Excel文件
    uploaded_file = st.file_uploader("上传你的Excel文件", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # 读取Excel文件并转换为矩阵
        z_matrix = read_excel_and_convert_to_matrix(uploaded_file)

        # 用户可以调整插入点的数量
        num_points = st.sidebar.slider("调整插入点数量", 1, 20, 10)

        # 生成三维曲面图
        fig = generate_3d_surface(z_matrix, num_points)

        # 显示图形
        st.pyplot(fig)


if __name__ == '__main__':
    main()