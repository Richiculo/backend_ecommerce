# populate_ecommerce_bolivia.py
import os
import random
import decimal
from datetime import timedelta
from faker import Faker
from random import randint, choice, uniform
from django.utils import timezone
from django.db.models import Count
from django.db import connection

# Configuración inicial
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_ecommerce.settings')
import django
django.setup()

fake = Faker('es_ES')

# Importar todos los modelos
from usuarios.models import Rol, Permiso, PermisoRol, Usuario, ActivitylogUsuario
from sucursales.models import Departamento, Sucursal
from productos.models import Proveedor, Categoria, Producto, Imagen_Producto, Detalle_Producto, Categoria_Producto, Stock_sucursal
from direcciones.models import Direccion
from pedidos.models import Metodo_Pago, Cart, ItemCart, Pago, Venta, Detalle_Venta

def vaciar_base_datos():
    """Vacía todas las tablas de la base de datos"""
    print("\nVaciando base de datos...")
    
    # Desactivar constraints temporalmente
    with connection.cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
        cursor.execute("SET CONSTRAINTS ALL DEFERRED")
    
    # Eliminar datos en orden inverso de dependencias
    Detalle_Venta.objects.all().delete()
    Venta.objects.all().delete()
    Pago.objects.all().delete()
    ItemCart.objects.all().delete()
    Cart.objects.all().delete()
    ActivitylogUsuario.objects.all().delete()
    Stock_sucursal.objects.all().delete()
    Categoria_Producto.objects.all().delete()
    Detalle_Producto.objects.all().delete()
    Imagen_Producto.objects.all().delete()
    Producto.objects.all().delete()
    Categoria.objects.all().delete()
    Proveedor.objects.all().delete()
    Direccion.objects.all().delete()
    Sucursal.objects.all().delete()
    Departamento.objects.all().delete()
    Usuario.objects.all().delete()
    PermisoRol.objects.all().delete()
    Permiso.objects.all().delete()
    Rol.objects.all().delete()
    Metodo_Pago.objects.all().delete()
    
    # Reiniciar secuencias de IDs
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sequence_name FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
        """)
        for seq in cursor.fetchall():
            cursor.execute(f"ALTER SEQUENCE {seq[0]} RESTART WITH 1")
    
    print("Base de datos vaciada exitosamente\n")

def crear_roles_y_permisos():
    print("Creando roles y permisos...")
    
    # Roles básicos (usamos get_or_create con IDs explícitos para evitar conflictos)
    roles_data = [
        (1, 'Administrador'),
        (2, 'Vendedor'),
        (3, 'Cliente'),
        (4, 'Inventario')
    ]
    
    for id, nombre in roles_data:
        Rol.objects.get_or_create(id=id, defaults={'nombre': nombre})
    
    # Permisos comunes
    permisos_data = [
        (1, 'ver_productos', 'Puede ver listado de productos'),
        (2, 'editar_productos', 'Puede editar productos'),
        (3, 'crear_productos', 'Puede crear nuevos productos'),
        (4, 'eliminar_productos', 'Puede eliminar productos'),
        (5, 'ver_ventas', 'Puede ver reportes de ventas'),
        (6, 'procesar_ventas', 'Puede procesar pedidos'),
        (7, 'ver_usuarios', 'Puede ver listado de usuarios'),
        (8, 'editar_usuarios', 'Puede editar usuarios'),
    ]
    
    for id, codigo, desc in permisos_data:
        Permiso.objects.get_or_create(
            id=id,
            defaults={
                'nombre': codigo,
                'descripcion': desc
            }
        )
    
    # Asignar permisos a roles
    permisos_assign = [
        # Administrador - todos los permisos
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
        # Vendedor - todos excepto editar usuarios y eliminar productos
        (2, 1), (2, 2), (2, 3), (2, 5), (2, 6), (2, 7),
        # Inventario - solo permisos de productos
        (4, 1), (4, 2), (4, 3)
    ]
    
    for rol_id, permiso_id in permisos_assign:
        PermisoRol.objects.get_or_create(
            rol_id=rol_id,
            permiso_id=permiso_id
        )
    
    print(f"Roles creados: {Rol.objects.count()}")
    print(f"Permisos creados: {Permiso.objects.count()}")

def crear_departamentos_bolivia():
    print("\nCreando departamentos de Bolivia...")
    departamentos = [
        "La Paz", "Santa Cruz", "Cochabamba", "Oruro", 
        "Potosí", "Tarija", "Chuquisaca", "Beni", "Pando"
    ]
    
    # Crear con IDs explícitos para evitar problemas
    for i, depto in enumerate(departamentos, 1):
        Departamento.objects.get_or_create(
            id=i,
            defaults={'nombre': depto}
        )
    
    print(f"Departamentos creados: {Departamento.objects.count()}")

def crear_sucursales():
    print("\nCreando sucursales...")
    # Mapeo de ciudades a departamentos
    ciudad_depto = {
        "La Paz": "La Paz",
        "Santa Cruz": "Santa Cruz",
        "Cochabamba": "Cochabamba",
        "El Alto": "La Paz",
        "Sucre": "Chuquisaca"
    }
    
    ciudades = [
        ("La Paz", "Av. 16 de Julio"),
        ("Santa Cruz", "Av. San Martín"),
        ("Cochabamba", "Av. Heroínas"),
        ("El Alto", "Av. Juan Pablo II"),
        ("Sucre", "Av. Venezuela")
    ]
    
    for i, (ciudad, direccion_principal) in enumerate(ciudades, 1):
        try:
            # Obtener el departamento correspondiente
            nombre_depto = ciudad_depto[ciudad]
            depto = Departamento.objects.get(nombre=nombre_depto)
            
            # Crear dirección
            direccion = Direccion.objects.create(
                pais="Bolivia",
                departamento=depto,
                ciudad=ciudad,
                calle=direccion_principal,
                numero=str(randint(100, 2000)),
                referencia=f"Entre {fake.street_name()} y {fake.street_name()}"
            )
            
            # Crear sucursal
            sucursal = Sucursal.objects.create(
                id=i,
                nombre=f"TecnoEmpresa {ciudad}",
                telefono=fake.numerify(text='2#######'),
                direccion=direccion
            )
            print(f"Sucursal creada: {sucursal.nombre}")
        except Exception as e:
            print(f"Error creando sucursal en {ciudad}: {str(e)}")

def crear_proveedores_electronicos():
    print("\nCreando proveedores de tecnología...")
    proveedores = [
        {"nombre": "TecnoImport Bolivia", "contacto": "Juan Pérez", "telefono": "22778899", "correo": "contacto@tecnoimport.bo"},
        {"nombre": "ElectroTech SRL", "contacto": "María Gómez", "telefono": "22446688", "correo": "ventas@electrotech.bo"},
        {"nombre": "Apple Bolivia", "contacto": "Carlos Fernández", "telefono": "22334455", "correo": "distribuidor@apple.bo"},
        {"nombre": "Samsung Bolivia", "contacto": "Ana Rodríguez", "telefono": "22667788", "correo": "ventas@samsung.bo"},
        {"nombre": "Xiaomi Official", "contacto": "Luisa Méndez", "telefono": "22558877", "correo": "xiaomi@distribuidor.bo"},
    ]
    
    for i, prov in enumerate(proveedores, 1):
        Proveedor.objects.create(
            id=i,
            **prov
        )
    
    print(f"Proveedores creados: {Proveedor.objects.count()}")

def crear_categorias_electronicos():
    print("\nCreando categorías de electrónicos...")
    categorias = [
        (1, "Smartphones", "Teléfonos inteligentes de última generación"),
        (2, "Laptops", "Computadoras portátiles para trabajo y gaming"),
        (3, "Tablets", "Dispositivos táctiles de diversas marcas"),
        (4, "Smartwatches", "Relojes inteligentes y wearables"),
        (5, "Audio", "Audífonos, parlantes y equipos de sonido"),
        (6, "Cámaras", "Cámaras fotográficas y drones"),
        (7, "Gaming", "Consolas, accesorios y componentes para gamers"),
        (8, "Componentes", "Hardware para computadoras y repuestos")
    ]
    
    for id, nombre, desc in categorias:
        Categoria.objects.create(
            id=id,
            nombre=nombre,
            descripcion=desc
        )
    
    print(f"Categorías creadas: {Categoria.objects.count()}")

def crear_usuarios(cantidad=30):
    print("\nCreando usuarios bolivianos...")
    
    # Usuario admin con ID fijo
    admin, created = Usuario.objects.get_or_create(
        id=1,
        defaults={
            'nombre': "Admin",
            'apellidos': "Sistema",
            'correo': "admin@tecnoempresa.bo",
            'is_staff': True,
            'is_superuser': True,
            'rol_id': 1  # Administrador
        }
    )
    if created:
        admin.set_password("admin123")
        admin.save()
    
    # Crear usuarios de prueba
    dominios = ['gmail.com', 'hotmail.com', 'yahoo.com', 'tecnoempresa.bo']
    roles = [2, 3, 4]  # IDs de Vendedor, Cliente, Inventario
    
    for i in range(2, cantidad + 2):  # Empezamos desde ID 2
        try:
            user = Usuario.objects.create(
                id=i,
                nombre=fake.first_name(),
                apellidos=fake.last_name() + " " + fake.last_name(),
                correo=f"{fake.user_name()}{i}@{choice(dominios)}",
                rol_id=choice(roles)
            )
            user.set_password("cliente123")
            user.save()
            
            if i % 10 == 0:
                print(f"Usuario creado: {user.correo} - Rol: {user.rol.nombre}")
        except Exception as e:
            print(f"Error creando usuario: {str(e)}")
            continue
    
    print(f"Total usuarios creados: {Usuario.objects.count()}")

def crear_direcciones_usuarios():
    print("\nCreando direcciones para usuarios...")
    usuarios = Usuario.objects.all()
    departamentos = Departamento.objects.all()
    
    for i, usuario in enumerate(usuarios, 1):
        try:
            depto = choice(departamentos)
            ciudad = fake.city() if depto.nombre != "La Paz" else choice(["La Paz", "El Alto"])
            
            Direccion.objects.create(
                id=i,
                usuario=usuario,
                pais="Bolivia",
                departamento=depto,
                ciudad=ciudad,
                zona=fake.bothify(text='Zona ##'),
                calle=fake.street_name(),
                numero=fake.building_number(),
                referencia=fake.sentence()
            )
        except Exception as e:
            print(f"Error creando dirección para usuario {usuario.id}: {str(e)}")
    
    print(f"Direcciones creadas: {Direccion.objects.count()}")

def crear_productos_electronicos():
    print("\nCreando productos electrónicos...")
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()
    
    # Smartphones
    marcas_phones = ["Samsung", "Apple", "Xiaomi", "Huawei", "Oppo"]
    for i, marca in enumerate(marcas_phones, 1):
        for j in range(1, 6):
            modelo = f"{marca} {choice(['Galaxy', 'iPhone', 'Redmi', 'Mate', 'Reno'])} {j}"
            producto = Producto.objects.create(
                id=(i-1)*5 + j,
                nombre=modelo,
                descripcion=f"Smartphone {marca} modelo {j} con {randint(4, 12)}GB RAM y {randint(64, 512)}GB almacenamiento",
                proveedor=choice(proveedores),
                esta_activo=True,
                esta_disponible=random.choice([True, True, True, False])  # 75% de probabilidad de estar disponible
            )
            
            # Precio y detalles
            precio_compra = decimal.Decimal(randint(800, 3000))
            precio_venta = precio_compra * decimal.Decimal(1.3)  # 30% de margen
            
            Detalle_Producto.objects.create(
                producto=producto,
                marca=marca,
                precio_compra=precio_compra,
                precio_venta=precio_venta,
                tiene_descuento=random.choice([True, False]),
                porcentaje_descuento=randint(5, 20) if random.choice([True, False]) else 0
            )
            
            # Asignar categorías
            cat_principal = categorias.get(nombre="Smartphones")
            Categoria_Producto.objects.create(producto=producto, categoria=cat_principal)
            
            # Asignar categoría secundaria (30% de probabilidad)
            if random.random() < 0.3:
                cat_secundaria = choice(categorias.exclude(nombre="Smartphones"))
                Categoria_Producto.objects.create(producto=producto, categoria=cat_secundaria)
    
    print(f"Productos electrónicos creados: {Producto.objects.count()}")

def crear_stock_sucursales():
    print("\nCreando stock en sucursales...")
    productos = Producto.objects.all()
    sucursales = Sucursal.objects.all()
    
    for i, producto in enumerate(productos, 1):
        for j, sucursal in enumerate(sucursales, 1):
            Stock_sucursal.objects.create(
                id=(i-1)*len(sucursales) + j,
                producto=producto,
                sucursal=sucursal,
                stock=randint(0, 20) if producto.esta_activo and producto.esta_disponible else 0
            )
    
    # Actualizar stock total en productos
    for producto in productos:
        producto.actualizar_stock_total()
    
    print(f"Registros de stock creados: {Stock_sucursal.objects.count()}")

def crear_metodos_pago_bolivia():
    print("\nCreando métodos de pago en Bolivia...")
    metodos = [
        {"nombre": "Tarjeta de crédito", "proveedor": "Visa/Mastercard", "descripcion": "Pago con tarjeta de crédito internacional"},
        {"nombre": "Transferencia bancaria", "proveedor": "BNB", "descripcion": "Transferencia desde cualquier banco nacional"},
        {"nombre": "Pago móvil", "proveedor": "Tigo Money", "descripcion": "Pago desde tu billetera móvil"},
        {"nombre": "QR", "proveedor": "Kash", "descripcion": "Pago con código QR desde tu banco"},
        {"nombre": "Efectivo", "proveedor": "Pago en sucursal", "descripcion": "Pago en efectivo en nuestras tiendas físicas"},
    ]
    
    for i, metodo in enumerate(metodos, 1):
        Metodo_Pago.objects.create(
            id=i,
            **metodo
        )
    
    print(f"Métodos de pago creados: {Metodo_Pago.objects.count()}")

def crear_pedidos_y_ventas():
    print("\nCreando pedidos y ventas...")
    usuarios = Usuario.objects.filter(rol__nombre='Cliente')
    productos = Producto.objects.filter(esta_activo=True, esta_disponible=True)
    metodos_pago = Metodo_Pago.objects.all()
    sucursales = Sucursal.objects.all()
    
    for i in range(1, 101):  # Crearemos 100 pedidos/ventas
        try:
            usuario = choice(usuarios)
            fecha_pedido = fake.date_time_between(start_date='-6months', end_date='now')
            
            # Crear carrito
            cart = Cart.objects.create(
                id=i,
                usuario=usuario,
                creado_en=fecha_pedido,
                estado=choice(['activo', 'confirmado', 'cancelado'])
            )
            
            # Agregar items al carrito (1-5 productos)
            productos_carrito = random.sample(list(productos), k=randint(1, 5))
            for j, producto in enumerate(productos_carrito, 1):
                detalle = producto.detalle
                ItemCart.objects.create(
                    id=(i-1)*5 + j,
                    cart=cart,
                    producto=producto,
                    cantidad=randint(1, 3),
                    precio_unitario=detalle.precio_final
                )
            
            # Si el carrito fue confirmado, crear venta
            if cart.estado == 'confirmado':
                total = sum(item.precio_unitario * item.cantidad for item in cart.items.all())
                
                # Crear pago
                pago = Pago.objects.create(
                    id=i,
                    metodo=choice(metodos_pago),
                    monto=total,
                    estado=choice(['pendiente', 'completado', 'fallido']),
                    fecha=fecha_pedido + timedelta(hours=randint(1, 24)),
                    referencia=fake.bothify(text='PAY-########') if random.choice([True, False]) else None
                )
                
                # Crear venta
                venta = Venta.objects.create(
                    id=i,
                    usuario=usuario,
                    pago=pago,
                    total=total,
                    estado=choice(['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado'])
                )
                
                # Crear detalles de venta
                for j, item in enumerate(cart.items.all(), 1):
                    Detalle_Venta.objects.create(
                        id=(i-1)*5 + j,
                        venta=venta,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.precio_unitario
                    )
                
                # Registrar actividad
                ActivitylogUsuario.objects.create(
                    id_usuario=usuario,
                    accion=f"Realizó compra por Bs. {total:.2f}"
                )
                
                if i % 20 == 0:
                    print(f"Venta #{venta.id} - Bs. {venta.total:.2f} - {venta.estado}")
        except Exception as e:
            print(f"Error creando pedido #{i}: {str(e)}")
            continue
    
    print("\nResumen de ventas:")
    print(f"Total pedidos: {Cart.objects.count()}")
    print(f"Total ventas confirmadas: {Venta.objects.count()}")

if __name__ == "__main__":
    print("=== POBLANDO E-COMMERCE ELECTRÓNICOS BOLIVIA ===")
    print("Este proceso puede tomar varios minutos...\n")
    
    # Vaciar la base de datos primero
    vaciar_base_datos()
    
    # Crear datos nuevos
    crear_roles_y_permisos()
    crear_departamentos_bolivia()
    crear_proveedores_electronicos()
    crear_categorias_electronicos()
    crear_sucursales()
    crear_usuarios()
    crear_direcciones_usuarios()
    crear_productos_electronicos()
    crear_stock_sucursales()
    crear_metodos_pago_bolivia()
    crear_pedidos_y_ventas()
    
    print("\n=== POBLACIÓN COMPLETADA ===")
    print("Credenciales importantes:")
    print("- Admin: correo 'admin@tecnoempresa.bo' / contraseña 'admin123'")
    print("- Clientes: contraseña 'cliente123' para todos los usuarios")
    print("\nEstadísticas finales:")
    print(f"- Usuarios: {Usuario.objects.count()}")
    print(f"- Productos: {Producto.objects.count()}")
    print(f"- Ventas: {Venta.objects.count()}")
    print(f"- Ingresos totales: Bs. {sum(v.total for v in Venta.objects.all()):.2f}")