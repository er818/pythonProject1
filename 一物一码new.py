import streamlit as st
import pandas as pd

def upload_data():
    st.title("上传数据表格")
    uploaded_file = st.file_uploader("选择文件", type=["xlsx", "csv"])
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        st.write(data)
        return data
    return None

def query_data(df):
    st.title("查询数据")
    query = st.text_input("输入查询条件")
    if query:
        filtered_data = df[df.apply(lambda row: query in str(row).lower(), axis=1)]
        st.write("查询结果：")
        st.write(filtered_data)

def main():
    st.set_page_config(page_title="数据查询应用", layout="wide")
    df = upload_data()
    if df is not None:
        query_data(df)

if __name__ == "__main__":
    main()