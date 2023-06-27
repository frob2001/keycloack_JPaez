from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from config import auth, fdb

app = Flask(__name__)
app.secret_key = "felimax2"

#-----------------------------------------LOGIN-----------------------------------------------------

def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if not session.get("user"):
      return redirect(url_for("index"))
    return f(*args, **kwargs)
  return decorated_function

@app.route('/')
def index():
  return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
  email = request.form['email']
  password = request.form['password']
  try:
    user = auth.sign_in_with_email_and_password(email, password)
    session["user"] = user['idToken']
    return redirect(url_for('inventario'))
  except:
    return render_template('login.html', message='El correo o la contraseña son incorrectos')


@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for("index"))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            return render_template('reset_password.html', message='Email de reseteo de contrasena enviado con exito')
        except:
            return render_template('reset_password.html', error='El correo no esta registrado')

    return render_template('reset_password.html')


#-----------------------------------------MANEJO DE SUCURSALES-----------------------------------------------------

@app.route("/sucursales/")
@login_required
def sucursales():
  datos = fdb.child("Sucursales").get().val()
  print(datos)
  return render_template("sucursales.html", datos=datos)

@app.route('/actualizarsucursal/<string:key>/<string:nombre>', methods=["GET", "POST"])
@login_required
def actualizar_sucursal(key, nombre):
  campo = fdb.child("Sucursales").child(key).get().val()
  if request.method == "POST":
    if nombre == "9 de Octubre":
       flash("La sucursal matriz no se puede actualizar")
       return redirect(url_for('detalles_sucursal', key=key))
    else:   
       nombre = request.form["nombre"]
       direccion = request.form["direccion"]
       fdb.child("Sucursales").child(key).update({"nombre": nombre, "direccion": direccion})
       flash("La sucursal ha sido modificada con éxito")
       return redirect(url_for('detalles_sucursal', key=key))
  else:
    return render_template('actualizarSucursal.html', key=key, campo=campo)

@app.route('/eliminarsucursal/<string:key>/<string:nombre>')
@login_required
def eliminar_sucursal(key, nombre):
    if nombre == "9 de Octubre":
       flash("La sucursal no se puede eliminar, es la sucursal matriz")
    else:   
       fdb.child("Sucursales").child(key).remove()
       flash("La sucursal ha sido eliminada con éxito")
    return redirect(url_for('sucursales'))

@app.route('/agregarsucursal/', methods=["GET", "POST"])
@login_required
def agregar_sucursal():
    if request.method == "POST":
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        nueva_sucursal = {"nombre": nombre, "direccion": direccion}

        #validación, si la sucursal ya existe no se repite, si no hay datos guardados, se compara con la lista nombres = [""]
        datos = fdb.child("Sucursales").get().val()
        nombres= [""]
        print(datos) #Devuelve none en caso de no tener datos
        if datos != None:
           nombres = [d['nombre'] for d in datos.values()]

        #Validación, compara los nombres de todos las sucursales en la base de datos
        if nombre in nombres:
           return render_template('agregarSucursal.html', message='La sucursal ya existe.')
        else:
           fdb.child("Sucursales").push(nueva_sucursal)
        return redirect(url_for('sucursales'))
    else:
       return render_template("agregarSucursal.html")

@app.route('/detallessucursal/<string:key>')
@login_required
def detalles_sucursal(key):
    campo = fdb.child('Sucursales').child(key).get().val()
    return render_template('detallesSucursales.html', key=key, campo=campo)


#-----------------------------------------MANEJO DE USUARIOS-----------------------------------------------------
#Mostrar usuarios
@app.route("/usuarios/")
@login_required
def usuarios():
  datos = fdb.child("Usuarios").get().val()
  return render_template("usuarios.html", datos=datos)

#Crear usuarios
@app.route('/crear_usuario/', methods=['GET', 'POST'])
def crear_usuario():
    datos = fdb.child("Sucursales").get().val()
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password == confirm_password:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                idToken = user['idToken']
                fdb.child("Usuarios").child(user['localId']).set({
                    "nombre": nombre,
                    "apellido": apellido,
                    "email": email,
                    "role": role,
                    "idToken":idToken
                })

                return redirect('/usuarios/')
            except Exception as e:
                return render_template("agregar_usuarios.html", message=str(e), datos=datos)
        else:
            return render_template("agregar_usuarios.html", message="Las contraseñas no corresponden.", datos=datos)
    else:
        return render_template("agregar_usuarios.html", datos=datos)


#Detalles de usuario
@app.route('/detalles_usuarios/<string:key>')
@login_required
def detalles_usuarios(key):
    campo = fdb.child('Usuarios').child(key).get().val()
    return render_template('detalles_usuarios.html', key=key, campo=campo)


#Eliminar usuario
@app.route('/eliminar_usuarios/<string:key>')
@login_required
def eliminar_usuarios(key):
    campo = fdb.child('Usuarios').child(key).get().val()

    idToken = campo['idToken']
    auth.delete_user_account(idToken)
    
    fdb.child("Usuarios").child(key).remove()

    flash("El usuario ha sido eliminado con éxito")
    return redirect(url_for('usuarios'))

#Actualizar usuario
@app.route('/actualizar_usuarios/<string:key>', methods=["GET", "POST"])
@login_required
def actualizar_usuarios(key):
  datos = fdb.child("Sucursales").get().val()
  campo = fdb.child("Usuarios").child(key).get().val()
  if request.method == "POST":
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    role = request.form['role']
    fdb.child("Usuarios").child(key).update({
        "nombre": nombre,
        "apellido": apellido,
        "role": role
    })
    flash("El usuario ha sido modificado con éxito")
    return redirect(url_for('detalles_usuarios', key=key))
  else:
    return render_template('actualizar_usuarios.html', key=key, campo=campo, datos=datos)


#-----------------------------------------MANEJO DE INVENTARIO-----------------------------------------------------

@app.route("/inventario/")
@login_required
def inventario():
  sucursales = fdb.child("Sucursales").get().val()
  nombres = [sucursal['nombre'] for sucursal in sucursales.values()]
  datos = fdb.child("Inventario").get().val()
  print(datos)
  return render_template("inventario.html", datos=datos, nombres=nombres)

@app.route('/verificar_codigo', methods=['POST'])
def verificar_codigo():
    codigo = request.form['codigo'].upper()
    datos = fdb.child("Inventario").get().val()
    if datos is None:
        codigos = []
    else:
        codigos = [d['codigo'] for d in datos.values()]
    existe = codigo in codigos
    return jsonify({'existe': existe})


@app.route('/crear_producto/', methods=["GET", "POST"])
@login_required
def crear_producto():
    datos = fdb.child("Sucursales").get().val()
    nombres = [sucursal['nombre'] for sucursal in datos.values()]
    if request.method == "POST":
        codigo = request.form["codigo"].upper()
        descripcion = request.form["descripcion"].upper()
        data = {}
        for key in request.form.keys():
           if key.startswith('oem'):
              data[key] = [x.upper() for x in request.form.getlist(key)]

        oems = data
        if oems == "":
           oems = "N/A"
        marca = request.form["marca"].upper()
        referencia = request.form["referencia"].upper()
        if referencia == "":
           referencia = "N/A"
        precio = float(request.form["precio"])
        precioiva = round(float(request.form["precio"])*1.12, 2)

        inventario = {}
        for nom in nombres:
           ubicacion = request.form["ubicacion " + nom].upper()
           if ubicacion == "":
              ubicacion = "N/A"
           ubicacionespecifica = request.form["ubicacionespecifica " + nom].upper()
           if ubicacionespecifica == "":
              ubicacionespecifica = "N/A"
           stock = request.form["stock " + nom]
           if stock == "":
              stock = 0
           else:
              stock = int(request.form["stock " + nom])
           inventario[nom] = {'ubicacion':ubicacion, 'ubicacionespecifica': ubicacionespecifica, 'stock':stock}
        print(inventario)

        datos = fdb.child("Inventario").get().val()
        codigos = [""]
        if datos != None:
           codigos = [d['codigo'] for d in datos.values()]

        #Validación, compara los nombres de todos las sucursales en la base de datos
        if codigo in codigos:
           return render_template('agregar_inventario.html', message='El producto ya existe.')
        else:
           fdb.child("Inventario").push({
            "codigo": codigo,
            "descripcion": descripcion,
            "oems": oems,
            "marca": marca,
            "referencia": referencia,
            "precio": precio,
            "precioiva": precioiva,
            "estado": inventario
        })
        return redirect(url_for('inventario'))
    else:
       datos = fdb.child("Sucursales").get().val()
       nombres = [sucursal['nombre'] for sucursal in datos.values()]

       return render_template("agregar_inventario.html", nombres=nombres)

@app.route('/detalles_producto/<string:key>')
@login_required
def detalles_producto(key):
    print(key)
    campo = fdb.child('Inventario').child(key).get().val()
    datos = fdb.child("Sucursales").get().val()
    nombres = [sucursal['nombre'] for sucursal in datos.values()]
    return render_template('detalles_inventario.html', key=key, campo=campo, nombres=nombres)

@app.route('/actualizar_producto/<string:key>', methods=["GET", "POST"])
@login_required
def actualizar_producto(key):
  campo = fdb.child("Inventario").child(key).get().val()
  datos = fdb.child("Sucursales").get().val()
  nombres = [sucursal['nombre'] for sucursal in datos.values()]
  if request.method == "POST":
      print(key)
      codigo = campo["codigo"]
      descripcion = request.form["descripcion"].upper()
      data = {}
      for code in request.form.keys():
          if code.startswith('oem'):
            data[code] = [x.upper() for x in request.form.getlist(code)]

      oems = data
      if oems == "":
          oems = "N/A"
      marca = request.form["marca"].upper()
      referencia = request.form["referencia"].upper()
      if referencia == "":
          referencia = "N/A"
      precio = float(request.form["precio"])
      precioiva = round(float(request.form["precio"])*1.12, 2)

      inventario = {}
      for nom in nombres:
          ubicacion = request.form["ubicacion " + nom].upper()
          if ubicacion == "":
            ubicacion = "N/A"
          ubicacionespecifica = request.form["ubicacionespecifica " + nom].upper()
          if ubicacionespecifica == "":
            ubicacionespecifica = "N/A"
          stock = request.form["stock " + nom]
          if stock == "":
            stock = 0
          else:
            stock = int(request.form["stock " + nom])
          inventario[nom] = {'ubicacion':ubicacion, 'ubicacionespecifica': ubicacionespecifica, 'stock':stock}
      print(inventario)
      fdb.child("Inventario").child(key).update({
        "codigo": codigo,
        "descripcion": descripcion,
        "oems": oems,
        "marca": marca,
        "referencia": referencia,
        "precio": precio,
        "precioiva": precioiva,
        "estado": inventario
      })
      flash("El producto se ha sido modificado con éxito")
      return redirect(url_for('detalles_producto', key=key))
  else:
      datos = fdb.child("Sucursales").get().val()
      nombres = [sucursal['nombre'] for sucursal in datos.values()]
      print(key)
      return render_template('actualizar_inventario.html', key=key, campo=campo, nombres=nombres)

@app.route('/eliminar_producto/<string:key>')
@login_required
def eliminar_producto(key):
    fdb.child("Inventario").child(key).remove()
    flash("El producto se ha sido eliminado con éxito")
    return redirect(url_for('inventario'))


#-----------------------------------------SALIDAS POR VENTAS-----------------------------------------------------
@app.route("/salidas/", methods=['GET', 'POST'])
@login_required
def salidas():
    datos = fdb.child("Sucursales").get().val()
    nombres = [sucursal['nombre'] for sucursal in datos.values()]
    
    if request.method == 'POST':
        sucursal_seleccionada = request.form['sucursal']
        # Obtener los datos de ventas de la sucursal seleccionada según tu lógica
        ventas = fdb.child("Salidas").child(sucursal_seleccionada).get().val()
        return render_template("salidas_ventas.html", nombres=nombres, ventas=ventas, sucursal_seleccionada=sucursal_seleccionada)
    else:
       sucursal_seleccionada = "9 de Octubre"
       ventas = fdb.child("Salidas").child(sucursal_seleccionada).get().val()
       print(ventas)
       return render_template("salidas_ventas.html", nombres=nombres, ventas=ventas, sucursal_seleccionada=sucursal_seleccionada)

@app.route('/crear_salida/<string:sucursal_seleccionada>', methods=['GET', 'POST'])
@login_required
def crear_salida(sucursal_seleccionada):
    if request.method == 'POST':
      documento = request.form["documento"].upper()
      fecha = request.form["fecha"]

      sucursal = request.form.get('sucursal', 'N/A').upper()
      
      cliente = request.form.get('cliente', 'N/A').upper()

      tipo_pago = request.form["tipo_pago"].upper()

      total = request.form["totalgeneral"].upper()

      productos = request.form.getlist("productocodigo")

      cantidades = request.form.getlist("cantidadproducto")

      precios = request.form.getlist("precioproducto")

      descuento = int(request.form["descuento"])

      print(documento, fecha, cliente, sucursal, tipo_pago, total, descuento, productos, cantidades)

      for i, producto in enumerate(productos):
          if ":" in producto:
              producto_info = producto.split(":")
              producto_codigo = producto_info[0].strip()  # Obtener el código del producto sin espacios adicionales
          else:
              producto_codigo = producto.strip()  # Utilizar el nombre completo del producto como código

          cantidad = int(cantidades[i])

          inventario = fdb.child("Inventario").get().val()

          for producto_key, producto_data in inventario.items():
              if producto_data["codigo"] == producto_codigo:
                  estado = producto_data["estado"]
                  if sucursal_seleccionada in estado:
                      stock_actual = estado[sucursal_seleccionada]["stock"]
                      nuevo_stock = stock_actual - cantidad
                      estado[sucursal_seleccionada]["stock"] = nuevo_stock
                      fdb.child("Inventario").child(producto_key).child("estado").set(estado)



      fdb.child("Salidas").child(sucursal_seleccionada).push({
        "documento": documento,
        "fecha": fecha,
        "cliente": cliente,
        "sucursal": sucursal,
        "tipo_pago": tipo_pago,
        "productos": productos,
        "cantidades": cantidades,
        "precio": precios,
        "total": total,
        "descuento": descuento
      })
      flash("La salida se ha creado")
      return redirect(url_for('salidas'))
    
    else:
      datos = fdb.child("Sucursales").get().val()
      nombres = [sucursal_seleccionada['nombre'] for sucursal_seleccionada in datos.values()]
      productos_con_stock = {}
      datos = fdb.child("Inventario").get().val()
      for producto in datos.values():
          sucursal_info = producto["estado"]
          estado = sucursal_info[sucursal_seleccionada]
          stock = estado["stock"]
          if stock > 0:
            oems=[]
            for data in producto['oems'].values():
              for x in range (1, len(data)):
                oems.append(str(data[0]) + str(data[x]))
            productos_con_stock[producto["codigo"]] = [oems, producto["descripcion"], stock, producto["precio"]]
        
          print(productos_con_stock)
        
      return render_template("agregar_salidas.html", productos=productos_con_stock, nombres=nombres, sucursal_seleccionada=sucursal_seleccionada)

@app.route('/detalles_salida/<string:sucursal_seleccionada>/<string:key>', methods=['GET', 'POST'])
@login_required
def detalles_salida(sucursal_seleccionada, key):
    salida = fdb.child('Salidas').child(sucursal_seleccionada).child(key).get().val()
    print(salida)
    return render_template('detalles_salida.html', key=key, salida=salida, sucursal_seleccionada=sucursal_seleccionada)
   
@app.route('/eliminar_salida/<string:sucursal_seleccionada>/<string:key>')
@login_required
def eliminar_salida(sucursal_seleccionada, key):
    llave = key
    salida = fdb.child('Salidas').child(sucursal_seleccionada).child(llave).get().val()
    inventario = fdb.child('Inventario').get().val()

    productos = salida['productos']
    cantidades = salida['cantidades']

    for i in range(len(productos)):
        producto_codigo = productos[i].split(':')[0]
        cantidad = int(cantidades[i])

        for key, producto in inventario.items():
            if producto['codigo'] == producto_codigo:
                producto['estado'][sucursal_seleccionada]['stock'] += cantidad
                break

    fdb.child('Inventario').set(inventario)
    fdb.child('Salidas').child(sucursal_seleccionada).child(llave).remove()

    flash("El producto se ha sido eliminado con éxito")
    return redirect(url_for('salidas'))

#-----------------------------------------ENTRADAS POR COMPRAS--------------------------------------------------
  
@app.route("/entradas_compras/", methods=['GET', 'POST'])
@login_required
def entradas_compras():
    compras = fdb.child("Entradas_Compras").get().val()
    print(compras)
    return render_template("entradas_compras.html", compras=compras)

@app.route('/crear_producto_compras/', methods=["GET", "POST"])
@login_required
def crear_producto_compras():
    datos = fdb.child("Sucursales").get().val()
    nombres = [sucursal['nombre'] for sucursal in datos.values()]
    if request.method == "POST":
        documento = request.form["documento"].upper()
        fecha = request.form["fecha"]
        tipo_compra = request.form['radio'].upper()
        codigo = request.form["codigo"].upper()
        descripcion = request.form["descripcion"].upper()
        data = {}
        for key in request.form.keys():
           if key.startswith('oem'):
              data[key] = [x.upper() for x in request.form.getlist(key)]

        oems = data
        if oems == "":
           oems = "N/A"
        marca = request.form["marca"].upper()
        referencia = request.form["referencia"].upper()
        if referencia == "":
           referencia = "N/A"
        precio = float(request.form["precio"])
        precioiva = round(float(request.form["precio"])*1.12, 2)

        inventario = {}
        for nom in nombres:
           ubicacion = request.form["ubicacion " + nom].upper()
           if ubicacion == "":
              ubicacion = "N/A"
           ubicacionespecifica = request.form["ubicacionespecifica " + nom].upper()
           if ubicacionespecifica == "":
              ubicacionespecifica = "N/A"
           stock = request.form["stock " + nom]
           if stock == "":
              stock = 0
           else:
              stock = int(request.form["stock " + nom])
           inventario[nom] = {'ubicacion':ubicacion, 'ubicacionespecifica': ubicacionespecifica, 'stock':stock}
        print(inventario)

        datos = fdb.child("Inventario").get().val()
        codigos = [""]
        if datos != None:
           codigos = [d['codigo'] for d in datos.values()]

        #Validación, compara los nombres de todos las sucursales en la base de datos
        if codigo in codigos:
           return render_template('agregar_inventario_compras.html', message='El producto ya existe.')
        else:
           fdb.child("Inventario").push({
            "codigo": codigo,
            "descripcion": descripcion,
            "oems": oems,
            "marca": marca,
            "referencia": referencia,
            "precio": precio,
            "precioiva": precioiva,
            "estado": inventario
           })
           fdb.child("Entradas_Compras").push({
              "documento": documento,
              "fecha": fecha,
              "productos": [codigo + ": "+ descripcion],
              "tipo_compra": tipo_compra,
              "cantidades": [inventario["9 de Octubre"]["stock"]],
              "precio": [precio],
              "total": round((inventario["9 de Octubre"]["stock"] * precio), 2)     
           })
        return redirect(url_for('entradas_compras'))
    else:
       datos = fdb.child("Sucursales").get().val()
       nombres = [sucursal['nombre'] for sucursal in datos.values()]

       return render_template("agregar_inventario_compras.html", nombres=nombres)

@app.route('/crear_entrada_compra/', methods=['GET', 'POST'])
@login_required
def crear_entrada_compra():
    if request.method == 'POST':
      documento = request.form["documento"].upper()
      fecha = request.form["fecha"]

      tipo_compra = request.form['radio'].upper()
      total = request.form["totalgeneral"].upper()
      productos = request.form.getlist("productocodigo")
      cantidades = request.form.getlist("cantidadproducto")
      precios = request.form.getlist("precioproducto")

      print(documento, fecha, total, productos, cantidades)

      for i, producto in enumerate(productos):
          if ":" in producto:
              producto_info = producto.split(":")
              producto_codigo = producto_info[0].strip()  # Obtener el código del producto sin espacios adicionales
          else:
              producto_codigo = producto.strip()  # Utilizar el nombre completo del producto como código

          cantidad = int(cantidades[i])

          inventario = fdb.child("Inventario").get().val()

          for producto_key, producto_data in inventario.items():
              if producto_data["codigo"] == producto_codigo:
                  estado = producto_data["estado"]
                  if "9 de Octubre" in estado:
                      stock_actual = estado["9 de Octubre"]["stock"]
                      nuevo_stock = stock_actual + cantidad
                      estado["9 de Octubre"]["stock"] = nuevo_stock
                      fdb.child("Inventario").child(producto_key).child("estado").set(estado)

      fdb.child("Entradas_Compras").push({
        "documento": documento,
        "fecha": fecha,
        "productos": productos,
        "tipo_compra": tipo_compra,
        "cantidades": [inventario["9 de Octubre"]["stock"]],
        "precio": [precios],
        "total": round((inventario["9 de Octubre"]["stock"] * precios), 2)     
      })
      flash("La salida se ha creado")
      return redirect(url_for('entradas_compras'))
    
    else:
      productos = {}
      datos = fdb.child("Inventario").get().val()
      for producto in datos.values():
          sucursal_info = producto["estado"]
          estado = sucursal_info["9 de Octubre"]
          stock = estado["stock"]
          oems=[]
          for data in producto['oems'].values():
            for x in range (1, len(data)):
              oems.append(str(data[0]) + str(data[x]))
          productos[producto["codigo"]] = [oems, producto["descripcion"], stock, producto["precio"]]
        
      return render_template("agregar_entradas_compras.html", productos=productos)


@app.route('/detalles_entrada_compra/<string:key>', methods=['GET', 'POST'])
@login_required
def detalles_entrada_compra(key):
    print(key)
    entrada = fdb.child('Entradas_Compras').child(key).get().val()
    return render_template('detalles_entradas_compras.html', key=key, entrada=entrada)

@app.route('/eliminar_entrada_compra/<string:key>')
@login_required
def eliminar_entrada_compra(key):
    llave = key
    salida = fdb.child('Entradas_Compras').child(llave).get().val()
    inventario = fdb.child('Inventario').get().val()

    productos = salida['productos']
    cantidades = salida['cantidades']

    for i in range(len(productos)):
        producto_codigo = productos[i].split(':')[0]
        cantidad = int(cantidades[i])

        print(producto_codigo)

        for key, producto in inventario.items():
            if producto['codigo'] == producto_codigo:
                producto['estado']['9 de Octubre']['stock'] -= cantidad
                break

    fdb.child('Inventario').set(inventario)
    fdb.child('Entradas_Compras').child(llave).remove()

    flash("La entrada por compra se ha eliminado con éxito")
    return redirect(url_for('entradas_compras'))

#-----------------------------------------ANALISIS ABC CORE-----------------------------------------------------

@app.route('/abc_analisis/')
@login_required
def abc_analysis():
    # Obtener los datos de Firebase
    inventario = fdb.child("Inventario").get()

    # Multiplicamos el stock por el precio para obtener el valor de los diferentes articulos en inventario
    inventory_data = {}
    for item in inventario.each():
        item_data = item.val()
        inventory_data[item_data['codigo']] = item_data['precio'] * item_data['estado']['9 de Octubre']['stock']

    # Realizamos el análisis ABC
    # Realizamos una sumatoria del total del costo del inventario
    total_value = sum(inventory_data.values())
    #Ordenamos los datos de manera descendente, lo usaremos en el grafico de valor de producto
    inventory_items = sorted(inventory_data.items(), key=lambda x: x[1], reverse=True)

    # Segun la formula del análsiis ABC para determinar en qué rango de porcentaje del valor acumulativo total se encuentra se usa lo siguiente:
    cumulative_value = 0
    abc_analysis = {}
    for item, value in inventory_items:
        cumulative_value += value
        if cumulative_value / total_value <= 0.8:
            abc_analysis[item] = 'A'
        elif cumulative_value / total_value <= 0.95:
            abc_analysis[item] = 'B'
        else:
            abc_analysis[item] = 'C'

    #Valores acumulados para grafica de tendencia
    cumulative_values = [sum([value for item, value in inventory_items][:i+1]) for i in range(len(inventory_items))]
    result = list(zip(range(len(inventory_data)), cumulative_values))

    category_start = 0

    #Envio los detalles de las secciones del grafico de tendencia
    rectangles = []
    for i in range(1, len(inventory_items)):
        if abc_analysis[inventory_items[i][0]] != abc_analysis[inventory_items[i-1][0]]:
            bottom_left = (category_start-0.4, cumulative_values[category_start])
            top_right = (i+0.4, cumulative_values[i-1])
            rectangles.append((bottom_left, top_right))
            category_start = i
    bottom_left = (category_start-0.4, cumulative_values[category_start])
    top_right = (len(inventory_items)-0.6, cumulative_values[-1])
    rectangles.append((bottom_left, top_right))

    print(abc_analysis)


    return render_template('abc.html', inventory_items=inventory_items, result=result, rectangles=rectangles, abc_analysis=abc_analysis)


#-----------------------------------------Filttrado de salidas-----------------------------------------------------
@app.route('/masvendido')
def masvendido():
    salidas = fdb.child("Salidas").get().val()

    salidas_tumbaco = salidas['9 de Octubre']

    filtdict = {}

    for key in salidas_tumbaco:
        documento = salidas_tumbaco[key]['documento']
        fecha = salidas_tumbaco[key]['fecha']
        productos = salidas_tumbaco[key]['productos']
        cantidades = salidas_tumbaco[key]['cantidades']
        filtdict[key] = {'documento': documento, 'fecha': fecha, 'productos': productos, 'cantidades': cantidades}

    print(filtdict)

    return render_template('filtrarsalida.html', filtdict=filtdict)


if __name__ == "__main__":
    app.run(debug=True)