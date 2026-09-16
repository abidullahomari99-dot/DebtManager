import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


# =========================================================
# DATABASE
# =========================================================

class Database:

    def __init__(self):

        self.conn = sqlite3.connect(
            "debt_manager.db"
        )

        self.cursor = self.conn.cursor()

        self.create_tables()


    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT
        )
        """)

        self.conn.commit()


    # =====================================================
    # CUSTOMER
    # =====================================================

    def add_customer(
        self,
        name,
        phone,
        address
    ):

        self.cursor.execute("""
        INSERT INTO customers
        (name, phone, address)
        VALUES (?, ?, ?)
        """, (
            name,
            phone,
            address
        ))

        self.conn.commit()


    def get_customers(self):

        self.cursor.execute("""
        SELECT id, name, phone, address
        FROM customers
        ORDER BY id DESC
        """)

        return self.cursor.fetchall()


    def search_customers(
        self,
        keyword
    ):

        keyword = f"%{keyword}%"

        self.cursor.execute("""
        SELECT id, name, phone, address
        FROM customers
        WHERE name LIKE ?
           OR phone LIKE ?
           OR address LIKE ?
           OR CAST(id AS TEXT) LIKE ?
        ORDER BY id DESC
        """, (
            keyword,
            keyword,
            keyword,
            keyword
        ))

        return self.cursor.fetchall()


    def get_customer(
        self,
        customer_id
    ):

        self.cursor.execute("""
        SELECT id, name, phone, address
        FROM customers
        WHERE id = ?
        """, (
            customer_id,
        ))

        return self.cursor.fetchone()


    def update_customer(
        self,
        customer_id,
        name,
        phone,
        address
    ):

        self.cursor.execute("""
        UPDATE customers
        SET name = ?,
            phone = ?,
            address = ?
        WHERE id = ?
        """, (
            name,
            phone,
            address,
            customer_id
        ))

        self.conn.commit()


    def delete_customer(
        self,
        customer_id
    ):

        self.cursor.execute("""
        DELETE FROM debts
        WHERE customer_id = ?
        """, (
            customer_id,
        ))

        self.cursor.execute("""
        DELETE FROM payments
        WHERE customer_id = ?
        """, (
            customer_id,
        ))

        self.cursor.execute("""
        DELETE FROM customers
        WHERE id = ?
        """, (
            customer_id,
        ))

        self.conn.commit()


    # =====================================================
    # DEBT
    # =====================================================

    def add_debt(
        self,
        customer_id,
        amount,
        description
    ):

        date = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )

        self.cursor.execute("""
        INSERT INTO debts
        (customer_id, amount, description, date)
        VALUES (?, ?, ?, ?)
        """, (
            customer_id,
            amount,
            description,
            date
        ))

        self.conn.commit()


    # =====================================================
    # PAYMENT
    # =====================================================

    def add_payment(
        self,
        customer_id,
        amount,
        description
    ):

        date = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )

        self.cursor.execute("""
        INSERT INTO payments
        (customer_id, amount, description, date)
        VALUES (?, ?, ?, ?)
        """, (
            customer_id,
            amount,
            description,
            date
        ))

        self.conn.commit()


    # =====================================================
    # TOTAL DEBT
    # =====================================================

    def get_total_debt(
        self,
        customer_id
    ):

        self.cursor.execute("""
        SELECT COALESCE(
            SUM(amount), 0
        )
        FROM debts
        WHERE customer_id = ?
        """, (
            customer_id,
        ))

        return self.cursor.fetchone()[0]


    # =====================================================
    # TOTAL PAYMENT
    # =====================================================

    def get_total_payment(
        self,
        customer_id
    ):

        self.cursor.execute("""
        SELECT COALESCE(
            SUM(amount), 0
        )
        FROM payments
        WHERE customer_id = ?
        """, (
            customer_id,
        ))

        return self.cursor.fetchone()[0]


    # =====================================================
    # REMAINING
    # =====================================================

    def get_remaining(
        self,
        customer_id
    ):

        debt = self.get_total_debt(
            customer_id
        )

        payment = self.get_total_payment(
            customer_id
        )

        return debt - payment


    # =====================================================
    # HISTORY
    # =====================================================

    def get_debt_history(
        self,
        customer_id
    ):

        self.cursor.execute("""
        SELECT amount, description, date
        FROM debts
        WHERE customer_id = ?
        ORDER BY id DESC
        """, (
            customer_id,
        ))

        return self.cursor.fetchall()


    def get_payment_history(
        self,
        customer_id
    ):

        self.cursor.execute("""
        SELECT amount, description, date
        FROM payments
        WHERE customer_id = ?
        ORDER BY id DESC
        """, (
            customer_id,
        ))

        return self.cursor.fetchall()


    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        self.conn.close()


# =========================================================
# MODERN BUTTON
# =========================================================

class ModernButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.background_normal = ""

        self.background_color = (
            0, 0, 0, 0
        )

        with self.canvas.before:

            Color(
                0.10,
                0.45,
                0.85,
                1
            )

            self.rect = RoundedRectangle(
                radius=[dp(15)]
            )

        self.bind(
            pos=self.update_rect,
            size=self.update_rect
        )


    def update_rect(
        self,
        *args
    ):

        self.rect.pos = self.pos
        self.rect.size = self.size


# =========================================================
# APP
# =========================================================

class DebtManagerApp(App):

    def build(self):

        self.title = "Debt Manager"

        self.db = Database()

        root = BoxLayout(
            orientation="vertical"
        )


        # =================================================
        # HEADER
        # =================================================

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(115),
            padding=dp(15)
        )

        self.header = header

        with header.canvas.before:

            Color(
                0.05,
                0.20,
                0.40,
                1
            )

            self.header_rect = RoundedRectangle(
                radius=[dp(18)]
            )

        header.bind(
            pos=self.update_header,
            size=self.update_header
        )


        title = Label(
            text="DEBT MANAGER",
            font_size=dp(27),
            bold=True,
            color=(1, 1, 1, 1)
        )


        subtitle = Label(
            text="Simple • Secure • Organized",
            font_size=dp(14),
            color=(
                0.85,
                0.90,
                1,
                1
            )
        )


        header.add_widget(title)
        header.add_widget(subtitle)

        root.add_widget(header)


        # =================================================
        # SCROLL
        # =================================================

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )


        content = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(18),
            size_hint_y=None
        )


        content.bind(
            minimum_height=
            content.setter("height")
        )


        welcome = Label(
            text="Welcome to Debt Manager",
            font_size=dp(22),
            bold=True,
            color=(
                0.10,
                0.15,
                0.20,
                1
            ),
            size_hint_y=None,
            height=dp(55)
        )


        content.add_widget(
            welcome
        )


        # =================================================
        # DASHBOARD BUTTON
        # =================================================

        dashboard = ModernButton(
            text="🏠   DASHBOARD",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(65)
        )

        dashboard.bind(
            on_press=self.show_dashboard
        )

        content.add_widget(dashboard)


        # =================================================
        # ADD CUSTOMER
        # =================================================

        add_customer = ModernButton(
            text="👤   ADD CUSTOMER",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(65)
        )

        add_customer.bind(
            on_press=self.show_add_customer
        )

        content.add_widget(add_customer)


        # =================================================
        # SEARCH
        # =================================================

        search = ModernButton(
            text="🔍   SEARCH CUSTOMER",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(65)
        )

        search.bind(
            on_press=self.show_customers
        )

        content.add_widget(search)


        # =================================================
        # ADD DEBT
        # =================================================

        add_debt = ModernButton(
            text="💰   ADD DEBT",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(65)
        )

        add_debt.bind(
            on_press=self.show_add_debt
        )

        content.add_widget(add_debt)


        # =================================================
        # PAYMENT
        # =================================================

        payment = ModernButton(
            text="💵   MAKE PAYMENT",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(65)
        )

        payment.bind(
            on_press=self.show_payment
        )

        content.add_widget(payment)


        # =================================================
        # ALL DEBTORS
        # =================================================

        debtors = ModernButton(
            text="📋   ALL DEBTORS",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(65)
        )

        debtors.bind(
            on_press=self.show_customers
        )

        content.add_widget(debtors)


        # =================================================
        # REPORT
        # =================================================

        report = ModernButton(
            text="📊   REPORTS",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(65)
        )

        report.bind(
            on_press=self.show_report
        )

        content.add_widget(report)


        # =================================================
        # ABOUT
        # =================================================

        about = ModernButton(
            text="ℹ️   ABOUT",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(65)
        )

        about.bind(
            on_press=self.show_about
        )

        content.add_widget(about)


        # =================================================
        # CREATOR
        # =================================================

        creator = Label(
            text="Created by: Abidullah Omari",
            font_size=dp(15),
            color=(
                0.30,
                0.30,
                0.30,
                1
            ),
            size_hint_y=None,
            height=dp(60)
        )

        content.add_widget(creator)


        scroll.add_widget(content)

        root.add_widget(scroll)


        return root


    # =====================================================
    # HEADER UPDATE
    # =====================================================

    def update_header(
        self,
        *args
    ):

        self.header_rect.pos = (
            self.header.pos
        )

        self.header_rect.size = (
            self.header.size
        )
            # =====================================================
    # DASHBOARD
    # =====================================================

    def show_dashboard(self, instance):

        customers = self.db.get_customers()

        total_debt = 0
        total_paid = 0

        for customer in customers:

            cid = customer[0]

            total_debt += self.db.get_total_debt(cid)

            total_paid += self.db.get_total_payment(cid)

        remaining = total_debt - total_paid

        text = (
            "🏠  DASHBOARD\n\n"
            f"👥 Total Customers: {len(customers)}\n\n"
            f"💰 Total Debt: {total_debt:.2f}\n\n"
            f"💵 Total Paid: {total_paid:.2f}\n\n"
            f"📌 Remaining Debt: {remaining:.2f}"
        )

        self.show_message(
            "Dashboard",
            text
        )


    # =====================================================
    # ADD CUSTOMER
    # =====================================================

    def show_add_customer(self, instance):

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(15)
        )

        name = TextInput(
            hint_text="Customer Name",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        phone = TextInput(
            hint_text="Phone Number",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        address = TextInput(
            hint_text="Address",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        save = ModernButton(
            text="SAVE CUSTOMER",
            size_hint_y=None,
            height=dp(55)
        )

        box.add_widget(name)
        box.add_widget(phone)
        box.add_widget(address)
        box.add_widget(save)

        popup = Popup(
            title="Add Customer",
            content=box,
            size_hint=(0.9, 0.65)
        )

        save.bind(
            on_press=lambda x:
            self.save_customer(
                name,
                phone,
                address,
                popup
            )
        )

        popup.open()


    def save_customer(
        self,
        name,
        phone,
        address,
        popup
    ):

        if not name.text.strip():

            popup.title = "Please enter customer name"

            return

        self.db.add_customer(
            name.text.strip(),
            phone.text.strip(),
            address.text.strip()
        )

        popup.dismiss()

        self.show_message(
            "Success",
            "Customer saved successfully."
        )


    # =====================================================
    # SEARCH CUSTOMERS
    # =====================================================

    def show_customers(self, instance):

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10)
        )

        search_input = TextInput(
            hint_text="Search by name, phone or ID...",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        box.add_widget(search_input)

        scroll = ScrollView(
            do_scroll_x=False
        )

        list_box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        list_box.bind(
            minimum_height=
            list_box.setter("height")
        )

        scroll.add_widget(list_box)

        box.add_widget(scroll)

        close = ModernButton(
            text="CLOSE",
            size_hint_y=None,
            height=dp(50)
        )

        box.add_widget(close)

        popup = Popup(
            title="Customers",
            content=box,
            size_hint=(0.97, 0.93)
        )

        close.bind(
            on_press=popup.dismiss
        )

        popup.open()

        self.refresh_customer_list(
            list_box,
            ""
        )

        search_input.bind(
            text=lambda instance, value:
            self.refresh_customer_list(
                list_box,
                value
            )
        )


    def refresh_customer_list(
        self,
        list_box,
        keyword
    ):

        list_box.clear_widgets()

        keyword = keyword.strip()

        if keyword:

            customers = self.db.search_customers(
                keyword
            )

        else:

            customers = self.db.get_customers()

        if not customers:

            list_box.add_widget(
                Label(
                    text="No customers found.",
                    size_hint_y=None,
                    height=dp(60)
                )
            )

            return

        for customer in customers:

            cid = customer[0]
            name = customer[1]
            phone = customer[2]
            address = customer[3]

            debt = self.db.get_total_debt(cid)
            paid = self.db.get_total_payment(cid)
            remaining = self.db.get_remaining(cid)

            card = BoxLayout(
                orientation="vertical",
                spacing=dp(5),
                padding=dp(10),
                size_hint_y=None,
                height=dp(225)
            )

            info = Label(
                text=(
                    f"ID: {cid}\n"
                    f"Name: {name}\n"
                    f"Phone: {phone}\n"
                    f"Address: {address}\n"
                    f"Total Debt: {debt:.2f}\n"
                    f"Paid: {paid:.2f}\n"
                    f"Remaining: {remaining:.2f}"
                ),
                font_size=dp(14),
                halign="left",
                valign="middle"
            )

            info.bind(
                size=lambda obj, size:
                setattr(
                    obj,
                    "text_size",
                    (size[0], None)
                )
            )

            buttons = BoxLayout(
                spacing=dp(6),
                size_hint_y=None,
                height=dp(48)
            )

            details = ModernButton(
                text="VIEW"
            )

            edit = ModernButton(
                text="EDIT"
            )

            delete = ModernButton(
                text="DELETE"
            )

            details.bind(
                on_press=lambda x,
                customer_id=cid:
                self.show_customer_details(
                    customer_id
                )
            )

            edit.bind(
                on_press=lambda x,
                customer_id=cid:
                self.show_edit_customer(
                    customer_id
                )
            )

            delete.bind(
                on_press=lambda x,
                customer_id=cid:
                self.confirm_delete_customer(
                    customer_id,
                    list_box,
                    keyword
                )
            )

            buttons.add_widget(details)
            buttons.add_widget(edit)
            buttons.add_widget(delete)

            card.add_widget(info)
            card.add_widget(buttons)

            list_box.add_widget(card)


    # =====================================================
    # CUSTOMER DETAILS
    # =====================================================

    def show_customer_details(
        self,
        customer_id
    ):

        customer = self.db.get_customer(
            customer_id
        )

        if not customer:

            self.show_message(
                "Error",
                "Customer not found."
            )

            return

        debt = self.db.get_total_debt(
            customer_id
        )

        paid = self.db.get_total_payment(
            customer_id
        )

        remaining = self.db.get_remaining(
            customer_id
        )

        text = (
            "CUSTOMER DETAILS\n\n"
            f"ID: {customer[0]}\n"
            f"Name: {customer[1]}\n"
            f"Phone: {customer[2]}\n"
            f"Address: {customer[3]}\n\n"
            f"Total Debt: {debt:.2f}\n"
            f"Total Paid: {paid:.2f}\n"
            f"Remaining: {remaining:.2f}"
        )

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(15)
        )

        label = Label(
            text=text,
            font_size=dp(17),
            halign="left",
            valign="middle"
        )

        history = ModernButton(
            text="VIEW HISTORY",
            size_hint_y=None,
            height=dp(50)
        )

        close = ModernButton(
            text="CLOSE",
            size_hint_y=None,
            height=dp(50)
        )

        box.add_widget(label)
        box.add_widget(history)
        box.add_widget(close)

        popup = Popup(
            title="Customer Details",
            content=box,
            size_hint=(0.92, 0.75)
        )

        history.bind(
            on_press=lambda x:
            self.show_history(
                customer_id
            )
        )

        close.bind(
            on_press=popup.dismiss
        )

        popup.open()


    # =====================================================
    # EDIT CUSTOMER
    # =====================================================

    def show_edit_customer(
        self,
        customer_id
    ):

        customer = self.db.get_customer(
            customer_id
        )

        if not customer:

            self.show_message(
                "Error",
                "Customer not found."
            )

            return

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(15)
        )

        name = TextInput(
            text=customer[1] or "",
            multiline=False,
            hint_text="Customer Name",
            size_hint_y=None,
            height=dp(50)
        )

        phone = TextInput(
            text=customer[2] or "",
            multiline=False,
            hint_text="Phone Number",
            size_hint_y=None,
            height=dp(50)
        )

        address = TextInput(
            text=customer[3] or "",
            multiline=False,
            hint_text="Address",
            size_hint_y=None,
            height=dp(50)
        )

        update = ModernButton(
            text="UPDATE CUSTOMER",
            size_hint_y=None,
            height=dp(55)
        )

        box.add_widget(name)
        box.add_widget(phone)
        box.add_widget(address)
        box.add_widget(update)

        popup = Popup(
            title="Edit Customer",
            content=box,
            size_hint=(0.9, 0.65)
        )

        update.bind(
            on_press=lambda x:
            self.update_customer(
                customer_id,
                name,
                phone,
                address,
                popup
            )
        )

        popup.open()


    def update_customer(
        self,
        customer_id,
        name,
        phone,
        address,
        popup
    ):

        if not name.text.strip():

            popup.title = "Enter customer name"

            return

        self.db.update_customer(
            customer_id,
            name.text.strip(),
            phone.text.strip(),
            address.text.strip()
        )

        popup.dismiss()

        self.show_message(
            "Success",
            "Customer updated successfully."
        )


    # =====================================================
    # DELETE CUSTOMER
    # =====================================================

    def confirm_delete_customer(
        self,
        customer_id,
        list_box,
        keyword
    ):

        customer = self.db.get_customer(
            customer_id
        )

        if not customer:

            return

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(15)
        )

        message = Label(
            text=(
                f"Delete customer?\n\n"
                f"Name: {customer[1]}\n"
                f"ID: {customer_id}\n\n"
                "All debts and payments "
                "will also be deleted."
            ),
            halign="center",
            valign="middle"
        )

        buttons = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        yes = ModernButton(
            text="YES, DELETE"
        )

        no = ModernButton(
            text="CANCEL"
        )

        buttons.add_widget(yes)
        buttons.add_widget(no)

        box.add_widget(message)
        box.add_widget(buttons)

        popup = Popup(
            title="Confirm Delete",
            content=box,
            size_hint=(0.9, 0.55)
        )

        no.bind(
            on_press=popup.dismiss
        )

        yes.bind(
            on_press=lambda x:
            self.delete_customer(
                customer_id,
                popup,
                list_box,
                keyword
            )
        )

        popup.open()


    def delete_customer(
        self,
        customer_id,
        popup,
        list_box,
        keyword
    ):

        self.db.delete_customer(
            customer_id
        )

        popup.dismiss()

        self.refresh_customer_list(
            list_box,
            keyword
        )


    # =====================================================
    # ADD DEBT
    # =====================================================

    def show_add_debt(
        self,
        instance
    ):

        if not self.db.get_customers():

            self.show_message(
                "No Customers",
                "Please add a customer first."
            )

            return

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(15)
        )

        customer_id = TextInput(
            hint_text="Customer ID",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(50)
        )

        amount = TextInput(
            hint_text="Debt Amount",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(50)
        )

        description = TextInput(
            hint_text="Description",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        save = ModernButton(
            text="SAVE DEBT",
            size_hint_y=None,
            height=dp(55)
        )

        box.add_widget(customer_id)
        box.add_widget(amount)
        box.add_widget(description)
        box.add_widget(save)

        popup = Popup(
            title="Add Debt",
            content=box,
            size_hint=(0.9, 0.7)
        )

        save.bind(
            on_press=lambda x:
            self.save_debt(
                customer_id,
                amount,
                description,
                popup
            )
        )

        popup.open()


    def save_debt(
        self,
        customer_id,
        amount,
        description,
        popup
    ):

        try:

            cid = int(
                customer_id.text
            )

            value = float(
                amount.text
            )

        except:

            popup.title = (
                "Enter valid information"
            )

            return

        if not self.db.get_customer(cid):

            popup.title = (
                "Customer ID not found"
            )

            return

        if value <= 0:

            popup.title = (
                "Amount must be greater than 0"
            )

            return

        self.db.add_debt(
            cid,
            value,
            description.text.strip()
        )

        popup.dismiss()

        self.show_message(
            "Success",
            "Debt added successfully."
        )


    # =====================================================
    # PAYMENT
    # =====================================================

    def show_payment(
        self,
        instance
    ):

        if not self.db.get_customers():

            self.show_message(
                "No Customers",
                "Please add a customer first."
            )

            return

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(15)
        )

        customer_id = TextInput(
            hint_text="Customer ID",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(50)
        )

        amount = TextInput(
            hint_text="Payment Amount",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(50)
        )

        description = TextInput(
            hint_text="Description",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        save = ModernButton(
            text="SAVE PAYMENT",
            size_hint_y=None,
            height=dp(55)
        )

        box.add_widget(customer_id)
        box.add_widget(amount)
        box.add_widget(description)
        box.add_widget(save)

        popup = Popup(
            title="Make Payment",
            content=box,
            size_hint=(0.9, 0.7)
        )

        save.bind(
            on_press=lambda x:
            self.save_payment(
                customer_id,
                amount,
                description,
                popup
            )
        )

        popup.open()


    def save_payment(
        self,
        customer_id,
        amount,
        description,
        popup
    ):

        try:

            cid = int(
                customer_id.text
            )

            value = float(
                amount.text
            )

        except:

            popup.title = (
                "Enter valid information"
            )

            return

        if not self.db.get_customer(cid):

            popup.title = (
                "Customer ID not found"
            )

            return

        if value <= 0:

            popup.title = (
                "Amount must be greater than 0"
            )

            return

        remaining = self.db.get_remaining(
            cid
        )

        if value > remaining:

            popup.title = (
                "Payment cannot be greater "
                "than remaining debt"
            )

            return

        self.db.add_payment(
            cid,
            value,
            description.text.strip()
        )

        popup.dismiss()

        self.show_message(
            "Success",
            "Payment saved successfully."
        )


    # =====================================================
    # HISTORY
    # =====================================================

    def show_history(
        self,
        customer_id
    ):

        customer = self.db.get_customer(
            customer_id
        )

        if not customer:

            return

        debts = self.db.get_debt_history(
            customer_id
        )

        payments = self.db.get_payment_history(
            customer_id
        )

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12)
        )

        scroll = ScrollView(
            do_scroll_x=False
        )

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        content.bind(
            minimum_height=
            content.setter("height")
        )

        content.add_widget(
            Label(
                text=(
                    f"HISTORY: {customer[1]}"
                ),
                font_size=dp(20),
                bold=True,
                size_hint_y=None,
                height=dp(45)
            )
        )

        content.add_widget(
            Label(
                text="--- DEBTS ---",
                font_size=dp(18),
                bold=True,
                size_hint_y=None,
                height=dp(40)
            )
        )

        if debts:

            for debt in debts:

                content.add_widget(
                    Label(
                        text=(
                            f"💰 {debt[0]:.2f}\n"
                            f"{debt[1]}\n"
                            f"{debt[2]}"
                        ),
                        halign="left",
                        size_hint_y=None,
                        height=dp(75)
                    )
                )

        else:

            content.add_widget(
                Label(
                    text="No debt history.",
                    size_hint_y=None,
                    height=dp(45)
                )
            )

        content.add_widget(
            Label(
                text="--- PAYMENTS ---",
                font_size=dp(18),
                bold=True,
                size_hint_y=None,
                height=dp(40)
            )
        )

        if payments:

            for payment in payments:

                content.add_widget(
                    Label(
                        text=(
                            f"💵 {payment[0]:.2f}\n"
                            f"{payment[1]}\n"
                            f"{payment[2]}"
                        ),
                        halign="left",
                        size_hint_y=None,
                        height=dp(75)
                    )
                )

        else:

            content.add_widget(
                Label(
                    text="No payment history.",
                    size_hint_y=None,
                    height=dp(45)
                )
            )

        scroll.add_widget(content)

        close = ModernButton(
            text="CLOSE",
            size_hint_y=None,
            height=dp(50)
        )

        box.add_widget(scroll)
        box.add_widget(close)

        popup = Popup(
            title="Debt & Payment History",
            content=box,
            size_hint=(0.96, 0.9)
        )

        close.bind(
            on_press=popup.dismiss
        )

        popup.open()


    # =====================================================
    # REPORT
    # =====================================================

    def show_report(
        self,
        instance
    ):

        customers = self.db.get_customers()

        total_debt = 0
        total_paid = 0

        for customer in customers:

            cid = customer[0]

            total_debt += (
                self.db.get_total_debt(cid)
            )

            total_paid += (
                self.db.get_total_payment(cid)
            )

        remaining = (
            total_debt - total_paid
        )

        text = (
            "📊 DEBT REPORT\n\n"
            f"👥 Customers: {len(customers)}\n\n"
            f"💰 Total Debt: {total_debt:.2f}\n\n"
            f"💵 Total Paid: {total_paid:.2f}\n\n"
            f"📌 Remaining: {remaining:.2f}"
        )

        self.show_message(
            "Reports",
            text
        )


    # =====================================================
    # ABOUT
    # =====================================================

    def show_about(
        self,
        instance
    ):

        text = (
            "DEBT MANAGER\n\n"
            "A simple debt management "
            "application.\n\n"
            "Features:\n"
            "• Customer Management\n"
            "• Debt Management\n"
            "• Payment Management\n"
            "• Search\n"
            "• Reports\n"
            "• History\n\n"
            "Created by:\n"
            "Abidullah Omari\n\n"
            "Python + Kivy + SQLite"
        )

        self.show_message(
            "About",
            text
        )


    # =====================================================
    # MESSAGE POPUP
    # =====================================================

    def show_message(
        self,
        title,
        message
    ):

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20)
        )

        label = Label(
            text=message,
            font_size=dp(17),
            halign="center",
            valign="middle"
        )

        close = ModernButton(
            text="OK",
            size_hint_y=None,
            height=dp(50)
        )

        box.add_widget(label)
        box.add_widget(close)

        popup = Popup(
            title=title,
            content=box,
            size_hint=(0.88, 0.65)
        )

        close.bind(
            on_press=popup.dismiss
        )

        popup.open()


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    def on_stop(self):

        self.db.close()


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    DebtManagerApp().run()