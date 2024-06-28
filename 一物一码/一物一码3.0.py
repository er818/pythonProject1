import streamlit as st
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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
    if selected_data_types:  # 确保用户选择了数据类型
        filtered_df = filtered_df[filtered_df[data_type_col].isin(selected_data_types)]  # 根据选择的数据类型过滤

    # 应用查询条件
    if query_conditions:
        for col, query in query_conditions.items():
            filtered_df = filtered_df[filtered_df[col].str.contains(query, case=False, na=False)]

    # 显示查询结果
    st.write("查询结果：")
    if filtered_df.empty:
        st.info("没有找到匹配的记录。显示前10行数据：")
        st.dataframe(df.head(10))
    else:
        st.dataframe(filtered_df)

# 为每个类别创建查询页面的快捷方式
def create_query_pages(categories):
    return {f"{category} 查询": lambda category=category: query_page(category, category.lower().replace(" ", "_")) for
            category in categories}

# 定义映射页面
def mapping_page():
    st.title("映射页面")

    # 上传待映射数据表
    mapping_file = st.file_uploader("上传待映射数据表：", type=["xlsx", "xls"])
    if mapping_file is not None:
        mapping_df = load_data(mapping_file)
        st.write(f"待映射数据已上传，文件名：{mapping_file.name}，条目数：{len(mapping_df)}")
    else:
        st.warning("请上传待映射数据表。")
        return

    if mapping_df.empty:
        st.error("上传的待映射数据为空。")
        return

    # 从已上传的目标数据表中选择一个表
    target_tables = session_data.get("uploaded_data", {})
    if not target_tables:
        st.error("没有可映射的目标数据表，请先上传目标数据表。")
        return

    target_table_key = st.selectbox("选择目标数据表：", list(target_tables.keys()))
    target_df = target_tables.get(target_table_key)

    if target_df is None or target_df.empty:
        st.error("选择的目标数据表为空或未找到。")
        return

    # 让用户选择待映射数据的编码列和名称列
    mapping_columns = mapping_df.columns.tolist()
    selected_mapping_code_column = st.selectbox("选择待映射编码列：", mapping_columns)
    selected_mapping_name_column = st.selectbox("选择待映射名称列：", [col for col in mapping_columns if col != selected_mapping_code_column])

    # 让用户选择目标数据的编码列和名称列
    target_columns = target_df.columns.tolist()
    selected_target_code_column = st.selectbox("选择目标数据编码列：", target_columns)
    selected_target_name_column = st.selectbox("选择目标数据名称列：", [col for col in target_columns if col != selected_target_code_column])

    # 执行匹配逻辑
    new_rows = []  # 初始化列表来收集所有行的数据

    for index, row in mapping_df.iterrows():
        match_type = None
        match_score = None
        matched_row = None

        # 尝试名称完全匹配
        name_exact_match = target_df[target_df[selected_target_name_column] == row[selected_mapping_name_column]]

        if not name_exact_match.empty:
            match_type = '名称精确匹配'
            matched_row = name_exact_match.iloc[0]
        else:
            # 名称未匹配，尝试编码完全匹配
            code_exact_match = target_df[target_df[selected_target_code_column] == row[selected_mapping_code_column]]
            if not code_exact_match.empty:
                match_type = '编码精确匹配'
                matched_row = code_exact_match.iloc[0]
            else:
                # 编码也未匹配，尝试名称模糊匹配
                fuzzy_result = process.extractOne(row[selected_mapping_name_column], target_df[selected_target_name_column].astype(str))
                if fuzzy_result:
                    match_type = '名称模糊匹配'
                    match_score = fuzzy_result[1]  # 匹配分数作为阈值
                    matched_row = target_df[target_df[selected_target_name_column] == fuzzy_result[0]].iloc[0]

        # 将匹配结果或未匹配结果添加到 new_rows 列表
        new_rows.append({
            '待映射数据编码': row[selected_mapping_code_column],
            '待映射数据名称': row[selected_mapping_name_column],
            '目标表编码': matched_row[selected_target_code_column] if matched_row is not None else None,
            '目标表名称': matched_row[selected_target_name_column] if matched_row is not None else None,
            '匹配类型': match_type,
            '匹配阈值': match_score
        })

    # 使用列表一次性创建新的 DataFrame
    mapping_results = pd.DataFrame(new_rows)

    # 显示映射结果
    if mapping_results.empty:
        st.write("没有找到匹配的记录。")
    else:
        st.write("映射结果：")
        original_mapping_results = mapping_results.copy()  # 复制原始映射结果以供参考

        # 允许用户通过文本输入修改特定的列
        for index, row in original_mapping_results.iterrows():
            st.write(f"行 {index + 1}:")
            # 为“目标表编码”列创建文本输入框
            target_code_input = st.text_input("目标表编码:", value=row['目标表编码'], key=f"target_code_{index}")
            # 为“目标表名称”列创建文本输入框
            target_name_input = st.text_input("目标表名称:", value=row['目标表名称'], key=f"target_name_{index}")

        # 提交按钮，用于保存编辑后的映射结果
        submit_changes = st.button("提交更改")

        if submit_changes:
            # 更新映射结果 DataFrame
            for index, row in original_mapping_results.iterrows():
                # 检查是否有输入，如果有则更新
                if st.session_state.get(f"target_code_{index}", None):
                    mapping_results.at[index, '目标表编码'] = st.session_state[f"target_code_{index}"]
                if st.session_state.get(f"target_name_{index}", None):
                    mapping_results.at[index, '目标表名称'] = st.session_state[f"target_name_{index}"]

            # 显示更新后的映射结果
            st.write("更新后的映射结果：")
            st.dataframe(mapping_results)


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
        # 直接创建一个包含所有页面选项的字典
        pages = {
            "映射": mapping_page,
        }
        # 将查询页面选项添加到 pages 字典中
        pages.update(query_pages)  # 使用 update 方法合并字典
        pages.update({
            "上传管理": upload_management_page,
            "已上传数据信息": uploaded_data_info_page,
        })

        selected_page = st.radio("选择页面:", list(pages.keys()))

    # 根据用户选择显示相应页面
    if selected_page in pages:
        pages[selected_page]()  # 调用选中页面的函数
    else:
        st.write("页面未找到。")

if __name__ == "__main__":
    main()