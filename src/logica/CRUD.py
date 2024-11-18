from pkg_resources import non_empty_lines
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from src.modelo.modelo import Usuario, engine, Sesion, Etiqueta, ContraseniaEtiqueta
from src.config import sessionmaker
from datetime import datetime
from src.modelo.modelo import Contrasenia  # Asegúrate de importar correctamente el modelo Contrasenia

class UsuarioCRUD:
    def __init__(self, session):
        self.session = session

    def create_usuario(self, nombre_usuario, email, password_hash, rol):
        """Crear un nuevo usuario"""
        try:
            nuevo_usuario = Usuario(
                nombre_usuario=nombre_usuario,
                email=email,
                password_hash=password_hash,
                rol=rol
            )
            self.session.add(nuevo_usuario)
            self.session.commit()
            return nuevo_usuario
        except IntegrityError:
            self.session.rollback()  # Rollback en caso de error (por ejemplo, email duplicado)
            raise Exception("El email ya está registrado.")

    def iniciar_sesion(self, email, password_hash):
        """Iniciar sesión con un usuario basado en el correo y la contraseña proporcionados"""
        usuario = self.session.query(Usuario).filter_by(email=email).first()
        if usuario and usuario.password_hash == password_hash:
            # Aquí podrías hacer cualquier lógica adicional, como registrar la sesión
            # Crear una sesión para el usuario
            sesion = Sesion(id_usuario=usuario.id_usuario, fecha_inicio=datetime.now())
            self.session.add(sesion)
            self.session.commit()
            return sesion  # Retornar la sesión creada
        return None

    def get_usuario_by_id(self, id_usuario):
        """
        Obtiene un usuario específico por su ID.
        """
        return self.session.query(Usuario).filter_by(id_usuario=id_usuario).first()

    def get_usuario_by_email(self, email):
        """
        Obtiene un usuario específico por su email.
        """
        return self.session.query(Usuario).filter_by(email=email).first()

    def update_usuario(self, id_usuario, nombre_usuario=None, email=None, password_hash=None, rol=None):
        """
        Actualiza la información de un usuario.
        """
        usuario = self.get_usuario_by_id(id_usuario)
        if usuario:
            if nombre_usuario:
                usuario.nombre_usuario = nombre_usuario
            if email:
                usuario.email = email
            if password_hash:
                usuario.password_hash = password_hash
            if rol:
                usuario.rol = rol
            self.session.commit()
        return usuario

    def delete_usuario(self, id_usuario):
        """
        Elimina un usuario de la base de datos.
        """
        usuario = self.get_usuario_by_id(id_usuario)
        if usuario:
            self.session.delete(usuario)
            self.session.commit()
        return usuario

    def cerrar_sesion(self, id_sesion):
        """Cerrar sesión de un usuario"""
        # Buscar la sesión por su ID
        sesion = self.session.query(Sesion).filter_by(id_sesion=id_sesion).first()
        if sesion:
            # Establecer la fecha de cierre de la sesión
            sesion.fecha_fin = datetime.now()
            self.session.commit()
            return sesion
        else:
            raise Exception("Sesión no encontrada")

class Contraseniacrud:
    def __init__(self, session):
        self.session = session

    def create_contrasenia(self, servicio, nombre_usuario_servicio, contrasenia_encriptada, id_usuario, nota=None):
        """Crear una nueva contrasenia en la base de datos"""
        # Verificar si ya existe una contraseña para este servicio y usuario
       # existing_contrasenia = self.session.query(Contrasenia).filter_by(servicio=servicio, id_usuario=id_usuario).first()
       # if existing_contrasenia:
        #    raise Exception("Ya existe una contraseña para este servicio y usuario")

        contrasenia = Contrasenia(
            servicio=servicio,
            nombre_usuario_servicio=nombre_usuario_servicio,
            contrasenia_encriptada=contrasenia_encriptada,
            fecha_creacion=datetime.now(),
            #ultima_modificacion=datetime.now(),
            ultima_modificacion=None,
            id_usuario=id_usuario,
            nota=nota
        )
        self.session.add(contrasenia)
        self.session.commit()
        return contrasenia

    def get_contrasenias_by_user(self, id_usuario):
        """Obtener todas las contraseñas asociadas a un usuario"""
        return self.session.query(Contrasenia).filter_by(id_usuario=id_usuario).all()

    def editar_contrasena(self, id_contrasenia, contrasenia_encriptada=None, nota=None):
        """Actualizar los campos de una contrasenia"""
        contrasenia = self.session.query(Contrasenia).filter_by(id_contrasenia=id_contrasenia).first()
        if not contrasenia:
            raise Exception("La contraseña no existe")

        if contrasenia_encriptada:
            contrasenia.contrasenia_encriptada = contrasenia_encriptada
        if nota:
            contrasenia.nota = nota

        contrasenia.ultima_modificacion = datetime.now()
        self.session.commit()
        return contrasenia

    def delete_contrasenia(self, id_contrasenia):
        """Eliminar una contrasenia"""
        contrasenia = self.session.query(Contrasenia).filter_by(id_contrasenia=id_contrasenia).first()
        if not contrasenia:
            raise Exception("La contraseña no existe")

        self.session.delete(contrasenia)
        self.session.commit()

    def obtener_contrasenias_usuario(self, usuario_id):
        try:
            contrasenas = self.session.query(Contrasenia).filter(Contrasenia.id_usuario == usuario_id).all()
            return contrasenas
        except Exception as e:
            print(f"Error al obtener contraseñas: {e}")
            return []


class EtiquetaCRUD:
    def __init__(self, session):
        self.session = session

    def create_etiqueta(self, nombre):
        if not nombre:
            raise ValueError("El nombre de la etiqueta no puede ser vacío.")
        etiqueta = Etiqueta(nombre=nombre)
        self.session.add(etiqueta)
        self.session.commit()
        return etiqueta

    def get_etiqueta(self, id_etiqueta):
        etiqueta = self.session.query(Etiqueta).filter(Etiqueta.id_etiqueta == id_etiqueta).first()
        if not etiqueta:
            raise ValueError(f"Etiqueta con id {id_etiqueta} no encontrada.")
        return etiqueta

    def update_etiqueta(self, id_etiqueta, **kwargs):
        etiqueta = self.get_etiqueta(id_etiqueta)
        if etiqueta:
            for key, value in kwargs.items():
                setattr(etiqueta, key, value)
            self.session.commit()
            return etiqueta
        else:
            raise ValueError(f"No se pudo actualizar. Etiqueta con id {id_etiqueta} no encontrada.")

    def delete_etiqueta(self, id_etiqueta):
        etiqueta = self.get_etiqueta(id_etiqueta)
        if etiqueta:
            self.session.delete(etiqueta)
            self.session.commit()
            return etiqueta
        else:
            raise ValueError(f"No se pudo eliminar. Etiqueta con id {id_etiqueta} no encontrada.")

class SesionCRUD:
    def __init__(self, session):
        self.session = session

    def create_sesion(self, id_usuario, ip):
        sesion = Sesion(
            id_usuario=id_usuario,
            fecha_inicio=datetime.now(),
            ip=ip
        )
        self.session.add(sesion)
        self.session.commit()
        return sesion

    def get_sesion(self, id_sesion):
        return self.session.query(Sesion).filter(Sesion.id_sesion == id_sesion).first()

    def update_sesion(self, id_sesion, **kwargs):
        sesion = self.get_sesion(id_sesion)
        if sesion:
            for key, value in kwargs.items():
                setattr(sesion, key, value)
            self.session.commit()
        return sesion

    def delete_sesion(self, id_sesion):
        sesion = self.get_sesion(id_sesion)
        if sesion:
            self.session.delete(sesion)
            self.session.commit()
        return sesion

class ContraseniaEtiquetaCRUD:
    def __init__(self, session):
        self.session = session

    def create_contrasenia_etiqueta(self, id_contrasenia, id_etiqueta):
        relacion = ContraseniaEtiqueta(
            id_contrasenia=id_contrasenia,  # Corrige aquí el parámetro
            id_etiqueta=id_etiqueta
        )
        self.session.add(relacion)
        self.session.commit()
        return relacion

    def delete_contrasenia_etiqueta(self, id_contrasenia_etiqueta):
        relacion = self.session.query(ContraseniaEtiqueta).filter(ContraseniaEtiqueta.id_contrasenia_etiqueta == id_contrasenia_etiqueta).first()
        if relacion:
            self.session.delete(relacion)
            self.session.commit()
        return relacion
