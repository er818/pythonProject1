import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------
# 1. 基础配置与缓存设置
# --------------------------
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(
    page_title="费用预估demo",
    page_icon=":bar_chart:",
    layout="wide"
)


@st.cache_data
def load_data(file, is_csv):
    if is_csv:
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)


@st.cache_data
def merge_data(case_df, expense_df, case_key, expense_key, birth_date_field, admission_date_field):
    merged_df = pd.merge(
        case_df,
        expense_df,
        left_on=case_key,
        right_on=expense_key,
        how='inner',  # 内连接确保仅保留能关联的记录
        suffixes=('_case', '_expense')
    )

    merged_df[birth_date_field] = pd.to_datetime(merged_df[birth_date_field], errors='coerce')
    merged_df[admission_date_field] = pd.to_datetime(merged_df[admission_date_field], errors='coerce')

    merged_df['年龄_case'] = (merged_df[admission_date_field] - merged_df[birth_date_field]).dt.days / 365.25
    merged_df['年龄_case'] = merged_df['年龄_case'].fillna(0)
    merged_df['年龄_case'] = merged_df['年龄_case'].apply(lambda x: max(0, int(x)) if not np.isnan(x) else 0)

    return merged_df


# 处理项目统计的函数（索引从1开始）- 增加了数值格式化
def calculate_item_stats(df, case_key, item_name_field, item_quantity_field, item_amount_field):
    # 1. 按就诊流水号和项目名称分组，计算每个流水号下每个项目的总数量和总金额
    item_case_group = df.groupby([case_key, item_name_field]).agg({
        item_quantity_field: 'sum',  # 同一流水号下项目总数量
        item_amount_field: 'sum'  # 同一流水号下项目总金额
    }).reset_index()

    # 2. 过滤掉项目总数量<=0的记录
    item_case_filtered = item_case_group[item_case_group[item_quantity_field] > 0]

    # 3. 按项目名称分组，计算统计量
    item_stats = item_case_filtered.groupby(item_name_field).agg({
        case_key: 'nunique',  # 例数：符合条件的流水号数量
        item_quantity_field: 'sum',  # 项目合计数：总数量
        item_amount_field: 'sum'  # 项目总金额
    }).reset_index()

    # 4. 计算例均金额：总金额 / 例数（避免除0错误）
    item_stats['例均金额'] = item_stats.apply(
        lambda row: row[item_amount_field] / row[case_key] if row[case_key] > 0 else 0,
        axis=1
    )

    # 5. 格式化数值：项目合计数取整数，总金额和例均金额取一位小数
    item_stats = item_stats.rename(columns={
        case_key: '例数',
        item_quantity_field: '项目合计数',
        item_amount_field: '项目总金额',
        item_name_field: '项目名称'
    })

    # 关键修改：数值格式化
    item_stats['项目合计数'] = item_stats['项目合计数'].round().astype(int)  # 取整数
    item_stats['项目总金额'] = item_stats['项目总金额'].round(1)  # 保留一位小数
    item_stats['例均金额'] = item_stats['例均金额'].round(1)  # 保留一位小数

    # 6. 按例均金额排序，取top50
    item_stats = item_stats.sort_values('例均金额', ascending=False).head(50)

    # 7. 重置索引，从1开始计数
    item_stats = item_stats.reset_index(drop=True)
    item_stats.index = item_stats.index + 1  # 索引从1开始

    return item_stats


# --------------------------
# 2. 初始化会话状态
# --------------------------
if 'merged_df' not in st.session_state:
    st.session_state.merged_df = None
if 'case_df' not in st.session_state:
    st.session_state.case_df = None
if 'expense_df' not in st.session_state:
    st.session_state.expense_df = None
if 'insurance_config' not in st.session_state:
    st.session_state.insurance_config = {}
if 'case_key' not in st.session_state:
    st.session_state.case_key = None
if 'surgery_fields' not in st.session_state:
    st.session_state.surgery_fields = []

# --------------------------
# 3. 侧边栏 - 数据上传和配置
# --------------------------
with st.sidebar:
    st.header("数据上传")

    case_file = st.file_uploader("上传病案信息表", type=["csv", "xlsx"], key="case_file")
    if case_file:
        try:
            is_csv = case_file.name.endswith('.csv')
            st.session_state.case_df = load_data(case_file, is_csv)
            st.success(f"已加载病案表（{len(st.session_state.case_df)} 条记录）")
        except Exception as e:
            st.error(f"加载失败: {e}")

    expense_file = st.file_uploader("上传费用明细表", type=["csv", "xlsx"], key="expense_file")
    if expense_file:
        try:
            is_csv = expense_file.name.endswith('.csv')
            st.session_state.expense_df = load_data(expense_file, is_csv)
            st.success(f"已加载费用表（{len(st.session_state.expense_df)} 条记录）")
        except Exception as e:
            st.error(f"加载失败: {e}")

    if st.session_state.case_df is not None and st.session_state.expense_df is not None:
        st.header("数据关联配置")
        case_columns = st.session_state.case_df.columns.tolist()
        expense_columns = st.session_state.expense_df.columns.tolist()

        case_key = st.selectbox("病案表关联主键（就诊流水号）", case_columns)
        expense_key = st.selectbox("费用表关联主键", expense_columns)
        st.session_state.case_key = case_key

        st.subheader("日期字段")
        birth_date_field = st.selectbox("出生日期", case_columns)
        admission_date_field = st.selectbox("入院日期", case_columns)

        st.subheader("分析字段")
        primary_diagnosis_field = st.selectbox("主要诊断字段", case_columns)
        total_cost_field = st.selectbox("总费用字段", case_columns)
        payment_type_field = st.selectbox("支付类型字段", case_columns)

        st.subheader("费用明细表字段")
        item_name_field = st.selectbox("项目名称", expense_columns)
        item_quantity_field = st.selectbox("项目数量", expense_columns)
        item_amount_field = st.selectbox("项目金额", expense_columns)

        # 自动识别手术字段
        st.subheader("手术字段识别")
        surgery_fields = [col for col in case_columns if "手术名称" in col]

        if surgery_fields:
            st.info(f"已自动识别 {len(surgery_fields)} 个手术字段: {', '.join(surgery_fields)}")
            st.session_state.surgery_fields = surgery_fields
        else:
            st.warning("未找到包含'手术'的字段，请手动选择")
            surgery_field = st.selectbox("选择手术字段", case_columns)
            st.session_state.surgery_fields = [surgery_field]

        if st.button("执行数据关联"):
            try:
                st.session_state.merged_df = merge_data(
                    st.session_state.case_df,
                    st.session_state.expense_df,
                    case_key,
                    expense_key,
                    birth_date_field,
                    admission_date_field
                )

                st.session_state.fields = {
                    'primary_diagnosis': primary_diagnosis_field,
                    'total_cost': total_cost_field,
                    'payment_type': payment_type_field,
                    'item_name': item_name_field,
                    'item_quantity': item_quantity_field,
                    'item_amount': item_amount_field,
                    'birth_date': birth_date_field,
                    'admission_date': admission_date_field
                }

                st.success(f"数据关联成功（{len(st.session_state.merged_df)} 条记录）")
            except Exception as e:
                st.error(f"关联失败: {e}")

        if st.session_state.merged_df is not None:
            st.header("支付类型分类")
            payment_types = st.session_state.merged_df[payment_type_field].dropna().unique().tolist()
            if payment_types:
                insurance_types = st.multiselect("医保类型", payment_types)
                commercial_types = st.multiselect("商保类型", [t for t in payment_types if t not in insurance_types])

                if st.button("保存配置"):
                    st.session_state.insurance_config = {
                        'insurance': insurance_types,
                        'commercial': commercial_types
                    }
                    st.success("配置已保存")

# --------------------------
# 4. 主页面 - 统计分析
# --------------------------
if st.session_state.merged_df is not None and st.session_state.insurance_config:
    st.header("费用预估demo")
    fields = st.session_state.fields
    case_key = st.session_state.case_key
    merged_df = st.session_state.merged_df

    # 查询条件
    st.subheader("查询条件")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("性别", ["全部", "男", "女"])
        age_range = st.slider("年龄范围", 0, 120, (0, 120))
        primary_diagnosis = st.text_input("主要诊断", value="")
        surgeries_input = st.text_input("手术关键词（多个用空格分隔，使用AND关系）", value="")
        has_surgery = st.selectbox("是否有手术", ["全部", "是", "否"], index=0)
    with col2:
        other_diagnosis = st.text_input("其他诊断（多个关键词用空格分隔）", value="")

    if st.button("执行查询"):
        # 筛选逻辑
        query_df = merged_df[
            (merged_df['年龄_case'] >= age_range[0]) &
            (merged_df['年龄_case'] <= age_range[1])
            ]

        if primary_diagnosis:
            query_df = query_df[
                query_df[fields['primary_diagnosis']].astype(str).str.contains(primary_diagnosis, na=False, case=False)
            ]

        # 修改手术关键词匹配逻辑为AND关系
        if surgeries_input:
            surgery_keywords = [kw.strip() for kw in surgeries_input.split() if kw.strip()]
            if surgery_keywords:
                # 初始化所有记录都满足条件
                surgery_conditions = pd.Series(True, index=query_df.index)

                # 对每个关键词，检查是否所有手术字段都不包含它
                for kw in surgery_keywords:
                    keyword_condition = pd.Series(False, index=query_df.index)
                    for field in st.session_state.surgery_fields:
                        if field in query_df.columns:
                            field_data = query_df[field].astype(str).str.strip()
                            # 只要有一个手术字段包含关键词，就算匹配
                            keyword_condition = keyword_condition | (
                                        (field_data != "") & (field_data != "nan") & field_data.str.contains(kw,
                                                                                                             na=False,
                                                                                                             case=False))

                    # 更新总条件：必须所有关键词都至少在一个手术字段中出现
                    surgery_conditions = surgery_conditions & keyword_condition

                query_df = query_df[surgery_conditions]

        if has_surgery != "全部" and st.session_state.surgery_fields:
            has_surgery_condition = pd.Series(False, index=query_df.index)
            for field in st.session_state.surgery_fields:
                if field in query_df.columns:
                    field_data = query_df[field].astype(str).str.strip()
                    has_surgery_condition = has_surgery_condition | (field_data != "") & (field_data != "nan")
            if has_surgery == "是":
                query_df = query_df[has_surgery_condition]
            else:
                query_df = query_df[~has_surgery_condition]

        if gender != "全部":
            gender_field = "性别描述"
            if gender_field in query_df.columns:
                query_df = query_df[query_df[gender_field] == gender]
            else:
                st.warning("未找到性别字段，性别筛选无效")

        if other_diagnosis:
            other_diagnosis_fields = [col for col in query_df.columns if "其他诊断名称" in col]
            if not other_diagnosis_fields:
                st.warning("未找到包含'其他诊断名称'的字段，其他诊断筛选无效")
            else:
                st.info(f"已识别 {len(other_diagnosis_fields)} 个其他诊断字段，将进行模糊匹配")
                other_diagnosis_keywords = [kw.strip() for kw in other_diagnosis.split() if kw.strip()]
                if other_diagnosis_keywords:
                    other_diag_conditions = pd.Series(False, index=query_df.index)
                    for field in other_diagnosis_fields:
                        if field in query_df.columns:
                            field_data = query_df[field].astype(str).str.strip()
                            for kw in other_diagnosis_keywords:
                                kw_match = (field_data != "") & (field_data != "nan") & field_data.str.contains(kw,
                                                                                                                na=False,
                                                                                                                case=False)
                                other_diag_conditions = other_diag_conditions | kw_match
                    query_df = query_df[other_diag_conditions]

        # 结果统计
        unique_cases = query_df[case_key].nunique()
        st.success(f"找到 {unique_cases} 例患者（去重后）")

        if unique_cases == 0:
            st.warning("没有找到符合条件的数据")
        else:
            patient_data = query_df.groupby(case_key).agg({
                fields['total_cost']: 'first',
                fields['payment_type']: 'first'
            }).reset_index()

            insurance_types = st.session_state.insurance_config['insurance']
            commercial_types = st.session_state.insurance_config['commercial']

            insurance_patient_ids = patient_data[patient_data[fields['payment_type']].isin(insurance_types)][
                case_key].tolist()
            commercial_patient_ids = patient_data[patient_data[fields['payment_type']].isin(commercial_types)][
                case_key].tolist()

            insurance_case_count = len(insurance_patient_ids)
            commercial_case_count = len(commercial_patient_ids)

            total_avg = patient_data[fields['total_cost']].sum() / unique_cases if unique_cases > 0 else 0
            insurance_avg = patient_data[patient_data[fields['payment_type']].isin(insurance_types)][
                                fields['total_cost']].sum() / insurance_case_count if insurance_case_count > 0 else 0
            commercial_avg = patient_data[patient_data[fields['payment_type']].isin(commercial_types)][
                                 fields['total_cost']].sum() / commercial_case_count if commercial_case_count > 0 else 0

            st.subheader("例均费用统计")
            col1, col2, col3 = st.columns(3)
            col1.metric("全部", f"{total_avg:.1f} 元", f"{unique_cases} 例")  # 确保主页面统计显示1位小数
            col2.metric("医保", f"{insurance_avg:.1f} 元", f"{insurance_case_count} 例")
            col3.metric("商保", f"{commercial_avg:.1f} 元", f"{commercial_case_count} 例")

            # 费用明细排行
            st.subheader("费用明细排行（按项目例均金额 Top50）")

            all_stats = calculate_item_stats(
                df=query_df,
                case_key=case_key,
                item_name_field=fields['item_name'],
                item_quantity_field=fields['item_quantity'],
                item_amount_field=fields['item_amount']
            )

            insurance_stats = None
            if insurance_case_count > 0:
                insurance_df = query_df[query_df[case_key].isin(insurance_patient_ids)]
                insurance_stats = calculate_item_stats(
                    df=insurance_df,
                    case_key=case_key,
                    item_name_field=fields['item_name'],
                    item_quantity_field=fields['item_quantity'],
                    item_amount_field=fields['item_amount']
                )

            commercial_stats = None
            if commercial_case_count > 0:
                commercial_df = query_df[query_df[case_key].isin(commercial_patient_ids)]
                commercial_stats = calculate_item_stats(
                    df=commercial_df,
                    case_key=case_key,
                    item_name_field=fields['item_name'],
                    item_quantity_field=fields['item_quantity'],
                    item_amount_field=fields['item_amount']
                )

            # 显示数据
            col_all, col_insurance, col_commercial = st.columns(3)
            with col_all:
                st.subheader("全部")
                # 强制格式化金额列，确保显示1位小数
                styled_all = all_stats.style.format({
                    '项目总金额': '{:.1f}',
                    '例均金额': '{:.1f}'
                }).set_table_attributes('style="width: 100%;"')
                st.dataframe(styled_all)
                if len(all_stats) > 0:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    sns.barplot(x='例均金额', y='项目名称', data=all_stats.head(5).reset_index())
                    ax.set_yticklabels([f"{i + 1}. {name}" for i, name in enumerate(all_stats.head(5)['项目名称'])])
                    st.pyplot(fig)

            with col_insurance:
                st.subheader("医保")
                if insurance_stats is not None and len(insurance_stats) > 0:
                    # 强制格式化金额列，确保显示1位小数
                    styled_insurance = insurance_stats.style.format({
                        '项目总金额': '{:.1f}',
                        '例均金额': '{:.1f}'
                    }).set_table_attributes('style="width: 100%;"')
                    st.dataframe(styled_insurance)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    sns.barplot(x='例均金额', y='项目名称', data=insurance_stats.head(5).reset_index())
                    ax.set_yticklabels(
                        [f"{i + 1}. {name}" for i, name in enumerate(insurance_stats.head(5)['项目名称'])])
                    st.pyplot(fig)
                else:
                    st.info("没有找到医保相关费用数据")

            with col_commercial:
                st.subheader("商保")
                if commercial_stats is not None and len(commercial_stats) > 0:
                    # 强制格式化金额列，确保显示1位小数
                    styled_commercial = commercial_stats.style.format({
                        '项目总金额': '{:.1f}',
                        '例均金额': '{:.1f}'
                    }).set_table_attributes('style="width: 100%;"')
                    st.dataframe(styled_commercial)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    sns.barplot(x='例均金额', y='项目名称', data=commercial_stats.head(5).reset_index())
                    ax.set_yticklabels(
                        [f"{i + 1}. {name}" for i, name in enumerate(commercial_stats.head(5)['项目名称'])])
                    st.pyplot(fig)
                else:
                    st.info("没有找到商保相关费用数据")

else:
    st.info("请先上传数据并完成配置")