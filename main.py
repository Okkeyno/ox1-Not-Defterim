import os
import sqlite3
import customtkinter as ctk

# VERİTABANI YOLU AYARI (AppData/Local/Rehbercim)
#
app_data_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "ox1 Not Defterim")
os.makedirs(app_data_dir, exist_ok=True)  # Klasör yoksa otomatik oluştur kodu

db_path = os.path.join(app_data_dir, "duties.db")

#
# VERİTABANI KURULUMU VE BAĞLANMA
#
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS duties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    number TEXT NOT NULL UNIQUE,
    notum TEXT,
    tag TEXT NOT NULL DEFAULT 'default',
    status TEXT NOT NULL DEFAULT 'active'
)
"""
)
connection.commit()

#
# GÖRSEL ARAYÜZ (UI) TASARIMI
#
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Ox1App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ox1 Not Defterim")
        self.geometry("450x650") #ekran boyutu
        self.resizable(False, False)

        self.title_label = ctk.CTkLabel(
            self,
            text="ox1 Not Defterim",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title_label.pack(pady=(20, 10))

        # VERİ GİRİŞ ALANLARI
        #
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=20, pady=10)

        self.name_entry = ctk.CTkEntry(
            self.form_frame, placeholder_text="Task Name"
        )
        self.name_entry.pack(fill="x", padx=10, pady=5)

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=20, pady=2)

        # Satırda 2 kutucuk olacak şekilde çerçeve  
        self.number_entry = ctk.CTkEntry(
            self.form_frame, placeholder_text="Number"
        )
        self.number_entry.pack(side="left",fill="x", padx=10, pady=5)

        self.tag_entry = ctk.CTkEntry(
            self.form_frame, placeholder_text="Tag (#acil)"
        )
        self.tag_entry.pack(side="right",fill="x", padx=10, pady=5)

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=20, pady=10)

        self.notum_entry = ctk.CTkEntry(
            self.form_frame, placeholder_text="Not (optional)"
        )
        self.notum_entry.pack(fill="x", padx=10, pady=5)

        self.add_btn = ctk.CTkButton(
            self.form_frame,
            text="Add Task",
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.add_task,
        )
        self.add_btn.pack(fill="x", padx=10, pady=(5, 10))

        # ARAMA ALANI
        self.search_entry = ctk.CTkEntry(
            self, placeholder_text="Search task..."
        )
        self.search_entry.pack(fill="x", padx=20, pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_task)

        self.status_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=2)

        # GÖREV LİSTESİ
        self.list_frame = ctk.CTkScrollableFrame(self, height=320)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_duties()

    def add_task(self):
        name = self.name_entry.get().strip()
        number = self.number_entry.get().strip()
        tag = self.tag_entry.get().strip()
        notum = self.notum_entry.get().strip()

        if not name or not number:
            self.show_status(" Please fill in name and number!", "red")
            return

        try:
            cursor.execute(
                "INSERT INTO duties (name, number, tag, notum) VALUES (?, ?, ?, ?)",
                (name, number, tag, notum),
            )
            connection.commit()
            self.show_status(f"Added: {name}", "green")

            self.name_entry.delete(0, "end")
            self.number_entry.delete(0, "end")
            self.tag_entry.delete(0, "end")
            self.notum_entry.delete(0, "end")
            self.load_duties()
        except sqlite3.IntegrityError:
            self.show_status("number already exists!", "red")

    def load_duties(self, rows=None):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if rows is None:
            cursor.execute("SELECT * FROM duties ORDER BY name ASC")
            rows = cursor.fetchall()

        if not rows:
            no_data_label = ctk.CTkLabel(
                self.list_frame, text="No duties found."
            )
            no_data_label.pack(pady=20)
            return

        for row in rows:
            contact_id, name, number, notum, tag = row[0], row[1], row[2], row[3], row[4]

            card = ctk.CTkFrame(self.list_frame, fg_color="#2A2D2E")
            card.pack(fill="x", pady=4, padx=5)

            if notum:
                info_text = f" {name}\n {number}\n {tag} \n {notum}"
            else:
                info_text = f" {name}\n {number}\n {tag}"

            info_label = ctk.CTkLabel(
                card, text=info_text, justify="left", anchor="w"
            )
            info_label.pack(side="left", padx=10, pady=8)

            delete_btn = ctk.CTkButton(
                card,
                text="Delete",
                width=60,
                height=28,
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=lambda c_id=contact_id: self.delete_contact(c_id),
            )
            delete_btn.pack(side="right", padx=10)

    def search_task(self, event=None):
        query = self.search_entry.get().strip()
        cursor.execute(
            "SELECT * FROM duties WHERE (name LIKE ?) OR (tag LIKE ?) OR (notum LIKE ?) ORDER BY name ASC",
            (f"%{query}%", f"%{query}%", f"%{query}%"),
        )
        results = cursor.fetchall()
        self.load_duties(results)

    def delete_contact(self, contact_id):
        cursor.execute("DELETE FROM duties WHERE id = ?", (contact_id,))
        connection.commit()
        self.show_status("🗑️ Contact deleted", "orange")
        self.load_duties()

    def show_status(self, message, color):
        color_map = {
            "red": "#F87171",
            "green": "#4ADE80",
            "orange": "#FBBF24",
        }
        self.status_label.configure(
            text=message, text_color=color_map.get(color, "white")
        )


if __name__ == "__main__":
    app = Ox1App()
    app.mainloop()
    connection.close()