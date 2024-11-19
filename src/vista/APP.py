import tkinter as tk
import secrets
import string
import pyperclip  # Librería para copiar al portapapeles
import json
import os
from tkinter import messagebox, ttk, filedialog
from sqlalchemy.orm import sessionmaker
from src.modelo.modelo import engine
from src.logica.CRUD import UsuarioCRUD, Contraseniacrud

# Configurar sesión de SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()
usuario_crud = UsuarioCRUD(session)

# Archivo para guardar contraseñas generadas
PASSWORDS_FILE = 'generated_passwords.json'

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Inicio de Sesión")
        self.root.geometry("300x250")

        # Etiquetas y campos de entrada
        self.label_email = tk.Label(root, text="Correo Electrónico:")
        self.label_email.pack(pady=5)
        self.entry_email = tk.Entry(root, width=30)
        self.entry_email.pack(pady=5)

        self.label_password = tk.Label(root, text="Contraseña:")
        self.label_password.pack(pady=5)
        self.entry_password = tk.Entry(root, width=30, show="*")
        self.entry_password.pack(pady=5)

        # Botones
        self.button_login = tk.Button(root, text="Iniciar Sesión", command=self.login)
        self.button_login.pack(pady=10)

        self.button_register = tk.Button(root, text="Crear Usuario", command=self.open_register_window)
        self.button_register.pack(pady=5)

    def login(self):
        email = self.entry_email.get()
        password = self.entry_password.get()

        if not email or not password:
            messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.")
            return

        try:
            sesion = usuario_crud.iniciar_sesion(email, password)
            if sesion:
                messagebox.showinfo("Éxito", "Inicio de sesión exitoso.")
                self.root.destroy()
            else:
                messagebox.showerror("Error", "Correo o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ha ocurrido un error: {e}")

    def open_register_window(self):
        RegisterWindow(self.root)

class RegisterWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Registrar Usuario")
        self.window.geometry("300x350")

        self.label_username = tk.Label(self.window, text="Nombre de Usuario:")
        self.label_username.pack(pady=5)
        self.entry_username = tk.Entry(self.window, width=30)
        self.entry_username.pack(pady=5)

        self.label_email = tk.Label(self.window, text="Correo Electrónico:")
        self.label_email.pack(pady=5)
        self.entry_email = tk.Entry(self.window, width=30)
        self.entry_email.pack(pady=5)

        self.label_password = tk.Label(self.window, text="Contraseña:")
        self.label_password.pack(pady=5)
        self.entry_password = tk.Entry(self.window, width=30, show="*")
        self.entry_password.pack(pady=5)

        # Botón para generar contraseña segura
        self.button_generate_password = tk.Button(self.window, text="Generar Contraseña", command=self.open_password_generator)
        self.button_generate_password.pack(pady=5)

        self.label_rol = tk.Label(self.window, text="Rol (admin/usuario):")
        self.label_rol.pack(pady=5)
        self.entry_rol = tk.Entry(self.window, width=30)
        self.entry_rol.pack(pady=5)

        self.button_register = tk.Button(self.window, text="Registrar", command=self.register_user)
        self.button_register.pack(pady=10)

    def open_password_generator(self):
        PasswordGeneratorWindow(self.window, self.entry_password)

    def register_user(self):
        nombre_usuario = self.entry_username.get()
        email = self.entry_email.get()
        password = self.entry_password.get()
        rol = self.entry_rol.get()

        if not nombre_usuario or not email or not password or not rol:
            messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.")
            return

        try:
            usuario_crud.create_usuario(nombre_usuario, email, password, rol)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el usuario: {e}")

class PasswordGeneratorWindow:
    def __init__(self, parent, target_entry):
        self.target_entry = target_entry
        self.window = tk.Toplevel(parent)
        self.window.title("Generar Contraseña Segura")
        self.window.geometry("350x250")

        tk.Label(self.window, text="Longitud de la contraseña:").pack(pady=5)
        self.entry_length = tk.Entry(self.window, width=5)
        self.entry_length.insert(0, "12")  # Valor por defecto
        self.entry_length.pack(pady=5)

        self.button_generate = tk.Button(self.window, text="Generar", command=self.generate_password)
        self.button_generate.pack(pady=5)

        self.generated_password = tk.StringVar()
        self.label_password = tk.Label(self.window, textvariable=self.generated_password, wraplength=250, fg="blue")
        self.label_password.pack(pady=5)

        # Nuevos botones para copiar y guardar
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        self.button_copy = tk.Button(button_frame, text="Copiar al Portapapeles", command=self.copy_to_clipboard)
        self.button_copy.pack(side=tk.LEFT, padx=5)

        self.button_use = tk.Button(button_frame, text="Usar en Formulario", command=self.use_password)
        self.button_use.pack(side=tk.LEFT, padx=5)

        self.button_save = tk.Button(button_frame, text="Guardar Contraseña", command=self.save_password)
        self.button_save.pack(side=tk.LEFT, padx=5)

    def generate_password(self):
        try:
            length = int(self.entry_length.get())
            if length < 6:
                messagebox.showwarning("Advertencia", "La contraseña debe tener al menos 6 caracteres.")
                return
            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(characters) for _ in range(length))
            self.generated_password.set(password)
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un valor numérico válido para la longitud.")

    def copy_to_clipboard(self):
        password = self.generated_password.get()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Éxito", "Contraseña copiada al portapapeles.")
        else:
            messagebox.showwarning("Advertencia", "Primero genere una contraseña.")

    def use_password(self):
        password = self.generated_password.get()
        if password:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, password)
            messagebox.showinfo("Éxito", "Contraseña insertada en el formulario.")
        else:
            messagebox.showwarning("Advertencia", "Primero genere una contraseña.")

    def save_password(self):
        password = self.generated_password.get()
        if password:
            # Guardar la contraseña en un archivo JSON
            try:
                # Si el archivo no existe, inicializa una lista vacía
                if not os.path.exists(PASSWORDS_FILE):
                    with open(PASSWORDS_FILE, 'w') as f:
                        json.dump([], f)

                # Leer contraseñas existentes
                with open(PASSWORDS_FILE, 'r') as f:
                    passwords = json.load(f)

                # Agregar nueva contraseña
                passwords.append(password)

                # Guardar contraseñas actualizadas
                with open(PASSWORDS_FILE, 'w') as f:
                    json.dump(passwords, f, indent=4)

                messagebox.showinfo("Éxito", "Contraseña guardada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la contraseña: {e}")
        else:
            messagebox.showwarning("Advertencia", "Primero genere una contraseña.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()