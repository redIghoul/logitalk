import threading
from socket import *
from customtkinter import *

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title("Чат")
        self.minsize(400, 300)
        self.geometry("600x400")

        self.frame = CTkFrame(self, width=0)
        self.frame.pack(side="left", fill="y")
        self.frame.pack_propagate(False)
        self.is_show_menu = False
        self.frame_width = 0

        self.label = CTkLabel(self.frame, text='Ваше Ім`я')
        self.label.pack(pady=20)

        self.entry = CTkEntry(self.frame)
        self.entry.pack(pady=5)

        self.save_btn = CTkButton(self.frame, text="Зберегти нік", command=self.save_username)
        self.save_btn.pack(pady=10)

        self.label_theme = CTkOptionMenu(self.frame, values=['Темна', 'Світла'], command=self.change_theme)
        self.label_theme.pack(side='bottom', pady=20)

        self.chat_frame = CTkFrame(self)
        self.chat_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        self.menu_show_speed = 20

        self.chat_text = CTkTextbox(self.chat_frame, state='disabled')
        self.chat_text.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        self.bottom_frame = CTkFrame(self.chat_frame)
        self.bottom_frame.pack(fill="x", pady=5)

        self.message_input = CTkEntry(self.bottom_frame, placeholder_text='Введіть повідомлення:')
        self.message_input.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # 🔽 Додаємо підтримку Enter для надсилання повідомлень
        self.message_input.bind("<Return>", lambda event: self.send_message())

        self.send_button = CTkButton(self.bottom_frame, text='▶️', width=40, command=self.send_message)
        self.send_button.pack(side="right")

        self.username = "User"

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("6.tcp.eu.ngrok.io", 15614))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"❌ Не вдалося підключитися: {e}")

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()

    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += self.menu_show_speed
            self.frame.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='◀️')
        if self.is_show_menu:
            self.after(20, self.show_menu)

    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= self.menu_show_speed
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='▶️')
        if not self.is_show_menu:
            self.after(20, self.close_menu)

    def change_theme(self, value):
        if value == 'Темна':
            set_appearance_mode('dark')
        else:
            set_appearance_mode('light')

    def send_message(self):
        message = self.message_input.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_input.delete(0, END)

    def add_message(self, text):
        self.chat_text.configure(state='normal')
        self.chat_text.insert(END, text + '\n')
        self.chat_text.configure(state='disabled')
        self.chat_text.see(END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(f"{author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)

    def save_username(self):
        new_name = self.entry.get().strip()
        if new_name:
            old_name = self.username
            self.username = new_name
            try:
                msg = f"TEXT@{self.username}@[SYSTEM] {old_name} змінив(ла) імʼя на {self.username}\n"
                self.sock.send(msg.encode('utf-8'))
            except:
                pass
            self.add_message(f"✅ Нік змінено на {self.username}")

win = MainWindow()
win.mainloop()