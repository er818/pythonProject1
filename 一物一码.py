pip install openpyxl
import streamlit as st
import pandas as pd
from datetime import datetime

# 使用session_state来存储数据和登录状态
session_data = st.session_state.setdefault("session_data", {
    "uploaded_data": {},
    "login_status": False,
    "last_login_username": None
})

# 预定义的账号和密码
USERNAME = "sysadmin"
PASSWORD = "password"


# 定义加载数据函数
def load_data(file_path):
    return pd.read_excel(file_path)


# 定义登录页面
def login_page():
    st.title("登录页面")
    username = st.text_input("账号:", value="")
    password = st.text_input("密码:", type="password", value="")

    if st.button("登录"):
        if username == USERNAME and password == PASSWORD:
            session_data["login_status"] = True
            session_data["last_login_username"] = username
            st.write("登录成功！")
        else:
            st.write("账号或密码错误！请重试。")


# 定义检查登录状态的函数
def check_login():
    if not session_data["login_status"]:
        login_page()


# 定义上传管理页面
def upload_management_page():
    if not session_data.get("login_status", False):
        login_page()
        return

    st.title("上传管理页面")
    categories = ["👩🏻‍⚕️疾病诊断-D", "🚑手术操作-O", "🩺医疗服务项目-I",
        "💊西药中成药-Y", "🪷中药饮片-T", "💉医用耗材-C",
        "🏩医疗机构-H", "📑体检项目-E"]

    for category in categories:
        key = category.lower().replace(" ", "_")
        # 检查 session_data 中是否已经存在对应的列表
        if key not in session_data or not isinstance(session_data[key], list):
            session_data[key] = []

        uploaded_file = st.file_uploader(f"上传 {category} 的数据表：", type=["xlsx", "xls"])
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            df.attrs['filename'] = uploaded_file.name
            session_data["uploaded_data"][key] = df
            # 记录上传信息并添加到列表
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            uploader = session_data["last_login_username"]  # 获取当前登录的用户名
            upload_info = {
                "filename": df.attrs['filename'],
                "upload_time": upload_time,
                "uploader": uploader,  # 记录上传人信息
                "entry_count": len(df)  # 记录文件条目数
            }
            session_data[key].append(upload_info)
            st.write(f"{category} 的数据表已上传，文件名：{uploaded_file.name}，条目数：{len(df)}")

# 定义已上传数据信息展示页面
def uploaded_data_info_page():
    st.title("已上传数据信息")

    # 遍历 session_data 中的上传记录
    for key, records in session_data.items():
        if isinstance(records, list):  # 确保是列表
            st.header(key.title().replace("_", " "))
            for record in records:
                filename = record["filename"]
                upload_time = record["upload_time"]
                uploader = record.get("uploader", "未知用户")  # 获取上传人信息，如果没有则显示未知用户
                entry_count = record.get("entry_count", 0)  # 获取条目数，如果没有则默认为0
                st.write(f"- 文件名：{filename}，上传时间：{upload_time}，"
                         f"条目数：{entry_count}，上传人：{uploader}")


# 定义查询页面的逻辑
def query_page(category, data_key):
    st.title(f"{category} 查询页面")

    # 获取存储的数据表
    df = session_data["uploaded_data"].get(data_key, pd.DataFrame())

    # 检查数据表是否为空
    if df.empty:
        st.error("查询的数据表为空。")
        return

    # 获取数据类型列作为复选框选项
    data_type_col = "数据类型"
    if data_type_col in df.columns:
        data_types = df[data_type_col].unique()
        selected_data_types = st.multiselect(f"选择{data_type_col}（多选）：", data_types, default=[])
    else:
        st.error(f"数据表中没有找到 '{data_type_col}' 列。")
        return

    # 获取其他列名，排除索引列和“数据类型”列
    other_columns = [col for col in df.columns.tolist() if col != data_type_col]

    # 找出包含“名称”的列名，默认选中这些列
    default_columns = [col for col in other_columns if "名称" in col]
    selected_columns = st.multiselect("请选择想要查询的列（多选）：", other_columns, default=default_columns)

    # 初始化查询条件字典
    query_conditions = {}
    # 为每个选中的列创建查询条件输入框
    for col in selected_columns:
        query_input = st.text_input(f"输入 {col} 的查询条件：")
        if query_input:  # 如果用户输入了查询条件
            query_conditions[col] = query_input

    # 过滤数据
    filtered_df = df
    if query_conditions:
        for col, query in query_conditions.items():
            filtered_df = filtered_df[filtered_df[col].str.contains(query, case=False, na=False)]

    # 显示查询结果
    st.write("查询结果：")
    if filtered_df.empty:
        st.info("没有找到匹配的记录。显示前10行数据：")
        st.dataframe(df.head(10))
    else:
        st.dataframe(filtered_df.head(10))  # 展示前10行匹配的数据


# 为每个类别创建查询页面的快捷方式
def create_query_pages(categories):
    return {f"{category} 查询": lambda category=category: query_page(category, category.lower().replace(" ", "_")) for
            category in categories}


# 主函数
def main():
    st.title("一物一码数据标准管理应用")

    # 创建查询页面选项
    query_pages = create_query_pages([
        "👩🏻‍⚕️疾病诊断-D", "🚑手术操作-O", "🩺医疗服务项目-I",
        "💊西药中成药-Y", "🪷中药饮片-T", "💉医用耗材-C",
        "🏩医疗机构-H", "📑体检项目-E"
    ])

    # 设置侧边栏和页面选择
    with st.sidebar:
        pages = {
            **query_pages,  # 添加查询页面选项
            "上传管理": upload_management_page,
            "已上传数据信息": uploaded_data_info_page,
        }
        selected_page = st.radio("选择页面:", list(pages.keys()))

    # 根据用户选择显示相应页面
    if selected_page in query_pages:
        query_pages[selected_page]()  # 调用查询页面函数
    else:
        pages[selected_page]()  # 调用其他页面函数


if __name__ == "__main__":
    main()