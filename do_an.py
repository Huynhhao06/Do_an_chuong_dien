import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import paho.mqtt.client as mqtt
MAY_CHU = "broker.hivemq.com"
CMD_TOPIC = "lop9/relay/cmd"
STATE_TOPIC = "lop9/relay/state"
mqtt_client = mqtt.Client()
trang_thai_chuong = False  
def bat_chuong():
    mqtt_client.publish(CMD_TOPIC, "ON")
def tat_chuong():
    mqtt_client.publish(CMD_TOPIC, "OFF")
def on_message(client, userdata, msg):
    global trang_thai_chuong
    payload = msg.payload.decode()

    if msg.topic == STATE_TOPIC:
        if payload == "ON":
            trang_thai_chuong = True
            cap_nhat_gui(True)
        elif payload == "OFF":
            trang_thai_chuong = False
            cap_nhat_gui(False)
def cap_nhat_gui(bat):
    if bat:
        nhan_trang_thai.config(text="Chuông: ĐANG RUNG", fg="green")
    else:
        nhan_trang_thai.config(text="Chuông: TẮT", fg="red")
LICH_MUA_DONG = [
    "07:00", "07:50", "08:45", "09:40", "10:35",
    "13:00", "13:55", "14:45", "15:40", "16:35"
]
LICH_MUA_HE = [
    "06:30", "07:25", "08:15", "09:10", "10:05",
    "13:30", "14:20", "15:15", "16:10", "17:05"
]
CAC_THU = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
cau_hinh_tuan = {
    thu: {
        "kich_hoat": True,
        "che_do": "lich",     # lich | tuy_chinh
        "gio_tuy_chinh": []
    } for thu in CAC_THU
}
cua_so = tk.Tk()
cua_so.title("Đồ án chuông điện cho trường học")
cua_so.geometry("900x620")
che_do_mua = tk.StringVar(value="dong")
nhan_gio = tk.Label(cua_so, font=("Arial", 20, "bold"), fg="#7f8c8d")
nhan_gio.pack(pady=10)
def cap_nhat_gio():
    hien_tai = datetime.now()
    thu = CAC_THU[hien_tai.weekday()]
    nhan_gio.config(
        text=f"{thu} | {hien_tai.strftime('%H:%M:%S')} | {hien_tai.strftime('%d/%m/%Y')}"
    )
    cua_so.after(1000, cap_nhat_gio)
def an_chuot(event):
    bat_chuong()
def nha_chuot(event):
    tat_chuong()
nut_giu = tk.Button(
    cua_so,
    text="GIỮ ĐỂ RUNG CHUÔNG",
    font=("Arial", 16),
    bg="orange",
    width=22,
    height=2
)
nut_giu.bind("<ButtonPress-1>", an_chuot)
nut_giu.bind("<ButtonRelease-1>", nha_chuot)
nut_giu.pack(pady=10)
nhan_trang_thai = tk.Label(cua_so, text="Chuông: TẮT", font=("Arial", 14), fg="red")
nhan_trang_thai.pack()
khung_tuan = tk.LabelFrame(cua_so, text="Lịch hoạt động theo ngày")
khung_tuan.pack(pady=15)
bien_check = {}
nhan_che_do = {}
def cap_nhat_mau(thu):
    cau_hinh = cau_hinh_tuan[thu]
    if not cau_hinh["kich_hoat"]:
        mau, chu = "#e5e7e9", "Tắt"
    elif cau_hinh["che_do"] == "tuy_chinh":
        mau, chu = "#fad7a0", "Tuỳ chỉnh"
    else:
        mau, chu = "#d5f5e3", "Theo lịch"
    nhan_che_do[thu].config(bg=mau, text=chu)
def bat_tat_thu(thu):
    cau_hinh_tuan[thu]["kich_hoat"] = bien_check[thu].get()
    cap_nhat_mau(thu)
def mo_cua_so_gio(thu):
    cau_hinh = cau_hinh_tuan[thu]
    win = tk.Toplevel(cua_so)
    win.geometry("360x320")
    win.resizable(False, False)
    win.grab_set()
    tk.Label(win, text=f"Giờ chuông {thu}", font=("Arial", 15, "bold")).pack(pady=10)
    listbox = tk.Listbox(win, width=10, height=6, font=("Arial", 12))
    listbox.pack()
    for t in cau_hinh["gio_tuy_chinh"]:
        listbox.insert(tk.END, t)
    khung_nhap = tk.Frame(win)
    khung_nhap.pack(pady=10)
    gio = tk.Spinbox(khung_nhap, from_=0, to=23, width=4, format="%02.0f")
    gio.pack(side="left", padx=5)
    tk.Label(khung_nhap, text=":").pack(side="left")
    phut = tk.Spinbox(khung_nhap, from_=0, to=59, width=4, format="%02.0f")
    phut.pack(side="left", padx=5)
    def them():
        t = f"{gio.get()}:{phut.get()}"
        if t not in listbox.get(0, tk.END):
            listbox.insert(tk.END, t)
    tk.Button(khung_nhap, text="THÊM", command=them).pack(side="left", padx=10)
    def xoa():
        sel = listbox.curselection()
        if sel:
            listbox.delete(sel[0])
    tk.Button(win, text="XOÁ GIỜ", command=xoa).pack(pady=5)
    def luu():
        cau_hinh["gio_tuy_chinh"] = sorted(listbox.get(0, tk.END))
        cau_hinh["che_do"] = "tuy_chinh"
        cap_nhat_mau(thu)
        win.destroy()
    tk.Button(
        win, text="LƯU",
        bg="#27ae60", fg="white",
        font=("Arial", 13, "bold"),
        width=16, command=luu
    ).pack(pady=15)
def hien_menu(event, thu):
    menu = tk.Menu(cua_so, tearoff=0)
    def dung_lich():
        cau_hinh_tuan[thu]["che_do"] = "lich"
        cau_hinh_tuan[thu]["gio_tuy_chinh"] = []
        cap_nhat_mau(thu)
    def tuy_chinh():
        cau_hinh_tuan[thu]["che_do"] = "tuy_chinh"
        cap_nhat_mau(thu)
        mo_cua_so_gio(thu)
    menu.add_command(label="Theo lịch", command=dung_lich)
    menu.add_command(label="Tuỳ chỉnh", command=tuy_chinh)
    menu.tk_popup(event.x_root, event.y_root)
for i, thu in enumerate(CAC_THU):
    bien = tk.BooleanVar(value=True)
    tk.Checkbutton(
        khung_tuan, text=thu,
        variable=bien,
        command=lambda t=thu: bat_tat_thu(t)
    ).grid(row=i, column=0, sticky="w", padx=10, pady=2)
    nhan = tk.Label(khung_tuan, width=12, relief="ridge", cursor="hand2")
    nhan.grid(row=i, column=1, padx=10)
    nhan.bind("<Button-1>", lambda e, t=thu: hien_menu(e, t))
    bien_check[thu] = bien
    nhan_che_do[thu] = nhan
    cap_nhat_mau(thu)
def doi_mua():
    if not messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đổi mùa không?"):
        che_do_mua.set("dong")
khung_mua = tk.LabelFrame(cua_so, text="Chế độ mùa")
khung_mua.pack(pady=10)
tk.Radiobutton(khung_mua, text="Mùa đông",
               variable=che_do_mua, value="dong",
               command=doi_mua).pack(side="left", padx=15)
tk.Radiobutton(khung_mua, text="Mùa hè",
               variable=che_do_mua, value="he",
               command=doi_mua).pack(side="left", padx=15)
lan_rung_cuoi = {"thu": None, "gio": None}
def xu_ly_chuong():
    hien_tai = datetime.now()
    thu = CAC_THU[hien_tai.weekday()]
    gio_phut = hien_tai.strftime("%H:%M")
    if hien_tai.second == 0:
        cau_hinh = cau_hinh_tuan[thu]
        if cau_hinh["kich_hoat"]:
            danh_sach_gio = (
                cau_hinh["gio_tuy_chinh"]
                if cau_hinh["che_do"] == "tuy_chinh"
                else (
                    LICH_MUA_DONG
                    if che_do_mua.get() == "dong"
                    else LICH_MUA_HE
                )
            )

            if gio_phut in danh_sach_gio:
                if lan_rung_cuoi["thu"] != thu or lan_rung_cuoi["gio"] != gio_phut:
                    lan_rung_cuoi["thu"] = thu
                    lan_rung_cuoi["gio"] = gio_phut
                    bat_chuong()
                    cua_so.after(5000, tat_chuong)
    cua_so.after(200, xu_ly_chuong)
mqtt_client.on_message = on_message
mqtt_client.connect(MAY_CHU, 1883, 60)
mqtt_client.subscribe(STATE_TOPIC)
mqtt_client.loop_start()
cap_nhat_gio()
xu_ly_chuong()
cua_so.mainloop()
