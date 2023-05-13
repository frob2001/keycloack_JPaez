from flask import Flask, render_template, request, redirect, url_for, flash, session
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
    return redirect(url_for('sucursales'))
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

@app.route('/actualizarsucursal/<string:key>', methods=["GET", "POST"])
@login_required
def actualizar_sucursal(key):
  campo = fdb.child("Sucursales").child(key).get().val()
  if request.method == "POST":
    nombre = request.form["nombre"]
    direccion = request.form["direccion"]
    fdb.child("Sucursales").child(key).update({"nombre": nombre, "direccion": direccion})
    flash("La sucursal ha sido modificada con éxito")
    return redirect(url_for('detalles_sucursal', key=key))
  else:
    return render_template('actualizarSucursal.html', key=key, campo=campo)

@app.route('/eliminarsucursal/<string:key>')
@login_required
def eliminar_sucursal(key):
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
                fdb.child("Usuarios").child(user['localId']).set({
                    "nombre": nombre,
                    "apellido": apellido,
                    "email": email,
                    "role": role
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
  datos = fdb.child("Inventario").get().val()
  print(datos)
  return render_template("inventario.html", datos=datos)


@app.route('/crear_producto/', methods=["GET", "POST"])
@login_required
def crear_producto():
    if request.method == "POST":
        codigo = request.form["codigo"]
        descripcion = request.form["descripcion"]
        oems = request.form["oems"]
        marca = request.form["marca"]
        referencia = request.form["referencia"]
        precio = float(request.form["precio"])
        precioiva = float(request.form["precio"])*1.12
        ubicacion = request.form["ubicacion"]
        ubicacionespecifica = request.form["ubicacionespecifica"]
        stock = request.form["stock"]

        datos = fdb.child("Inventario").get().val()
        codigos = [""]
        print(datos) #Devuelve none en caso de no tener datos
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
            "ubicacion": ubicacion,
            "ubicacionespecifica": ubicacionespecifica,
            "stock": stock
        })
        return redirect(url_for('inventario'))
    else:
       return render_template("agregar_inventario.html")

@app.route('/detalles_producto/<string:key>')
@login_required
def detalles_producto(key):
    campo = fdb.child('Inventario').child(key).get().val()
    return render_template('detalles_inventario.html', key=key, campo=campo)

@app.route('/actualizar_producto/<string:key>', methods=["GET", "POST"])
@login_required
def actualizar_producto(key):
  campo = fdb.child("Inventario").child(key).get().val()
  if request.method == "POST":
    codigo = request.form["codigo"]
    descripcion = request.form["descripcion"]
    oems = request.form["oems"]
    marca = request.form["marca"]
    referencia = request.form["referencia"]
    precio = float(request.form["precio"])
    precioiva = float(request.form["precio"])*1.12
    ubicacion = request.form["ubicacion"]
    ubicacionespecifica = request.form["ubicacionespecifica"]
    stock = request.form["stock"]
    fdb.child("Inventario").child(key).update({
            "codigo": codigo,
            "descripcion": descripcion,
            "oems": oems,
            "marca": marca,
            "referencia": referencia,
            "precio": precio,
            "precioiva": precioiva,
            "ubicacion": ubicacion,
            "ubicacionespecifica": ubicacionespecifica,
            "stock": stock
        })
    flash("El producto se ha sido modificado con éxito")
    return redirect(url_for('detalles_producto', key=key))
  else:
    return render_template('actualizar_inventario.html', key=key, campo=campo)

@app.route('/eliminar_producto/<string:key>')
@login_required
def eliminar_producto(key):
    fdb.child("Inventario").child(key).remove()
    flash("El producto se ha sido eliminado con éxito")
    return redirect(url_for('inventario'))

if __name__ == "__main__":
    app.run(debug=True)