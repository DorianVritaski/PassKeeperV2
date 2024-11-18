from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

# Tabla de asociación para la relación muchos a muchos entre Contraseña y Etiqueta
class ContraseniaEtiqueta(Base):
    __tablename__ = 'contrasenia_etiqueta'
    id_contrasenia_etiqueta = Column(Integer, primary_key=True)
    id_contrasenia = Column(Integer, ForeignKey('contrasenias.id_contrasenia'))
    id_etiqueta = Column(Integer, ForeignKey('etiquetas.id_etiqueta'))


class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(Integer, primary_key=True)
    nombre_usuario = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.now)

    contrasenias = relationship("Contrasenia", back_populates="usuario")
    sesiones = relationship("Sesion", back_populates="usuario")


class Contrasenia(Base):
    __tablename__ = 'contrasenias'

    id_contrasenia = Column(Integer, primary_key=True)
    servicio = Column(String, nullable=False)
    nombre_usuario_servicio = Column(String, nullable=False)
    contrasenia_encriptada = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    #ultima_modificacion = Column(DateTime, onupdate=datetime.now)
    ultima_modificacion = Column(DateTime, nullable=True)
    nota = Column(String)

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'))
    usuario = relationship("Usuario", back_populates="contrasenias")
    etiquetas = relationship("Etiqueta", secondary='contrasenia_etiqueta', back_populates="contrasenias")


class Etiqueta(Base):
    __tablename__ = 'etiquetas'

    id_etiqueta = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    contrasenias = relationship("Contrasenia", secondary='contrasenia_etiqueta', back_populates="etiquetas")


class Sesion(Base):
    __tablename__ = 'sesiones'

    id_sesion = Column(Integer, primary_key=True)
    fecha_inicio = Column(DateTime, default=datetime.now)
    fecha_fin = Column(DateTime, nullable=True)
    ip = Column(String)

    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'))
    usuario = relationship("Usuario", back_populates="sesiones")


# Configuración de la base de datos para pruebas (en memoria)
engine = create_engine("sqlite:///dbpasskeeper2.db")
Session = sessionmaker(bind=engine)
Session = Session()

# Crear las tablas en la base de datos de prueba
Base.metadata.create_all(engine)
