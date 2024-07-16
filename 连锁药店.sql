--太原市:1401
--update: zhanggh 20240617 连锁机构新增药店数量,只有少数药店的非连锁排除,国飞只查连锁;

--1、总体情况
select
	min(setl_time) '起始时间',
	max(setl_time) '结束时间',
	cqunt(1) '总结算人次',
	count(DISTINCT psn_no) '总结算人数',
	sum(toFloat32(medfee_sumamt))/ 10000 '医疗总费用',
	sum(toFloat32(hifp_pay))/10000 '统筹基金费用',
	sum(toFloat32(fund_pay_sumamt))/ 10000 '基金总费用',
	sum(toFloat32(acct_pay))/10000 '个人账户费用',
	COUNT(DISTINCT fixmedins_code) '药店数量'
from
	DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi_yd
where
	refd_setl_flag='0' and vali_flag ='1' and dwh_soft_delete_flg ='0' and toYear(toDate(setl_time)) in (2022,2023)
and match(fix_blng_admdvs,'^1401')；


--两年的基本情况对比
with tb1 as
(select
	toYear(toDate(setl_time)) '年份',
	count(1) '总结算人次',
	count(DISTINCT psn_no) '总结算人数',
	sum(toFloat32(medfee_sumamt))/ 10000 '医疗总费用',
	sum(toFloat32(hifp_pay))/10000 '统筹基金费用',
	sum(toFloat32(fund_pay_sumamt))/ 10000 '基金总费用',
	sum(toFloat32(acct_pay))/ 10000 '个人账户费用'
	COUNT(DISTINCT fixmedins_code) '药店数量'
from
	DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi_yd
where
	refd_setl_flag='0' and vali_flag ='1' and dwh_soft_delete_flg ='0'and toYear(toDate(setl_time)) in (2022,2023)
	and match(fix_blng_admdvs,'^1401')
group by
	'年份')
SELECT * FROM tb1
ORDER BY '年份'；



--生成机构标准名称
DROP table if exists std_yaodian_taiyuan;
create table std_yaodian_taiyuan engine=MergeTree order by fixmedins code
SETTINGS allow_nullable_key=1
as
SELECT fixmedins_code,anyHeavy(fixmedins_name) fixmedins_nameSTD from DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi_yd
WHERE fixmedins_name IS NOT NULL AND fixmedins_code IS NOT NULL and match(fix_blng_admdvs, '^1401')
group by fixmedins_code；


--2.各机构费用情况
--按基金排名
WITH tbl AS
(select
	row_number()OVER (ORDERBY '统筹基金费用'desc) '序号',
	fixmedins_code,
	count(1) '总结算人次',
	count(DISTINCT psn_no) '总结算人数',
	sum(toFloat32(medfee_sumamt))/10000 '医疗总费用',
	sum(toFloat32(hifp_pay))/ 10000 '统筹基金费用',
	sum(toFloat32(fund_pay_sumamt))/10000 '基金总费用',
	sum(toFloat32(acct_pay))/ 10000 '个人账户费用',
	sum(toFloat32(cash_payamt))/10000 '个人现全费用',
from
	DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi_yd
where
	refd_setl_flag = '0' and vali_flag = '1' and dwh_soft_delete_flg = '0' and toYear(toDate(setl_time)) in (2022,2023)
	and match(fix_blng_admdvs,'^1401')
group by
    fixmedins_code
having '统筹基金费用'>0
order by
    '统筹基金费用'DESC
limit 50),
tb2 as
(SELEcT * FRoM tb1 JoIN std_yaodian_taiyuan USING fixmedins_code)
SELECT'序号',fixmedins_code '机构编码',
fixmedins_name_STD '机构名称',
'总结算人次','总结算人数','医疗总费用','统筹基金费用',
'个人账户费用'FROM tb2 ORDER BY '序号'；


--T0P10机构涉及的连锁机构总体情况
with tb1 as
(SELECT
multiIf(fixmedins_name 1ike '%湖南达意维康医药产业股份有限公司%', '湖南达意维康医药产业股份有限公司',
        fixmedins_name 1ike '%老百姓大药房连锁%', '老百姓大药房连锁',
        fixmedins_name 1ike '%湖南九芝堂零售连锁%', '湖南九芝堂零售连锁',
        fixmedins_name 1ike '%国药控股湖南维安大药房连锁%', '国药控股湖南维安大药房连锁',
        fixmedins_name 1ike '%湖南干金大药房连锁%', '湖南干金大药房连锁',
        fixmedins_name 1ike '%湖南华益润生大药房有限公司%', '湖南华益润生大药房有限公司',
        fixmedins_name 1ike '%益丰大药房连锁%', '益丰大药房连锁',
        fixmedins_name 1ike '%湖南雅翠药房连锁%', '湖南雅翠药房连锁',
        '其他'
)'连销机构'
count(DISTINCT fixmedins_code)'药店数量',
SUM(toF1oat32(medfee_sumamt))/10000 '总费用',
SUM('总费用') over () total1,'总费用'/total1 '总费用占比',
SUM(toF1oat32(hifp_pay))/10000 '统等基金支付',
SUM('统筹基金支付') over () total2,'统筹基金支付'/total2 '统帮基金占比'
SUM(toF1oat32(fundpay_sumamt))/10000-'统筹基金支付' '具他基全支付'
SUM(toFloat32(acct_pay))/10000 '个账支付总额',
SUM('个账支付总额') over total4,'个账支付总额'/total4 '个账支付占比'
FROM DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi_yd
where refd_setl_flag = '0' and vali_flag='1' and dwh_soft_delete_flg = '0' and toyear(toDate(setl_time)) in (2022,2023)
and match(fix_blng_admdvs,'1401')
group by '连锁机构')
select '连锁机构','药店数量','总费用','总费用占比','统筹基金支付','统筹基金占比','其他基金支付','个账支付总额','个账支付占比' from tb1
order by if('连锁机构'='其他',1,0),'统筹基金支付' desc；


--锁定一下连锁
DROP TABLE if exists T0P50 yaodian_taiyuan;
create table Top50 yaodian_taiyuan engine-MergeTree order by fixmedins_code
SETTINGS allow_nullable_key=1
as
WITH tb1 AS
(SELECT
    row_number() OVER (ORDER BY'统筹基金费用') desc) '序号',
    fixmedins_code,
    COUNT(1)'总结算人次',
    COUNT(DISTINCT psn_no) '总结算人数',
    sum(toF1oat32(medfee_sumamt))/10000 '医疗总费用',
    sum(toFloat32(hifppay))/10000 '统筹基金费用',
    sum(toF1oat32(fundpaysumamt))/10000 '基金总费用',
    sum(toF1oat32(acctpay))/10000 '个人账户费用',
    sum(toFloat32(cash_payamt))/10000 '个人现金费用'
FROM
    DB_OUTDRUG_ODs.setl_d_tklife_dist_shanxiyd
where
    refd_setl_flag='0'and vali_flag='1' and dwh_soft_delete_flg ='0' and toyear(toDate(setl_time)) in (2022,2023)
    and match(fix_blng_admdvs,'^14o1')
    and match(fixmedins_name,
    '湖南达意维康医药产业股份有限公司|老百姓大药房连锁|湖南九芝堂零售连锁|国药控股湖南维安大药房连锁|湖南干金大药房连锁|湖南华益润生大药房有限公司|益丰大药房连锁|湖南雅翠药房连锁'
group by
    fixmedins_code
having '统筹基金费用'>0
order by
    '统筹基金费用' DESC
1imit 50)
SELECT * FROM tb1 JOIN std_yaodian_taiyuan USING fixmedins_code；


SELECT'序号',fixmedins_code'机构编妈',
fixmedins_name_STD '机构名称',
'总结算人次','总结算人数','医疗总费用','统筹基金费用',
'个人账户费用'FROM TOP50_yaodian_taiyuan ORDER BY '序号'；


--按统筹基金环比分析
with tb1 as
(select
    fixmedins_code,
    countIf(1,toYear(toDate(set1_time))=2022) '总结算人次_2022'
    countIf(1,toYear(toDate(setl_time))=2023) '总结算人次_2023'
    '总结算人次_2023'/'总结算人次_2022'-1 '人次增幅'
    sumIf(toFloat32(medfee_sumamt),toYear(toDate(set1_time))=2022)/10000 '总费用_2022'
    sumIf(toFloat32(medfee_sumamt),toYear(toDate(set1_time))=2023)/10000 '总费用_2023'
    '总费用_2023'/'总费用_2022'-1 '总费用增幅'
    sumIf(toFloat32(hifp_pay),toYear(toDate(set1_time))=2022)/10000 '统筹费用_2022'
    sumIf(toFloat32(hifp_pay),toYear(toDate(set1_time))=2023)/10000 '统筹费用_2023'
    '统筹费用_2023'/'统筹费用_2022'-1 '统筹基金增幅'
    '总费用_2022'*10000/'总结算人次_2022' '次均总费_2022'
    '总费用_2023'*10000/'总结算人次_2022' '次均总费_2023'
    '次均总费_2023'/'次均总费_2022'-1 '次均增幅'
    COUNT(DISTINCT setl_id)/COUNT(DISTINCT psn_no) '人次人头比'
from
    DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi yd
where
    refd_setl_flag='0'and vali_flag='1' and dwh_soft_delete_flg ='0' and  toyear(toDate(setl_time)) in (2022,2023)
    and match(fix_blng_admdvs,'^1401')
group by
    fixmedins_code),
tb2 AS
(SELECT'序号',fixmedins_code,fixmedins_name_STD FROM TOP50_yaodian_taiyuan WHERE '序号'<=10)
SELECT tb2.'序号' '序号',--fixmedins_code '机构编码'
fixmedins_name_STD '机构名称','总结算人次_2022',
'总结算人次_2023','人次增幅',
'总费用_2022','总费用_2023','总费用增幅','统筹费用_2022','统筹费用_2023','统筹基金增幅','次均总费_2022','次均总费_2023','次均增幅','人次人头比'
FROM tb1 JOIN tb2 USING fixmedins_code
ORDER BY tb2.'序号'
limit 10；

--STEP1:药品单价标准差分析
WITH
tb0 as
(SELECT fixmedins_code FROM TOP50_yaodian_taiyuan WHERE '序号'<=50),
tb1 AS
(select fixmedins_code,hilist_name'医保目录名称',
stddevPopStable(toFloat32(pric))'单价标雀差',
COUNT(DISTINCT PriC)'单价数量',
max(round(toFloat32(pric),2))'最高单价',
min(round(toFloat32(pric),2))'最低单价'
FROM DB_OUTDRUG_ODS.fee_1ist_d_dist_shanxi_yd
where toYear(toDate(fee_ocur_time)) in (2022,2023)
    AND fixmedins_code GLOBAL IN(SELECT fixmedins_code FROM tb0)
--  AND hilist_name IN(SELECT'医保目录名称' FROM TOP50_hilist_shanxi_yd)
and hilist_name !='无'AND vali_flag='1'and dwh_soft_delete_flg='0'
and not match(hilist_name,'自费|商保')
group by fixmedins_code,'医保目录名称'),
tb2 AS
(SELECT* FROM T0P50_yaodian_taiyuan),
tb3 AS
(SELECT tb1.*,B.'序号' '机构序号',B.fixmedins_name_STD FROM tb1 JOIN tb2 USING fixmedins_code),
tb4 as
    (
SELECT '机构序号',
--tb2.'序号' '药品序号',
    fixmedins_code '机构编码', fixmedins_name_STD '机构名称', '医保目录名称', '单价标准差', '单价数量', '最高单价', '最低单价'
FROM tb3
--JOIN tb2 USING '医保目录名称'
WHERE ('单价标准差'>200 AND '单价数量'>=10) 0R('单价数量' >19 and '最高单价'>100)
),
tb5 as
(select '机构序号',count()num from tb4 group by '机构序号' having num>30)
select * from tb4 where'机构序号'in(select'机构序号'from tb5)
ORDER BY '机构序号',
'单价标准差' DESC；

--STEP2:季度异常分析,基金排名前10的机构
WITH
tb0 AS
(SELECT fixmedins_code FROM T0P50_yaodian_taiyuan WHERE'序号'<=10),
tb1 AS
(select
    fixmedins_code,toyear(toDate(setl_time))'年份',
    sumIf(ifNul1(toFloat32(hifp_pay),0),toQuarter(toDate(set]_time))=1)/10000 '统筹基金费用Q1'
    sumIf(ifNul1(toFloat32(hifp_pay),0),toQuarter(toDate(set]_time))=2)/10000 '统筹基金费用Q2'
    sumIf(ifNul1(toFloat32(hifp_pay),0),toQuarter(toDate(set]_time))=3)/10000 '统筹基金费用Q3'
    sumIf(ifNul1(toFloat32(hifp_pay),0),toQuarter(toDate(set]_time))=4)/10000 '统筹基金费用Q4'
    greatest('统筹基金费用Q1','统筹基金费用Q2','统筹基金费用Q3','统筹基金费用Q4')/('统筹基金费用Q1'+'统筹基金费用Q2'+'统筹基金费用Q3'+'统筹基金费用Q4') '统筹基金最高季度占比'
from
    DB_OUTDRUG_ODs.setl_d_tklife_dist_shanxi yd
where
    refd_setl_flag='0'and vali_flag='1'and dwh_soft_delete_flg='0' and toyear(toDate(setl_time)) in (2022,2023)
AND fixmedins_code GLOBAL IN(SELECT fixmedins_code FRoM tb0)
and match(fix _blng_admdvs,'^1401')
group by
    fixmedins_code,'年份'),
tb2 AS
(SELECT'序号',fixmedins_code,fixmedins_name_STD FRoM T0P50_yaodian_taiyuan WHERE '序号'<=10)
SELECT'tb2.序号' '序号',fixmedins_code'机构代码',
fixmedins_name_STD'机构名称',
'年份','统筹基金费用Q1','统筹基金费用02','统筹基金费用Q3','统筹基金费用04','统筹基金最高季度占比'
FROM tb1 JOIN tb2 USING fixmedins_code
ORDER BY'年份',tb2.'序号'；

--STEP3:T0P10月度异常分析
with
tb0 as
(SELECT fixmedins_code FROM T0P50_yaodian_taiyuan WHERE '序号'<=50),
tb1 as
(select
    fixmedins_code,
    toYYYYMM(toDate(setl_time))'月份',
    sum(toF1oat32(medfee_sumamt))/ 10000 '医疗总费用',
    sum(toFloat32(hifp_pay))/10000 '统著基金费用',
    sum(toFloat32(acct_pay))/10000 '个人账户费用'
from
    DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi_yd
where
    refd_setl_flag='0'and vali_flag='1'and dwh_soft_delete_flg='0' and toyear(toDate(setl_time)) in (2022,2023)
    AND fixmedins_code GLOBAL IN(SELECT fixmedins_code FRoM tb0)
    and match(fix _blng_admdvs,'^1401')
group by
    fixmedins_code,'月份'),
tb2 AS
(SELECT'序号',fixmedins_code,fixnedins_name_STD FROM TOP50_yaodian_taiyuan WHERE '序号'<=10)
SELECT tb2.序号'序号',fixmedins_code'机构代码',
fixnedins_name_STD '机构名称',
'月份','医疗总费用','统筹基金费用','个人账户费用'
FROM tb1 JOIN tb2 USING fixmedins_code
ORDER BY'序号','月份'；

--职工现金支付问题
WITH
tb0 as
(SELECT fixmedins_code FROM TOP50_yaodian_taiyuan WHERE '序号'<=50),
tb1 as
(select
    fixmedins_code,
    sum(toFloat32(medfee_sumamt))/10000 '职工医疗总费用',
	sum(toFloat32(hifp_pay))/ 10000 '职工统筹基金费用',
	sum(toFloat32(acct_pay))/ 10000 '职工个人账户费用',
    sum(toFloat32(acctmulaidpay))/10000 '职工共济账户费用',
	sum(toFloat32(cash_payamt))/10000 '职工个人现金费用',
    '职工个人现金费用'/'职工医疗总费用' '职工个人规金占比'
from
    DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi_yd
where
    refd_setl_flag='0'and vali_flag='1'and dwh_soft_delete_flg='0' and toyear(toDate(setl_time)) in (2022,2023)
    AND fixmedins_code GLOBAL IN(SELECT fixmedins_code FROM tb0)
    and insutype='310'
--  and toyYear(toDate(setl_time))=2023 --菏泽2022无个账，特殊条件
    and match(fix_blng_admdvs,'^1401')
group by
    fixmedins_code),
tb2 AS
(SELECT'序号',fixmedins_code,fixnedins_name_STD FROM TOP50_yaodian_taiyuan WHERE '序号'<=10)
SELECT tb2.序号'序号',fixmedins_code'机构代码',
fixnedins_name_STD '机构名称',
'职工医疗总费用','职工统筹基金费用','职工个人账户费用','职工共济账户费用','职工个人现金费用'.'职工个人规金占比'
FROM tb1 JOIN tb2 USING fixmedins_code
ORDER BY'职工个人规金占比' desc；

--药品中草药占比问题
WITH
tb0 as
(SELECT fixmedins_code FROM TOP50_yaodian_taiyuan WHERE '序号'<=50),
tb1 as
(select fixmedins_code,
    sum(toFloat32(det_item_fee_sumamt))/10000 '医疗总勇用',
    sumIf(toFloat32(det_item_fee_sumamt),list_type 1ike '%101%')/10000/'医疗总费用' '西药中成药占比',
    sumIf(toFloat32(det_item_fee_sumamt),match(list_type,'102|106'))/10000/'医疗总费用' '中药饮片及颗粒占比',
    sumIf(toFloat32(det_item_fee_sumamt),list_type 1ike '%103%')/10000/'医疗总费用' '自制剂占比',
    sumIf(toFloat32(det_item_fee_sumamt),list_type 1ike '%104%')/10000/'医疗总费用' '民族药占比',
    sumIf(toFloat32(det_item_fee_sumamt),list_type 1ike '%201%')/10000/'医疗总费用' '医疗服务占比',
    sumIf(toFloat32(det_item_fee_sumamt),list_type 1ike '%301%')/10000/'医疗总费用' '医用耗材占比',
1-'西药中成药占比'-'中药饮片及颗粒占比'-'自制剂占比'-'民族药占比'-'医疗服务占比'-'医用耗材占比' '其他占比'
from DB_OUTDRUG_ODS.setl_d_tklife_dist_shanxi_yd
where toyear(toDate(fee_ocur_time)) in (2022,2023)
    AND fixmedins_code GLOBAL IN(SELECT fixmedins_code FROM tb0)
--  AND hilist name IN(SELECT'医保目录名称' FROM TOP50_hilist_shanxi_yd)
and hilist_name !='无' AND vali_flag='1' and dwh_soft_deletc_flg='0'
group by fixmedins_code),
tb2 AS
SELECT * FROM TOP50_yaodian_taiyuan),
tb3 AS
(SELECT tb1.*,B.'序号' '机构序号',B.fixmedins_name_STD FROM tb1 JOIN tb2 USING fixmedins_code)
SELECT '机构序号',
--tb2.'序号' '药品序号'，
fixmedins_code'机构编码',fixnedins_name_STD '机构名称',
'医疗总费用','西药中成药占比','中药饮片及颗粒占比','自制剂占比','民族药占比','医疗服务占比','医用耗材占比','其他占比'
FROM tb3
ORDER BY '中药饮片及颗粒占比'desc;




























