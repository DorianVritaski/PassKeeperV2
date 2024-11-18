import tkinter as tk
from tkinter import messagebox, ttk
from sqlalchemy.orm import sessionmaker
from src.modelo.modelo import engine
from src.logica.CRUD import UsuarioCRUD, Contraseniacrud
from tkinter import ttk
from datetime import datetime

# Configurar sesión de SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()
usuario_crud = UsuarioCRUD(session)
contrasenia_crud = Contraseniacrud(session)

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
                self.root.destroy()  # Cierra la ventana de login
                GestionContrasenasWindow(sesion.id_usuario)  # Pasa el id_usuario al abrir la ventana de contraseñas
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
        self.window.geometry("300x300")

        # Campos para registrar un nuevo usuario
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

        self.label_rol = tk.Label(self.window, text="Rol (ejemplo: admin, usuario):")
        self.label_rol.pack(pady=5)
        self.entry_rol = tk.Entry(self.window, width=30)
        self.entry_rol.pack(pady=5)

        self.button_register = tk.Button(self.window, text="Registrar", command=self.register_user)
        self.button_register.pack(pady=10)

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


class GestionContrasenasWindow:
    def __init__(self, usuario_id):
        self.usuario_id = usuario_id  # Recibe el id del usuario
        self.root = tk.Tk()
        self.root.title("Gestión de Contraseñas")
        self.root.geometry("800x400")  # Ajusté el tamaño para más espacio

        # Tabla de contraseñas
        self.tree = ttk.Treeview(self.root, columns=(
            "ID", "Servicio", "Usuario", "Contraseña Encriptada", "Fecha de Creación", "Última Modificación", "Nota"),
                                 show="headings")

        # Definir encabezados de las columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Servicio", text="Servicio")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Contraseña Encriptada", text="Contraseña Encriptada")
        self.tree.heading("Fecha de Creación", text="Fecha de Creación")
        self.tree.heading("Última Modificación", text="Última Modificación")
        self.tree.heading("Nota", text="Nota")

        # Ajustar el ancho de las columnas
        self.tree.column("ID", width=50)
        self.tree.column("Servicio", width=150)
        self.tree.column("Usuario", width=150)
        self.tree.column("Contraseña Encriptada", width=150)
        self.tree.column("Fecha de Creación", width=150)
        self.tree.column("Última Modificación", width=150)
        self.tree.column("Nota", width=200)

        # Mostrar la tabla
        self.tree.pack(fill="both", expand=True)

        # Botones
        frame_botones = tk.Frame(self.root)
        frame_botones.pack()

        tk.Button(frame_botones, text="Agregar", command=self.agregar_contrasena).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Editar", command=self.editar_contrasena).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Eliminar", command=self.eliminar_contrasena).pack(side="left", padx=10)

        # Cargar contraseñas
        self.cargar_contrasenas()

        self.root.mainloop()

    def cargar_contrasenas(self):
        """Carga las contraseñas del usuario desde la base de datos"""
        # Limpiar la tabla antes de cargar datos
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener contraseñas de la base de datos
        contrasenas = contrasenia_crud.obtener_contrasenias_usuario(self.usuario_id)

        # Insertar los datos en la tabla
        for contrasenia in contrasenas:
            self.tree.insert("", "end", values=(
                contrasenia.id_contrasenia,
                contrasenia.servicio,
                contrasenia.nombre_usuario_servicio,
                contrasenia.contrasenia_encriptada,  # Columna de Contraseña Encriptada
                contrasenia.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if contrasenia.fecha_creacion else "",
                # Fecha de creación
                contrasenia.ultima_modificacion.strftime(
                    "%Y-%m-%d %H:%M:%S") if contrasenia.ultima_modificacion else "",  # Última modificación
                contrasenia.nota or ""  # Nota (si no hay nota, colocar vacío)
            ))

    def agregar_contrasena(self):
        def guardar_contrasena():
            servicio = entry_servicio.get()
            nombre_usuario_servicio = entry_usuario.get()
            contrasenia = entry_contrasenia.get()
            nota = text_nota.get("1.0", tk.END).strip()

            if not servicio or not nombre_usuario_servicio or not contrasenia:
                messagebox.showwarning("Advertencia", "Por favor, complete todos los campos obligatorios.")
                return

            try:
                # Crear la nueva contraseña en la base de datos
                contrasenia_crud.create_contrasenia(
                    id_usuario=self.usuario_id,
                    servicio=servicio,
                    nombre_usuario_servicio=nombre_usuario_servicio,
                    contrasenia_encriptada=contrasenia,  # Aquí deberías encriptar la contraseña
                    nota=nota
                )
                messagebox.showinfo("Éxito", "Contraseña agregada correctamente.")
                self.cargar_contrasenas()
                ventana_agregar.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar la contraseña: {e}")

        # Crear una nueva ventana para añadir una contraseña
        ventana_agregar = tk.Toplevel(self.root)
        ventana_agregar.title("Agregar Contraseña")
        ventana_agregar.geometry("400x400")

        # Campos de entrada
        tk.Label(ventana_agregar, text="Servicio:").pack(pady=5)
        entry_servicio = tk.Entry(ventana_agregar, width=30)
        entry_servicio.pack(pady=5)

        tk.Label(ventana_agregar, text="Usuario del Servicio:").pack(pady=5)
        entry_usuario = tk.Entry(ventana_agregar, width=30)
        entry_usuario.pack(pady=5)

        tk.Label(ventana_agregar, text="Contraseña:").pack(pady=5)
        entry_contrasenia = tk.Entry(ventana_agregar, width=30, show="*")
        entry_contrasenia.pack(pady=5)

        tk.Label(ventana_agregar, text="Nota (opcional):").pack(pady=5)
        text_nota = tk.Text(ventana_agregar, height=5, width=40)
        text_nota.pack(pady=5)

        # Botón para guardar
        tk.Button(ventana_agregar, text="Guardar", command=guardar_contrasena).pack(pady=10)
        pass

    def editar_contrasena(self):
        # Implementar ventana para editar contraseña seleccionada
        pass

    def eliminar_contrasena(self):
        try:
            # Verificar si hay una contraseña seleccionada
            seleccion = self.tree.focus()  # Obtener la selección en la tabla
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor, seleccione una contraseña para eliminar.")
                return

            # Obtener datos de la contraseña seleccionada
            item_seleccionado = self.tree.item(seleccion)
            contrasena_id = item_seleccionado["values"][0]  # Suponiendo que el ID es la primera columna

            # Confirmación
            confirmacion = messagebox.askyesno("Confirmar eliminación",
                                               "¿Está seguro de que desea eliminar esta contraseña?")
            if not confirmacion:
                return

            # Eliminar contraseña en la base de datos
            try:
                contrasenia_crud.delete_contrasenia(contrasena_id)
                messagebox.showinfo("Éxito", "La contraseña ha sido eliminada correctamente.")
                self.cargar_contrasenas()  # Refrescar la tabla después de eliminar
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la contraseña: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"Hubo un problema al intentar eliminar la contraseña: {e}")
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
