# https://support.google.com/accounts/answer/185833?visit_id=638228519309478547-2329963985&p=InvalidSecondFactor&rd=1
# Generate the google app

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import sqlite3
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re

def save(name):
    selected_file = ""  

    def upload_file():
        nonlocal selected_file
        file_path = filedialog.askopenfilename()
        selected_file = file_path
        print("Choosed file:", selected_file)

    def send_email():
        nonlocal selected_file
        
        # 使用者資訊。
        email_sender = 'ekatmdrkd7227@gmail.com'  
        email_password = 'udnqcefrjnobwqre'  
        email_receiver = email_entry.get() 
        email_subject = subject_entry.get()  
        email_body = msg_text.get("1.0", "end-1c")  

        message = MIMEMultipart()
        message['From'] = email_sender
        message['To'] = email_receiver
        message['Subject'] = email_subject
    
        # add content
        message.attach(MIMEText(email_body, 'plain'))

        # add file
        if selected_file:
            attachment = open(selected_file, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=selected_file)
            message.attach(part)

        # Gmail server login
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_password)

        # send email
        server.send_message(message)
        server.quit()

    new_window = tk.Toplevel()
    new_window.title(f"Send email to {name}")

    upload_button = tk.Button(new_window, text="Upload file", command=upload_file)
    upload_button.pack()

    email_label = tk.Label(new_window, text="Receiver email:")
    email_label.pack()
    email_entry = tk.Entry(new_window)
    email_entry.pack()
    email_entry.delete(0, tk.END)  
    email_entry.insert(tk.END, values[1])  
    
    subject_label = tk.Label(new_window, text="Title:")
    subject_label.pack()
    subject_entry = tk.Entry(new_window)
    subject_entry.pack()
    
    msg_label = tk.Label(new_window, text="Content:")
    msg_label.pack()
    msg_text = tk.Text(new_window, height=5, width=30)
    msg_text.pack()
    
    confirm_button = tk.Button(new_window, text="Confirm", command=send_email)
    confirm_button.pack()

    
def load_address_book():
    cursor.execute("SELECT * FROM Our_members")
    rows = cursor.fetchall()
    
    # 好像不寫這一行會不斷的累加輸出 <name, email, time> 資訊。
    address_list.delete(*address_list.get_children())

    # 一行一行輸入。
    for row in rows:
        address_list.insert("", tk.END, values=row)
        
def view_contact(event):
    global values
    
    # 回傳使用者選的東西。
    selected_item = address_list.focus()

    # 再回傳使用者選的欄位的資訊。
    values = address_list.item(selected_item, "values")

    if values:
        # extract 名字
        name = values[0]
        print(values)
        save(name)
        
def add_to_address_book():
    name = name_entry.get()
    address = address_entry.get()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if name == "" or address == "":
        messagebox.showwarning("Warning", "Please insert the name and email.")
        return

    # email format check。
    if not re.match(r'^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$', address):
        messagebox.showwarning("email error", "Please insert the correct email.")
        return

    # 判斷是否新增的使用者是之前已經輸入過的。
    cursor.execute("SELECT * FROM Our_members WHERE name = ?", (name,))
    existing_row = cursor.fetchone()

    if existing_row:
        # 如果是的話 更新舊資訊 -> 新資訊。
        cursor.execute("UPDATE Our_members SET address = ?, time = ? WHERE name = ?", (address, current_time, name))
    else:
        # 如果不是的話 新增。
        cursor.execute("INSERT INTO Our_members VALUES (?, ?, ?)", (name, address, current_time))

    connection.commit()

    # 更新 Address book 資訊。
    load_address_book()

    # 輸入欄位初始化。
    name_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)

if __name__ == "__main__":
    """
    本作品的主要目的是不用特地打開 "gmail" 
    也可以透過單一個 APP 就可以發 "email"
    同時也可以附上一些照片、影片類等資訊。
    提升工作上的方便性。
    """
    # 主要 create 我們會用到的 database。
    connection = sqlite3.connect("Our_members.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Our_members (name TEXT, email TEXT, time TEXT)")

    window = tk.Tk()
    window.title("Address book")
    window.resizable(False, False) # 無法調整視窗的大小。
    
    # 輸入要添加人的名字。
    name_label = tk.Label(window, text="NAME:")
    name_label.pack()
    name_entry = tk.Entry(window)
    name_entry.pack()

    # 輸入要添加人的 email。
    address_label = tk.Label(window, text="EMAIL:")
    address_label.pack()
    address_entry = tk.Entry(window)
    address_entry.pack()

    # 把這個資訊添加到上面所創的 database。
    add_button = tk.Button(window, text="Add to Address book", command=add_to_address_book)
    add_button.pack()

    # 因為一旦超過視窗的量，我們需要添加 scrollbar 來增加使用者的方便性。
    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 輸出 Address book 資訊
    address_list = ttk.Treeview(window, columns=("Name", "Email", "Time"), yscrollcommand=scrollbar.set)
    
    # 刪掉第一個 column。
    address_list.column("#0", width=0, stretch=tk.NO) 
    address_list.heading("#0", text="", anchor=tk.CENTER)  
    address_list.heading("Name", text="Name")
    address_list.heading("Email", text="Email")
    address_list.heading("Time", text="Time")
    address_list.pack()

    # yview = 垂直方向 scrollbar
    scrollbar.config(command=address_list.yview)
    
    # 輸入完會員的資訊之後，再 load 一下使用者的資訊來 refresh 更新畫面顯示的資訊。
    load_address_book()

    # 如果使用者針對 Address 資訊欄點兩下後任何一個人的資訊之後，會跳出打內容的視窗。
    address_list.bind("<Double-1>", view_contact)
    
    # 執行 GUI
    window.mainloop()

    # 結束
    cursor.close()
    connection.close()
