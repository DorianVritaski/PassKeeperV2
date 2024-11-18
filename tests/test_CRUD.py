import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.modelo.modelo import Base, Usuario, Sesion, Contrasenia, ContraseniaEtiqueta, Etiqueta
from src.logica.CRUD import UsuarioCRUD, Contraseniacrud, EtiquetaCRUD, SesionCRUD, ContraseniaEtiquetaCRUD


class TestUsuarioCRUD(unittest.TestCase):
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear una base de datos en memoria para las pruebas
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Crear la instancia de la clase que vamos a probar, pasando la sesión
        self.usuario_crud = UsuarioCRUD(self.session)

    def tearDown(self):
        """Limpiar después de cada prueba"""
        self.session.close()

    def test_create_usuario(self):
        """Probar la creación de un usuario"""
        # Crear un usuario
        nombre_usuario = "user_test"
        email = "user_test@example.com"
        password_hash = "hashed_password"
        rol = "user"

        usuario = self.usuario_crud.create_usuario(nombre_usuario, email, password_hash, rol)

        # Verificar que el usuario fue creado correctamente
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.nombre_usuario, nombre_usuario)
        self.assertEqual(usuario.email, email)
        self.assertEqual(usuario.rol, rol)

    def test_create_usuario_duplicate_email(self):
        """Probar la creación de un usuario con un email duplicado"""
        # Crear un primer usuario
        nombre_usuario = "user_test"
        email = "user_test@example.com"
        password_hash = "hashed_password"
        rol = "user"

        self.usuario_crud.create_usuario(nombre_usuario, email, password_hash, rol)

        # Intentar crear un usuario con el mismo email
        with self.assertRaises(Exception):  # Aquí verificamos si se lanza una excepción
            self.usuario_crud.create_usuario("another_user", email, "hashed_password_2", "admin")

    def test_iniciar_sesion(self):
        """Probar el inicio de sesión de un usuario"""
        # Crear un usuario
        nombre_usuario = "user_test"
        email = "user_test@example.com"
        password_hash = "hashed_password"
        rol = "user"

        usuario = self.usuario_crud.create_usuario(nombre_usuario, email, password_hash, rol)

        # Intentar iniciar sesión
        session = self.usuario_crud.iniciar_sesion(email, password_hash)

        # Verificar que la sesión es correcta
        self.assertIsNotNone(session)
        self.assertEqual(session.id_usuario, usuario.id_usuario)

    def test_cerrar_sesion(self):
        """Probar el cierre de sesión"""
        # Crear un usuario
        nombre_usuario = "user_test"
        email = "user_test@example.com"
        password_hash = "hashed_password"
        rol = "user"

        usuario = self.usuario_crud.create_usuario(nombre_usuario, email, password_hash, rol)

        # Iniciar sesión
        session = self.usuario_crud.iniciar_sesion(email, password_hash)

        # Cerrar sesión
        self.usuario_crud.cerrar_sesion(session.id_sesion)

        # Verificar que la sesión fue cerrada
        session_cerrada = self.session.query(Sesion).filter_by(id_sesion=session.id_sesion).first()
        self.assertIsNotNone(session_cerrada.fecha_fin)
        self.assertIsInstance(session_cerrada.fecha_fin, datetime)  # Verificar que fecha_fin es una instancia de datetime
class TestContraseniacrud(unittest.TestCase):
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear una base de datos en memoria para las pruebas
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Crear la instancia de la clase que vamos a probar
        self.contrasenia_crud = Contraseniacrud(self.session)

        # Crear un usuario para asociarlo a la contraseña
        self.usuario = Usuario(
            nombre_usuario="user_test",
            email="user_test@example.com",
            password_hash="hashed_password",
            rol="user"
        )
        self.session.add(self.usuario)
        self.session.commit()

    def tearDown(self):
        """Limpiar después de cada prueba"""
        self.session.close()

    def test_create_contrasenia(self):
        """Probar la creación de una contraseña"""
        # Datos de la nueva contraseña
        servicio = "Facebook"
        nombre_usuario_servicio = "user_test_facebook"
        contrasenia_encriptada = "encrypted_password_123"
        id_usuario = self.usuario.id_usuario
        nota = "Contraseña de Facebook"

        # Crear la contraseña
        contrasenia = self.contrasenia_crud.create_contrasenia(servicio, nombre_usuario_servicio, contrasenia_encriptada, id_usuario, nota)

        # Verificar que la contraseña fue creada correctamente
        self.assertIsNotNone(contrasenia)
        self.assertEqual(contrasenia.servicio, servicio)
        self.assertEqual(contrasenia.nombre_usuario_servicio, nombre_usuario_servicio)
        self.assertEqual(contrasenia.contrasenia_encriptada, contrasenia_encriptada)
        self.assertEqual(contrasenia.id_usuario, id_usuario)
        self.assertEqual(contrasenia.nota, nota)

        # Verificar que la contraseña fue guardada en la base de datos
        contrasenia_guardada = self.session.query(Contrasenia).filter_by(id_contrasenia=contrasenia.id_contrasenia).first()
        self.assertIsNotNone(contrasenia_guardada)
        self.assertEqual(contrasenia_guardada.servicio, servicio)

    def test_create_contrasenia_without_nota(self):
        """Probar la creación de una contraseña sin nota"""
        # Datos de la nueva contraseña sin nota
        servicio = "Twitter"
        nombre_usuario_servicio = "user_test_twitter"
        contrasenia_encriptada = "encrypted_password_456"
        id_usuario = self.usuario.id_usuario

        # Crear la contraseña
        contrasenia = self.contrasenia_crud.create_contrasenia(servicio, nombre_usuario_servicio, contrasenia_encriptada, id_usuario)

        # Verificar que la contraseña fue creada correctamente sin nota
        self.assertIsNotNone(contrasenia)
        self.assertEqual(contrasenia.servicio, servicio)
        self.assertEqual(contrasenia.nombre_usuario_servicio, nombre_usuario_servicio)
        self.assertEqual(contrasenia.contrasenia_encriptada, contrasenia_encriptada)
        self.assertEqual(contrasenia.id_usuario, id_usuario)
        self.assertIsNone(contrasenia.nota)

    def test_create_contrasenia_duplicate(self):
        """Probar la creación de una contraseña con un servicio duplicado para el mismo usuario"""
        # Datos de la nueva contraseña
        servicio = "Instagram"
        nombre_usuario_servicio = "user_test_instagram"
        contrasenia_encriptada = "encrypted_password_789"
        id_usuario = self.usuario.id_usuario
        nota = "Contraseña de Instagram"

        # Crear la contraseña
        self.contrasenia_crud.create_contrasenia(servicio, nombre_usuario_servicio, contrasenia_encriptada, id_usuario, nota)

        # Intentar crear una contraseña con el mismo servicio y usuario
        with self.assertRaises(Exception):  # Aquí verificamos si se lanza una excepción
            self.contrasenia_crud.create_contrasenia(servicio, "different_username", "new_encrypted_password", id_usuario, "New note")

class TestEtiquetaCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configuración de la base de datos en memoria
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        Session = sessionmaker(bind=cls.engine)
        cls.session = Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def setUp(self):
        # Inicializar el CRUD para cada prueba
        self.etiqueta_crud = EtiquetaCRUD(self.session)

    def test_create_etiqueta(self):
        # Crear una nueva etiqueta
        etiqueta = self.etiqueta_crud.create_etiqueta('Etiqueta de prueba')
        self.assertIsNotNone(etiqueta)
        self.assertEqual(etiqueta.nombre, 'Etiqueta de prueba')

    def test_get_etiqueta(self):
        # Crear una nueva etiqueta
        etiqueta = self.etiqueta_crud.create_etiqueta('Etiqueta de prueba')
        # Obtener la etiqueta por su id
        etiqueta_obtenida = self.etiqueta_crud.get_etiqueta(etiqueta.id_etiqueta)
        self.assertIsNotNone(etiqueta_obtenida)
        self.assertEqual(etiqueta_obtenida.id_etiqueta, etiqueta.id_etiqueta)
        self.assertEqual(etiqueta_obtenida.nombre, 'Etiqueta de prueba')

    def test_update_etiqueta(self):
        # Crear una nueva etiqueta
        etiqueta = self.etiqueta_crud.create_etiqueta('Etiqueta de prueba')
        # Actualizar la etiqueta
        updated_etiqueta = self.etiqueta_crud.update_etiqueta(etiqueta.id_etiqueta, nombre='Etiqueta actualizada')
        self.assertIsNotNone(updated_etiqueta)
        self.assertEqual(updated_etiqueta.nombre, 'Etiqueta actualizada')

    def test_delete_etiqueta(self):
        # Crear una nueva etiqueta
        etiqueta = self.etiqueta_crud.create_etiqueta('Etiqueta de prueba')
        # Eliminar la etiqueta
        etiqueta_eliminada = self.etiqueta_crud.delete_etiqueta(etiqueta.id_etiqueta)
        self.assertIsNotNone(etiqueta_eliminada)
        self.assertEqual(etiqueta_eliminada.nombre, 'Etiqueta de prueba')

    def test_get_etiqueta_no_existente(self):
        # Intentar obtener una etiqueta que no existe
        with self.assertRaises(ValueError):
            self.etiqueta_crud.get_etiqueta(999)

    def test_update_etiqueta_no_existente(self):
        # Intentar actualizar una etiqueta que no existe
        with self.assertRaises(ValueError):
            self.etiqueta_crud.update_etiqueta(999, nombre='Etiqueta inexistente')

    def test_delete_etiqueta_no_existente(self):
        # Intentar eliminar una etiqueta que no existe
        with self.assertRaises(ValueError):
            self.etiqueta_crud.delete_etiqueta(999)

    def test_create_etiqueta_sin_nombre(self):
        # Intentar crear una etiqueta sin nombre
        with self.assertRaises(ValueError):
            self.etiqueta_crud.create_etiqueta('')

class TestSesionCRUD(unittest.TestCase):
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear una base de datos en memoria para las pruebas
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Crear la instancia de la clase que vamos a probar
        self.sesion_crud = SesionCRUD(self.session)

        # Crear un usuario para asociar con la sesión
        self.usuario = Usuario(nombre_usuario="user_test", email="user_test@example.com", password_hash="hashed_password", rol="user")
        self.session.add(self.usuario)
        self.session.commit()

    def tearDown(self):
        """Limpiar después de cada prueba"""
        self.session.close()

    def test_create_sesion(self):
        """Probar la creación de una sesión"""
        ip = "192.168.1.1"
        sesion = self.sesion_crud.create_sesion(self.usuario.id_usuario, ip)

        # Verificar que la sesión fue creada correctamente
        self.assertIsNotNone(sesion)
        self.assertEqual(sesion.id_usuario, self.usuario.id_usuario)
        self.assertEqual(sesion.ip, ip)
        self.assertIsInstance(sesion.fecha_inicio, datetime)

    def test_get_sesion(self):
        """Probar la obtención de una sesión por ID"""
        ip = "192.168.1.1"
        sesion = self.sesion_crud.create_sesion(self.usuario.id_usuario, ip)

        # Obtener la sesión por ID
        retrieved_sesion = self.sesion_crud.get_sesion(sesion.id_sesion)

        # Verificar que la sesión recuperada es la misma
        self.assertEqual(retrieved_sesion.id_sesion, sesion.id_sesion)
        self.assertEqual(retrieved_sesion.ip, ip)

    def test_update_sesion(self):
        """Probar la actualización de una sesión"""
        ip = "192.168.1.1"
        sesion = self.sesion_crud.create_sesion(self.usuario.id_usuario, ip)

        # Actualizar la IP de la sesión
        nueva_ip = "192.168.1.2"
        updated_sesion = self.sesion_crud.update_sesion(sesion.id_sesion, ip=nueva_ip)

        # Verificar que la sesión fue actualizada
        self.assertEqual(updated_sesion.ip, nueva_ip)

    def test_delete_sesion(self):
        """Probar la eliminación de una sesión"""
        ip = "192.168.1.1"
        sesion = self.sesion_crud.create_sesion(self.usuario.id_usuario, ip)

        # Eliminar la sesión
        deleted_sesion = self.sesion_crud.delete_sesion(sesion.id_sesion)

        # Verificar que la sesión fue eliminada
        self.assertEqual(deleted_sesion.id_sesion, sesion.id_sesion)
        self.assertIsNone(self.sesion_crud.get_sesion(sesion.id_sesion))

class TestContraseniaEtiquetaCRUD(unittest.TestCase):
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear una base de datos en memoria para las pruebas
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Crear la instancia de la clase que vamos a probar
        self.contrasenia_etiqueta_crud = ContraseniaEtiquetaCRUD(self.session)

        # Crear un usuario, una contraseña y una etiqueta para asociar
        self.usuario = Usuario(nombre_usuario="user_test", email="user_test@example.com", password_hash="hashed_password", rol="user")
        self.session.add(self.usuario)
        self.session.commit()

        self.contrasenia = Contrasenia(
            servicio="email",
            nombre_usuario_servicio="user_test@example.com",
            contrasenia_encriptada="encrypted_password",
            id_usuario=self.usuario.id_usuario
        )
        self.session.add(self.contrasenia)

        self.etiqueta = Etiqueta(nombre="work")
        self.session.add(self.etiqueta)
        self.session.commit()

    def tearDown(self):
        """Limpiar después de cada prueba"""
        self.session.close()

    def test_create_contrasenia_etiqueta(self):
        """Probar la creación de una relación entre contrasenia y etiqueta"""
        relacion = self.contrasenia_etiqueta_crud.create_contrasenia_etiqueta(self.contrasenia.id_contrasenia, self.etiqueta.id_etiqueta)

        # Verificar que la relación fue creada correctamente
        self.assertIsNotNone(relacion)
        self.assertEqual(relacion.id_contrasenia, self.contrasenia.id_contrasenia)
        self.assertEqual(relacion.id_etiqueta, self.etiqueta.id_etiqueta)

    def test_delete_contrasenia_etiqueta(self):
        """Probar la eliminación de una relación entre contrasenia y etiqueta"""
        # Crear una relación entre contrasenia y etiqueta
        relacion = self.contrasenia_etiqueta_crud.create_contrasenia_etiqueta(self.contrasenia.id_contrasenia, self.etiqueta.id_etiqueta)

        # Eliminar la relación
        deleted_relacion = self.contrasenia_etiqueta_crud.delete_contrasenia_etiqueta(relacion.id_contrasenia_etiqueta)

        # Verificar que la relación fue eliminada
        self.assertEqual(deleted_relacion.id_contrasenia_etiqueta, relacion.id_contrasenia_etiqueta)
        self.assertIsNone(self.session.query(ContraseniaEtiqueta).filter(ContraseniaEtiqueta.id_contrasenia_etiqueta == relacion.id_contrasenia_etiqueta).first())


if __name__ == '__main__':
    unittest.main()
