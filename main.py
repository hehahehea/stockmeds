import sqlite3
import pytz
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from datetime import datetime

# Database Setup
conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    stock INTEGER NOT NULL,
    expiry_date DATE NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    medicine_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    date_taken DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Get Manila Timezone
def get_manila_time():
    tz = pytz.timezone('Asia/Manila')
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

# Kivy App Class
class PharmacyApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Add Medicine Section
        self.med_name = TextInput(hint_text="Name of Medicine", multiline=False)
        self.med_stock = TextInput(hint_text="Stock", input_filter='int', multiline=False)
        self.med_expiry = TextInput(hint_text="Expiry Date (YYYY-MM-DD)", multiline=False)
        self.add_button = Button(text="Add Medicine", on_press=self.add_medicine)

        # Edit Medicine Section
        self.edit_med_name = TextInput(hint_text="Medicine to Edit", multiline=False)
        self.new_med_name = TextInput(hint_text="New Name (Leave blank if same)", multiline=False)
        self.new_med_stock = TextInput(hint_text="New Stock (Leave blank if same)", input_filter='int', multiline=False)
        self.new_med_expiry = TextInput(hint_text="New Expiry Date (YYYY-MM-DD) (Leave blank if same)", multiline=False)
        self.edit_button = Button(text="Edit Medicine", on_press=self.edit_medicine)

        # Dispense Medicine Section
        self.patient_name = TextInput(hint_text="Name of Patient", multiline=False)
        self.dispense_med = TextInput(hint_text="Name of Medicine", multiline=False)
        self.dispense_qty = TextInput(hint_text="Quantity Taken", input_filter='int', multiline=False)
        self.dispense_button = Button(text="Give Medicine", on_press=self.dispense_medicine)

        # Other Functions
        self.check_stock_button = Button(text="Show Stock", on_press=self.show_stock)
        self.check_expiry_button = Button(text="Check Expiry", on_press=self.check_expiry)

        # Add Widgets to Layout
        self.layout.add_widget(Label(text="Cabiao Senior High School"))

        self.layout.add_widget(Label(text="Add Medicine"))
        self.layout.add_widget(self.med_name)
        self.layout.add_widget(self.med_stock)
        self.layout.add_widget(self.med_expiry)
        self.layout.add_widget(self.add_button)

        self.layout.add_widget(Label(text="Edit Medicine"))
        self.layout.add_widget(self.edit_med_name)
        self.layout.add_widget(self.new_med_name)
        self.layout.add_widget(self.new_med_stock)
        self.layout.add_widget(self.new_med_expiry)
        self.layout.add_widget(self.edit_button)

        self.layout.add_widget(Label(text="Give Medicine"))
        self.layout.add_widget(self.patient_name)
        self.layout.add_widget(self.dispense_med)
        self.layout.add_widget(self.dispense_qty)
        self.layout.add_widget(self.dispense_button)

        self.layout.add_widget(self.check_stock_button)
        self.layout.add_widget(self.check_expiry_button)

        return self.layout

    # Function to Add Medicine (Prevents Duplicate)
    def add_medicine(self, instance):
        name = self.med_name.text.strip()
        stock = self.med_stock.text.strip()
        expiry = self.med_expiry.text.strip()

        cursor.execute("SELECT id FROM medicines WHERE name = ?", (name,))
        existing_medicine = cursor.fetchone()

        if existing_medicine:
            self.show_popup("Error", "Medicine already exists! Use Edit instead.")
        elif name and stock and expiry:
            cursor.execute("INSERT INTO medicines (name, stock, expiry_date) VALUES (?, ?, ?)", (name, int(stock), expiry))
            conn.commit()
            self.show_popup("Success", f"{name} added with {stock} stock!")
            self.med_name.text = ""
            self.med_stock.text = ""
            self.med_expiry.text = ""
        else:
            self.show_popup("Error", "Fill all fields!")

    # Function to Edit Medicine
    def edit_medicine(self, instance):
        old_name = self.edit_med_name.text.strip()
        new_name = self.new_med_name.text.strip()
        new_stock = self.new_med_stock.text.strip()
        new_expiry = self.new_med_expiry.text.strip()

        cursor.execute("SELECT id FROM medicines WHERE name = ?", (old_name,))
        medicine = cursor.fetchone()

        if not medicine:
            self.show_popup("Error", "Medicine not found!")
            return

        if new_name:
            cursor.execute("UPDATE medicines SET name = ? WHERE name = ?", (new_name, old_name))
        if new_stock:
            cursor.execute("UPDATE medicines SET stock = ? WHERE name = ?", (int(new_stock), old_name if not new_name else new_name))
        if new_expiry:
            cursor.execute("UPDATE medicines SET expiry_date = ? WHERE name = ?", (new_expiry, old_name if not new_name else new_name))

        conn.commit()
        self.show_popup("Success", "Medicine details updated!")

    # Function to Dispense Medicine
    def dispense_medicine(self, instance):
        patient = self.patient_name.text.strip()
        medicine = self.dispense_med.text.strip()
        quantity = self.dispense_qty.text.strip()

        if not patient or not medicine or not quantity:
            self.show_popup("Error", "Fill all fields!")
            return

        cursor.execute("SELECT stock FROM medicines WHERE name = ?", (medicine,))
        result = cursor.fetchone()

        if not result:
            self.show_popup("Error", "Medicine not found!")
            return

        current_stock = result[0]

        if int(quantity) > current_stock:
            self.show_popup("Error", "Not enough stock!")
            return

        # Update Stock
        new_stock = current_stock - int(quantity)
        cursor.execute("UPDATE medicines SET stock = ? WHERE name = ?", (new_stock, medicine))
       
        # Add to Logs
        cursor.execute("INSERT INTO logs (patient_name, medicine_name, quantity, date_taken) VALUES (?, ?, ?, ?)",
                      (patient, medicine, int(quantity), get_manila_time()))

        conn.commit()
        self.show_popup("Success", f"{quantity} {medicine} dispensed to {patient}!")

    # Function to Show Stock
    def show_stock(self, instance):
        cursor.execute("SELECT name, stock FROM medicines")
        medicines = cursor.fetchall()
        stock_info = "\n".join([f"{name}: {stock}" for name, stock in medicines])
        self.show_popup("Medicine Stock", stock_info if stock_info else "No medicine available.")

    # Function to Check Expiry
    def check_expiry(self, instance):
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT name, expiry_date FROM medicines WHERE expiry_date <= ?", (today,))
        expired_meds = cursor.fetchall()
        expiry_info = "\n".join([f"{name}: Expired on {expiry}" for name, expiry in expired_meds])
        self.show_popup("Expired Medicines", expiry_info if expiry_info else "No expired medicines.")

    # Function to Show Popup Messages
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

    # Close DB Connection When App Stops
    def on_stop(self):
        conn.close()

# Run the App
if __name__ == "__main__":
    PharmacyApp().run()