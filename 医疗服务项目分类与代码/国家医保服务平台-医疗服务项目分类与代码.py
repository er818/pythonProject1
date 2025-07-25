from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# 设置Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 打开目标网页
driver.get('https://fuwu.nhsa.gov.cn/nationalHallSt/#/search/medical-service')

# 等待页面加载
time.sleep(10)  # 增加等待时间，确保页面完全加载

# 提取数据
data = []
rows = driver.find_elements(By.CSS_SELECTOR, 'tr.el-table__row:not(.expanded)')  # 选择未展开的行
for row in rows:
    expand_icon = row.find_element(By.CSS_SELECTOR, 'div.el-table__expand-icon i.el-icon-arrow-right')
    expand_icon.click()  # 点击展开图标
    time.sleep(2)  # 等待内容展开

    # 使用显式等待确保元素可见
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.el-form-item_content span'))
        )
        service_name_element = row.find_element(By.CSS_SELECTOR, '.el-form-item_content span')
        service_name = service_name_element.text
        medical_code_element = row.find_element(By.CSS_SELECTOR, '.el-form-item_content span:nth-of-type(2)')
        medical_code = medical_code_element.text
        data.append({'服务项目名称': service_name, '医疗目录编码': medical_code})
        print("提取数据成功:", service_name, medical_code)
    except Exception as e:
        print("提取数据失败:", e)
        continue

# 关闭浏览器
driver.quit()

# 检查是否提取到数据
if data:
    # 使用pandas创建DataFrame
    df = pd.DataFrame(data)
    # 将DataFrame保存到Excel文件
    df.to_excel('D:\\测试.xlsx', index=False)
    print('Data has been written to 测试.xlsx')
else:
    print("没有提取到数据，检查选择器和页面结构")