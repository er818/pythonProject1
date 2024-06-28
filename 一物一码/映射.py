import streamlit as st
import pandas as pd
from fuzzywuzzy import process

# 函数：上传Excel文件并返回DataFrame
def upload_excel(label):
    file = st.file_uploader(label, type=["xls", "xlsx"])
    if file:
        df = pd.read_excel(file)
        st.write(df.head())  # 显示数据预览
        return df
    return None

# 函数：模糊匹配编码和名称
def fuzzy_match(standard_df, mapping_df, match_threshold=80):
    mapped_df = mapping_df.copy()
    for index, row in mapping_df.iterrows():
        encoding = row['编码']
        name = str(row['名称'])  # 确保名称是字符串类型
        standard_names = standard_df['名称'].dropna().astype(str).tolist()  # 获取标准表中的名称列表

        # 使用模糊匹配找出最佳匹配项
        best_match = process.extractOne(name, standard_names)
        if best_match[1] >= match_threshold:
            # 根据匹配的名称找到标准表中的编码
            matched_encoding = standard_df[standard_df['名称'] == best_match[0]]['编码'].values[0]
            mapped_df.at[index, '映射编码'] = matched_encoding
            mapped_df.at[index, '映射名称'] = best_match[0]
        else:
            mapped_df.at[index, '映射编码'] = '未找到匹配'
            mapped_df.at[index, '映射名称'] = '未找到匹配'
    return mapped_df

def main():
    st.title("Excel数据映射工具")

    # 上传待映射数据表
    mapping_df = upload_excel("上传待映射数据表")

    # 上传标准表
    standard_df = upload_excel("上传标准表")

    if mapping_df is not None and standard_df is not None:
        # 执行模糊匹配
        result_df = fuzzy_match(standard_df, mapping_df)

        # 展示映射结果
        st.write("映射结果:")
        st.write(result_df)

if __name__ == "__main__":
    main()