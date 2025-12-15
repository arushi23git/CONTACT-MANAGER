import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import re
from datetime import datetime
from pathlib import Path


class ContactManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Data storage: store contacts.json in the same folder as this script
        app_dir = Path(__file__).parent.resolve()
        self.data_file = app_dir / "contacts.json"
        # create file if not exists (avoid read errors)
        if not self.data_file.exists():
            try:
                self.data_file.write_text("[]", encoding="utf-8")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create data file: {e}")

        self.contacts = self.load_contacts()

        self.setup_ui()
        self.refresh_contact_list()

    def setup_ui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="📞 Contact Manager",
                                font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Add contact section
        self.create_add_contact_frame(main_frame)

        # Search and filter section
        self.create_search_frame(main_frame)

        # Contact list section
        self.create_contact_list_frame(main_frame)

        # Action buttons
        self.create_action_buttons(main_frame)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

    def create_add_contact_frame(self, parent):
        # Add contact frame
        add_frame = ttk.LabelFrame(parent, text="Add New Contact", padding="15")
        add_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        add_frame.columnconfigure(1, weight=1)
        add_frame.columnconfigure(3, weight=1)

        # First row: Name and Phone
        ttk.Label(add_frame, text="Name*:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.name_entry = ttk.Entry(add_frame, width=25)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 15))

        ttk.Label(add_frame, text="Phone*:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.phone_entry = ttk.Entry(add_frame, width=20)
        self.phone_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))

        # Second row: Email and Address
        ttk.Label(add_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.email_entry = ttk.Entry(add_frame, width=25)
        self.email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 15), pady=(10, 0))

        ttk.Label(add_frame, text="Address:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.address_entry = ttk.Entry(add_frame, width=30)
        self.address_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Add button
        add_btn = ttk.Button(add_frame, text="Add Contact", command=self.add_contact)
        add_btn.grid(row=2, column=0, columnspan=4, pady=(15, 0))

        # Bind Enter key to add contact
        self.name_entry.bind('<Return>', lambda e: self.add_contact())
        self.phone_entry.bind('<Return>', lambda e: self.add_contact())
        self.email_entry.bind('<Return>', lambda e: self.add_contact())
        self.address_entry.bind('<Return>', lambda e: self.add_contact())

    def create_search_frame(self, parent):
        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 15))

        ttk.Label(search_frame, text="Search Contacts", font=('Arial', 12, 'bold')).pack(anchor=tk.W)

        # Search entry
        search_entry_frame = ttk.Frame(search_frame)
        search_entry_frame.pack(fill=tk.X, pady=(5, 10))

        ttk.Label(search_entry_frame, text="🔍").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_entry_frame)
        self.search_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_contacts())

        # Search options
        self.search_option = tk.StringVar(value="name")
        ttk.Radiobutton(search_frame, text="Search by Name",
                        variable=self.search_option, value="name",
                        command=self.search_contacts).pack(anchor=tk.W)
        ttk.Radiobutton(search_frame, text="Search by Phone",
                        variable=self.search_option, value="phone",
                        command=self.search_contacts).pack(anchor=tk.W)
        ttk.Radiobutton(search_frame, text="Search All Fields",
                        variable=self.search_option, value="all",
                        command=self.search_contacts).pack(anchor=tk.W)

        # Statistics
        self.stats_label = ttk.Label(search_frame, text="", font=('Arial', 9))
        self.stats_label.pack(anchor=tk.W, pady=(15, 0))

        # Clear search button
        ttk.Button(search_frame, text="Clear Search",
                   command=self.clear_search).pack(anchor=tk.W, pady=(10, 0))

    def create_contact_list_frame(self, parent):
        # Contact list frame
        list_frame = ttk.LabelFrame(parent, text="Contact List", padding="10")
        list_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview for contacts
        columns = ("Name", "Phone", "Email", "Address", "Added")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=18)

        # Define column headings and widths
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone Number")
        self.tree.heading("Email", text="Email Address")
        self.tree.heading("Address", text="Address")
        self.tree.heading("Added", text="Date Added")

        self.tree.column("Name", width=150)
        self.tree.column("Phone", width=120)
        self.tree.column("Email", width=180)
        self.tree.column("Address", width=200)
        self.tree.column("Added", width=100)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid scrollbars and treeview
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind double-click to view contact details
        self.tree.bind('<Double-1>', self.view_contact_details)

    def create_action_buttons(self, parent):
        # Action buttons frame
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=(15, 0))

        ttk.Button(btn_frame, text="View Details",
                   command=self.view_contact_details).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Edit Contact",
                   command=self.edit_contact).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Delete Contact",
                   command=self.delete_contact).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Export Contacts",
                   command=self.export_contacts).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Clear All",
                   command=self.clear_all_contacts).pack(side=tk.LEFT)

    def validate_email(self, email):
        """Validate email format"""
        if not email:
            return True  # Email is optional
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """Validate phone number format"""
        if not phone:
            return False
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10

    def add_contact(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        # Validation
        if not name:
            messagebox.showwarning("Warning", "Name is required.")
            self.name_entry.focus()
            return

        if not phone:
            messagebox.showwarning("Warning", "Phone number is required.")
            self.phone_entry.focus()
            return

        if not self.validate_phone(phone):
            messagebox.showerror("Error", "Please enter a valid phone number (at least 10 digits).")
            self.phone_entry.focus()
            return

        if email and not self.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            self.email_entry.focus()
            return

        # Check for duplicate phone numbers
        for contact in self.contacts:
            if not contact.get('deleted', False) and contact['phone'] == phone:
                messagebox.showwarning("Warning", "A contact with this phone number already exists.")
                return

        # Create new contact
        contact = {
            "id": self.get_next_id(),
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "date_modified": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.contacts.append(contact)
        self.save_contacts()
        self.refresh_contact_list()
        self.clear_form()

        self.status_var.set(f"Contact added: {name}")

    def get_next_id(self):
        """Generate next available ID"""
        if not self.contacts:
            return 1
        return max(contact.get('id', 0) for contact in self.contacts) + 1

    def clear_form(self):
        """Clear all input fields"""
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.name_entry.focus()

    def get_selected_contact(self):
        """Get the currently selected contact"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a contact.")
            return None

        item = self.tree.item(selection[0])
        contact_name = item['values'][0]
        contact_phone = item['values'][1]

        for contact in self.contacts:
            if (contact['name'] == contact_name and
                    contact['phone'] == contact_phone and
                    not contact.get('deleted', False)):
                return contact
        return None

    def view_contact_details(self, event=None):
        """Show detailed view of selected contact"""
        contact = self.get_selected_contact()
        if not contact:
            return

        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Contact Details - {contact['name']}")
        details_window.geometry("450x350")
        details_window.transient(self.root)
        details_window.grab_set()

        # Center the window
        details_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

        # Main frame
        main_frame = ttk.Frame(details_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Contact Information",
                  font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Contact details
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("Name:", contact['name']),
            ("Phone:", contact['phone']),
            ("Email:", contact['email'] or "Not provided"),
            ("Address:", contact['address'] or "Not provided"),
            ("Date Added:", contact['date_added']),
            ("Last Modified:", contact.get('date_modified', contact['date_added']))
        ]

        for i, (label, value) in enumerate(fields):
            ttk.Label(details_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10)
            )
            ttk.Label(details_frame, text=str(value), wraplength=250).grid(
                row=i, column=1, sticky=tk.W, pady=5
            )

        # Close button
        ttk.Button(main_frame, text="Close",
                   command=details_window.destroy).pack(pady=(20, 0))

    def edit_contact(self):
        """Edit selected contact"""
        contact = self.get_selected_contact()
        if not contact:
            return

        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Contact - {contact['name']}")
        edit_window.geometry("500x300")
        edit_window.transient(self.root)
        edit_window.grab_set()

        # Center the window
        edit_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

        # Main frame
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Title
        ttk.Label(main_frame, text="Edit Contact",
                  font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Form fields
        ttk.Label(main_frame, text="Name*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        name_entry = ttk.Entry(main_frame, width=40)
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        name_entry.insert(0, contact['name'])

        ttk.Label(main_frame, text="Phone*:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        phone_entry = ttk.Entry(main_frame, width=40)
        phone_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        phone_entry.insert(0, contact['phone'])

        ttk.Label(main_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        email_entry = ttk.Entry(main_frame, width=40)
        email_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        email_entry.insert(0, contact['email'])

        ttk.Label(main_frame, text="Address:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        address_entry = ttk.Entry(main_frame, width=40)
        address_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        address_entry.insert(0, contact['address'])

        def save_changes():
            new_name = name_entry.get().strip()
            new_phone = phone_entry.get().strip()
            new_email = email_entry.get().strip()
            new_address = address_entry.get().strip()

            # Validation
            if not new_name:
                messagebox.showwarning("Warning", "Name is required.")
                return

            if not new_phone:
                messagebox.showwarning("Warning", "Phone number is required.")
                return

            if not self.validate_phone(new_phone):
                messagebox.showerror("Error", "Please enter a valid phone number.")
                return

            if new_email and not self.validate_email(new_email):
                messagebox.showerror("Error", "Please enter a valid email address.")
                return

            # Check for duplicate phone (excluding current contact)
            for c in self.contacts:
                if (not c.get('deleted', False) and
                        c['id'] != contact['id'] and
                        c['phone'] == new_phone):
                    messagebox.showwarning("Warning", "A contact with this phone number already exists.")
                    return

            # Update contact
            contact['name'] = new_name
            contact['phone'] = new_phone
            contact['email'] = new_email
            contact['address'] = new_address
            contact['date_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")

            self.save_contacts()
            self.refresh_contact_list()
            self.status_var.set(f"Contact updated: {new_name}")
            edit_window.destroy()

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(btn_frame, text="Save Changes", command=save_changes).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT)

    def delete_contact(self):
        """Delete selected contact"""
        contact = self.get_selected_contact()
        if not contact:
            return

        if messagebox.askyesno("Confirm Delete",
                               f"Are you sure you want to delete the contact '{contact['name']}'?\n\nThis action cannot be undone."):
            contact['deleted'] = True
            self.save_contacts()
            self.refresh_contact_list()
            self.status_var.set(f"Contact deleted: {contact['name']}")

    def search_contacts(self):
        """Search contacts based on current search criteria"""
        self.refresh_contact_list()

    def clear_search(self):
        """Clear search field and show all contacts"""
        self.search_entry.delete(0, tk.END)
        self.refresh_contact_list()

    def refresh_contact_list(self):
        """Refresh the contact list display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get search criteria
        search_term = self.search_entry.get().lower()
        search_option = self.search_option.get()

        # Filter contacts
        filtered_contacts = []
        for contact in self.contacts:
            if contact.get('deleted', False):
                continue

            # Apply search filter
            if search_term:
                if search_option == "name" and search_term not in contact['name'].lower():
                    continue
                elif search_option == "phone" and search_term not in contact['phone']:
                    continue
                elif search_option == "all":
                    if not any(search_term in str(contact.get(field, '')).lower()
                               for field in ['name', 'phone', 'email', 'address']):
                        continue

            filtered_contacts.append(contact)

        # Sort contacts by name
        filtered_contacts.sort(key=lambda x: x['name'].lower())

        # Populate tree
        for contact in filtered_contacts:
            date_added = contact['date_added'].split()[0]  # Just the date part
            self.tree.insert("", tk.END, values=(
                contact['name'],
                contact['phone'],
                contact['email'] or "",
                contact['address'] or "",
                date_added
            ))

        # Update statistics
        total_contacts = len([c for c in self.contacts if not c.get('deleted', False)])
        showing_contacts = len(filtered_contacts)

        if search_term:
            self.stats_label.config(text=f"Showing {showing_contacts} of {total_contacts} contacts")
        else:
            self.stats_label.config(text=f"Total contacts: {total_contacts}")

    def export_contacts(self):
        """Export contacts to a text file"""
        if not any(not c.get('deleted', False) for c in self.contacts):
            messagebox.showinfo("Info", "No contacts to export.")
            return

        try:
            filename = f"contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("CONTACT LIST EXPORT\n")
                f.write("=" * 50 + "\n\n")

                active_contacts = [c for c in self.contacts if not c.get('deleted', False)]
                active_contacts.sort(key=lambda x: x['name'].lower())

                for i, contact in enumerate(active_contacts, 1):
                    f.write(f"{i}. {contact['name']}\n")
                    f.write(f"   Phone: {contact['phone']}\n")
                    if contact['email']:
                        f.write(f"   Email: {contact['email']}\n")
                    if contact['address']:
                        f.write(f"   Address: {contact['address']}\n")
                    f.write(f"   Added: {contact['date_added']}\n")
                    f.write("\n")

                f.write(f"\nTotal contacts exported: {len(active_contacts)}\n")
                f.write(f"Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            messagebox.showinfo("Success", f"Contacts exported to {filename}")
            self.status_var.set(f"Contacts exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export contacts: {e}")

    def clear_all_contacts(self):
        """Clear all contacts with confirmation"""
        active_count = len([c for c in self.contacts if not c.get('deleted', False)])
        if active_count == 0:
            messagebox.showinfo("Info", "No contacts to clear.")
            return

        if messagebox.askyesno("Confirm Clear All",
                               f"Are you sure you want to delete all {active_count} contacts?\n\nThis action cannot be undone."):
            for contact in self.contacts:
                contact['deleted'] = True
            self.save_contacts()
            self.refresh_contact_list()
            self.status_var.set(f"All contacts cleared ({active_count} contacts deleted)")

    def load_contacts(self):
        """Load contacts from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load contacts: {e}")
            return []

    def save_contacts(self):
        """Save contacts to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.contacts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save contacts: {e}")


def main():
    root = tk.Tk()
    app = ContactManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
