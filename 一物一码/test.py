import streamlit as st
import pandas as pd

# 定义一个函数来加载数据
def load_data(filepath):
    return pd.read_excel(filepath)

# 定义一个函数来过滤数据
def filter_data(df, data_type_selected, other_filters):
    # 如果数据类型被选中，则过滤数据类型
    if data_type_selected:
        df = df[df['数据类型'].isin(data_type_selected)]
    # 根据其他文本框输入过滤数据
    for col, value in other_filters.items():
        if value:  # 如果文本框有输入，则过滤
            df = df[df[col].str.contains(value, case=False, na=False)]
    return df

# 主函数
def main():
    st.title('药品信息查询页面')

    # 加载Excel文件（只在应用启动时加载一次）
    file_path = 'D:\\泰康\\ST\\西药中成药信息-拆分1-西药_有效_50%.xlsx'  # 替换为你的Excel文件路径
    if 'df' not in st.session_state:
        st.session_state['df'] = load_data(file_path)

    # 设置“数据类型”的下拉多选框选项
    data_type_options = [
        "一级项目-药品识别",
        "二级项目-解剖学",
        "三级项目-治疗学",
        "四级项目-治疗亚组",
        "五级项目-化学/疗法",
        "六级项目-通用名",
        "七级项目-通用名+标准剂型",
        "标准代码"
    ]
    data_type_selected = st.multiselect(
        '数据类型',
        data_type_options,
        []  # 默认不选择任何项
    )

    # 创建其他查询框
    other_filters = {
        '药品分类': st.text_input('药品分类', value=''),
        '药品代码': st.text_input('药品代码', value=''),
        '注册名称': st.text_input('注册名称', value=''),
        '批准文号': st.text_input('批准文号', value=''),
        '药品本位码': st.text_input('药品本位码', value='')
    }

    # 过滤数据
    filtered_df = filter_data(st.session_state['df'], data_type_selected, other_filters)

    # 显示结果
    if data_type_selected or any(value for value in other_filters.values()):
        st.write("查询结果:")
        st.dataframe(filtered_df.head(10))
    else:
        st.write("没有输入查询条件，显示前10行数据:")
        st.dataframe(st.session_state['df'].head(10))

if __name__ == "__main__":
    main()