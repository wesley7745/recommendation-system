import win32com.client as win32
import pandas as pd
from PIL import Image
import base64
from io import BytesIO

# =============================================================================
# 基本設定
# =============================================================================
outlook = win32.Dispatch('outlook.application')

# =============================================================================
# 帳戶設定
# =============================================================================
account = outlook.Session.Accounts.Item(1)

# =============================================================================
# 讀取Excel文件
# =============================================================================
file_pro = pd.read_excel("C:/Users/WCHuang8/Desktop/學習推薦系統專案/word2vec/output/top_matches_THR_pro2_translated.xlsx")
file_AI = pd.read_excel("C:/Users/WCHuang8/Desktop/學習推薦系統專案/word2vec/output/top_matches_THR_aiaiggthis_translated.xlsx")

# 部門列表和收件人對應
departments_receivers = {
    'Recruitment Department': ['wchuang8@winbond.com'],
    'Training and Development Department': ['wchuang8@winbond.com'],
    'Payroll Department': ['wchuang8@winbond.com'],
    'Employee Relations Department': ['wchuang8@winbond.com']
}

# 部門與主管名稱對應
department_managers = {
    'Recruitment Department': 'AD10主管',
    'Training and Development Department': 'AD20主管',
    'Payroll Department': 'AD30主管',
    'Employee Relations Department': 'AD40主管'
}

# 圖像路徑字典
images = {
    'Recruitment Department': "C:/Users/WCHuang8/Desktop/picture/recruit2.png",
    'Training and Development Department': "C:/Users/WCHuang8/Desktop/picture/training.png",
    'Payroll Department': "C:/Users/WCHuang8/Desktop/picture/payroll.png",
    'Employee Relations Department': "C:/Users/WCHuang8/Desktop/picture/relation.png"
}

# 共用的 CSS 風格，設置字體為微軟正黑體
css = "<style>body, table, p {font-family: '微軟正黑體';} table {border-collapse: collapse;} td, th {border: 1px solid black; padding: 8px;} h3 {font-family: '微軟正黑體';}</style>"

# =============================================================================
# 針對每個部門發送郵件
# =============================================================================
for department, receivers in departments_receivers.items():
    
    # 選取該部門的專業課程和AI課程
    dept_file_pro = file_pro[file_pro['Department Description'] == department]
    dept_file_ai = file_AI[file_AI['Department Description'] == department]

    # 如果該部門的課程選項中 `choose` 不為 1，則跳過發送
    if not any(dept_file_pro['choose'] == 1) and not any(dept_file_ai['choose'] == 1):
        continue
    
    # 创建新的邮件对象
    mail = outlook.CreateItem(0)
    mail._oleobj_.Invoke(*(64209, 0, 8, 0, account))
    
    # 初始化郵件收件人和主旨
    mail.To = ";".join(receivers)
    mail.Subject = '學習資源推薦'
    
    # 設置每個部門特定的主管名稱
    manager_name = department_managers.get(department, "主管")
    header = f'<p class="MsoNormal"><span style="font-family:&quot;微軟正黑體&quot;,sans-serif"><h3>Dear {manager_name}：</h3><p>向您推薦一些優質的學習資源，這些資源可以幫助您和您的團隊在專業方面進一步提升。以下是外部學習資源系統判斷出非常有價值的課程和工具：</p></span></p>'
    full_body_start = css + header

    # 開始拼接郵件內容
    full_body = full_body_start

    # 添加圖片（如果有需要）
    if department in images:
        image_path = images[department]
        
        # 裁剪图片为1200x300大小，并只显示中间部分
        with Image.open(image_path) as img:
            width, height = img.size
            left = (width - 1200) / 2
            top = (height - 300) / 2
            right = (width + 1200) / 2
            bottom = (height + 300) / 2
            cropped_img = img.crop((left, top, right, bottom))

            # 将裁剪后的图片转换为Base64编码
            buffered = BytesIO()
            cropped_img.save(buffered, format="PNG")
            encoded_string = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 添加图片到邮件正文
        image_tag = f'<p class="MsoNormal"><span style="font-family:&quot;微軟正黑體&quot;,sans-serif"><img src="data:image/png;base64,{encoded_string}" width="1200" height="300" alt="推薦的圖片"></span></p>'
        full_body += image_tag
    
    # 添加部門的專業課程
    if not dept_file_pro.empty and any(dept_file_pro['choose'] == 1):
        body = f'<p class="MsoNormal"><span style="font-family:&quot;微軟正黑體&quot;,sans-serif">推薦給{department}的 <strong>專業</strong> 線上課程：</span></p>'
        body += '<table><tr style="background-color:#e6f7ff;"><th>課程</th><th>課程描述</th><th>課程等級</th></tr>'
        for i in range(len(dept_file_pro)):
            if dept_file_pro['choose'].iloc[i] == 1:
                body += f'<tr>'
                body += f'<td style="width:33%;"><a href="{dept_file_pro["url"].iloc[i]}">{dept_file_pro["Course Title"].iloc[i]}</a></td>'
                body += f'<td style="width:60%;">{dept_file_pro["Course Description 中文"].iloc[i]}</td>'
                body += f'<td style="width:7%;">{dept_file_pro["course_level"].iloc[i]}</td>'
                body += "</tr>"
        body += "</table>"
        full_body += body

    # 添加部門的AI課程
    if not dept_file_ai.empty and any(dept_file_ai['choose'] == 1):
        body = f'<p class="MsoNormal"><span style="font-family:&quot;微軟正黑體&quot;,sans-serif">推薦給{department}的 <strong>AI</strong> 線上課程：</span></p>'
        body += '<table><tr style="background-color:#e6f7ff;"><th>課程</th><th>課程描述</th><th>課程等級</th></tr>'
        for i in range(len(dept_file_ai)):
            if dept_file_ai['choose'].iloc[i] == 1:
                body += "<tr>"
                body += f'<td style="width:33%;"><a href="{dept_file_ai["url"].iloc[i]}">{dept_file_ai["Course Title"].iloc[i]}</a></td>'
                body += f'<td style="width:60%;">{dept_file_ai["Course Description 中文"].iloc[i]}</td>'
                body += f'<td style="width:7%;">{dept_file_ai["course_level"].iloc[i]}</td>'
                body += "</tr>"
        body += "</table>"
        full_body += body

    
    
    # 設定郵件內容並發送
    mail.HTMLBody = full_body

    # # 添加投票選項
    # mail.VotingOptions = "推薦的課程很讚;推薦的課程還可以;推薦的課程仍需改善"

    try:
        mail.Send()
        print(f"郵件發送成功給: {department}")
    except Exception as e:
        print(f"郵件發送失敗給: {department}，錯誤訊息: {e}")


# import win32com.client as win32
# import pandas as pd

# # =============================================================================
# # 基本設定
# # =============================================================================
# outlook = win32.Dispatch('outlook.application')

# # =============================================================================
# # 帳戶設定
# # =============================================================================
# account = outlook.Session.Accounts.Item(1)

# # =============================================================================
# # 讀取Excel文件
# # =============================================================================
# file_pro = pd.read_excel("C:/Users/WCHuang8/Desktop/學習推薦系統專案/word2vec/output/top_matches_THR_pro2_translated.xlsx")
# file_AI = pd.read_excel("C:/Users/WCHuang8/Desktop/學習推薦系統專案/word2vec/output/top_matches_THR_aiaiggthis_translated.xlsx")

# # 部門列表和收件人對應
# departments_receivers = {
#     'Recruitment Department': ['wchuang8@winbond.com'],
#     'Training and Development Department': ['wchuang8@winbond.com'],
#     'Payroll Department': ['wchuang8@winbond.com'],
#     'Employee Relations Department': ['wchuang8@winbond.com']
# }

# # 部門與主管名稱對應
# department_managers = {
#     'Recruitment Department': 'AD10主管',
#     'Training and Development Department': 'AD20主管',
#     'Payroll Department': 'AD30主管',
#     'Employee Relations Department': 'AD40主管'
# }

# # 圖像路徑字典
# images = {
#     'Recruitment Department': "C:/Users/WCHuang8/Desktop/picture/圖片2.png",
#     'Training and Development Department': "C:/Users/WCHuang8/Desktop/picture/training.png",
#     'Payroll Department': "C:/Users/WCHuang8/Desktop/picture/payroll.png",
#     'Employee Relations Department': "C:/Users/WCHuang8/Desktop/picture/relation.png"
# }

# # 共用的 CSS 風格，設置字體為微軟正黑體
# css = "<style>body, table, p {font-family: '微軟正黑體';} table {border-collapse: collapse;} td, th {border: 1px solid black; padding: 8px;} h3 {font-family: '微軟正黑體';}</style>"

# # =============================================================================
# # 針對每個部門發送郵件
# # =============================================================================
# for department, receivers in departments_receivers.items():
    
#     # 選取該部門的專業課程和AI課程
#     dept_file_pro = file_pro[file_pro['Department Description'] == department]
#     dept_file_ai = file_AI[file_AI['Department Description'] == department]

#     # 如果該部門的課程選項中 `choose` 不為 1，則跳過發送
#     if not any(dept_file_pro['choose'] == 1) and not any(dept_file_ai['choose'] == 1):
#         continue
    
#     # 创建新的邮件对象
#     mail = outlook.CreateItem(0)
#     mail._oleobj_.Invoke(*(64209, 0, 8, 0, account))
    
#     # 初始化郵件收件人和主旨
#     mail.To = ";".join(receivers)
#     mail.Subject = '學習資源推薦'
    
#     # 設置每個部門特定的主管名稱
#     manager_name = department_managers.get(department, "主管")
#     header = f'<p class="MsoNormal"><span style="font-family:&quot;微軟正黑體&quot;,sans-serif"><h3>Dear {manager_name}：</h3><p>向您推薦一些優質的學習資源，這些資源可以幫助您和您的團隊在專業方面進一步提升。以下是外部學習資源系統判斷出非常有價值的課程和工具：</p></span></p>'
#     full_body_start = css + header

#     # 開始拼接郵件內容
#     full_body = full_body_start

#     # 添加圖片（如果有需要）
#     if department in images:
#         image_path = images[department]
#         attachment = mail.Attachments.Add(image_path)
#         image_cid = department.replace(' ', '_')  # 自訂一個CID
#         attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", image_cid)
#         image_tag = f'<p class="MsoNormal"><span style="font-family:&quot;微軟正黑體&quot;,sans-serif"><img src="cid:{image_cid}" width=100% height=100%></span></p>'
#         full_body += image_tag
    
#     # 添加部門的專業課程
#     if not dept_file_pro.empty and any(dept_file_pro['choose'] == 1):
#         body = f'<p class="MsoNormal"><span style="font-family:&quot;微軟正黑體&quot;,sans-serif">推薦給{department}的 <strong>專業</strong> 線上課程：</span></p>'
#         body += '<table><tr style="background-color:#e6f7ff;"><th>課程</th><th>課程描述</th><th>課程等級</th></tr>'
#         for i in range(len(dept_file_pro)):
#             if dept_file_pro['choose'].iloc[i] == 1:
#                 body += f'<tr>'
#                 body += f'<td style="width:33%;"><a href="{dept_file_pro["url"].iloc[i]}">{dept_file_pro["Course Title"].iloc[i]}</a></td>'
#                 body += f'<td style="width:60%;">{dept_file_pro["Course Description 中文"].iloc[i]}</td>'
#                 body += f'<td style="width:7%;">{dept_file_pro["course_level"].iloc[i]}</td>'
#                 body += "</tr>"
#         body += "</table>"
#         full_body += body

#     # 添加部門的AI課程
#     if not dept_file_ai.empty and any(dept_file_ai['choose'] == 1):
#         body = f'<p class="MsoNormal"><span style="font-family:&quot;微軟正黑體&quot;,sans-serif">推薦給{department}的 <strong>AI</strong> 線上課程：</span></p>'
#         body += '<table><tr style="background-color:#e6f7ff;"><th>課程</th><th>課程描述</th><th>課程等級</th></tr>'
#         for i in range(len(dept_file_ai)):
#             if dept_file_ai['choose'].iloc[i] == 1:
#                 body += "<tr>"
#                 body += f'<td style="width:33%;"><a href="{dept_file_ai["url"].iloc[i]}">{dept_file_ai["Course Title"].iloc[i]}</a></td>'
#                 body += f'<td style="width:60%;">{dept_file_ai["Course Description 中文"].iloc[i]}</td>'
#                 body += f'<td style="width:7%;">{dept_file_ai["course_level"].iloc[i]}</td>'
#                 body += "</tr>"
#         body += "</table>"
#         full_body += body

#     # 添加意見回饋投票示意圖
#     feedback_image_path = "C:/Users/WCHuang8/Desktop/picture/意見回饋投票示意圖.png"
#     feedback_attachment = mail.Attachments.Add(feedback_image_path)
#     feedback_cid = "feedback_image"
#     feedback_attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", feedback_cid)
#     feedback_image_tag = f'<p><img src="cid:{feedback_cid}" style="width:100%;"></p>'
#     full_body += feedback_image_tag
    
#     # 設定郵件內容並發送
#     mail.HTMLBody = full_body

#     # 添加投票選項
#     mail.VotingOptions = "推薦的課程很讚;推薦的課程還可以;推薦的課程仍需改善"

#     try:
#         mail.Send()
#         print(f"郵件發送成功給: {department}")
#     except Exception as e:
#         print(f"郵件發送失敗給: {department}，錯誤訊息: {e}")
