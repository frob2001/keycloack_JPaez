from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from config import auth, fdb

app = Flask(__name__)
app.secret_key = "felimax2"

#Commit test


#Verifica el login
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
    return redirect(url_for('inventariogeneral'))
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


@app.route('/sidebar/')
def sidebar():
    return render_template('sidebar.html')


#Actualización a Firebase

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
    nombre = fdb.child("Sucursales").child(key).child("nombre").get().val()
    print(nombre)
    fdb.child("Sucursales").child(key).remove()
    datos = fdb.child("Inventario").get().val()
    for nkey, value in datos.items():
      print(nkey + ": " + str(value["stock_prod"]))
      fdb.child("Inventario").child(nkey).child("stock_prod").child(nombre).remove()
      fdb.child("Inventario").child(nkey).child("ubi_prod").child(nombre).remove()
    flash("La sucursal ha sido eliminada con éxito")
    return redirect(url_for('sucursales'))

@app.route('/agregarsucursal/', methods=["GET", "POST"])
@login_required
def agregar_sucursal():
    if request.method == "POST":
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        nueva_sucursal = {"nombre": nombre, "direccion": direccion}


        datos = fdb.child("Sucursales").get().val()
        nombres = [d['nombre'] for d in datos.values()]

        if nombre in nombres:
           return render_template('agregarSucursal.html', message='La sucursal ya existe.')
        else:
           fdb.child("Sucursales").push(nueva_sucursal)
           datos = fdb.child("Inventario").get().val()
           for key, value in datos.items():
              print(key + ": " + str(value["stock_prod"]))
              fdb.child("Inventario").child(key).child("stock_prod").child(nombre).set(0)
              fdb.child("Inventario").child(key).child("ubi_prod").child(nombre).set("")
           flash("La sucursal se agregó correctamente")
        return redirect(url_for('sucursales'))
    else:
       return render_template("agregarSucursal.html")

@app.route('/detallessucursal/<string:key>')
@login_required
def detalles_sucursal(key):
    campo = fdb.child('Sucursales').child(key).get().val()
    return render_template('detallesSucursales.html', key=key, campo=campo)


#-----------------------------------------MANEJO DE INVENTARIO-----------------------------------------------------

@app.route("/inventariogeneral/")
@login_required
def inventariogeneral():
   sucursales = fdb.child("Sucursales").get().val()
   nom_sucursal = []
   for value in sucursales.values():
    nom_sucursal.append(value['nombre'])
   #print(nom_sucursal)
   datos = fdb.child("Inventario").get().val()
   for key, value in datos.items():
      print(key + ": " + str(value["stock_prod"]))
   return render_template("inventariogeneral.html", nom_sucursal=nom_sucursal, datos=datos)


@app.route('/agregarproducto/', methods=["GET", "POST"])
@login_required
def agregarproducto():
    #Consigo los nombres de las sucursales:
    sucursales = fdb.child("Sucursales").get().val()
    nom_sucursal = []
    for value in sucursales.values():
       nom_sucursal.append(value['nombre'])
    if request.method == "POST":
        cod_producto = request.form["cod_producto"]
        descripcion = request.form["descripcion"]
        marca = request.form["marca"]
        referencia = request.form["referencia"]
        precio = round(float(request.form["precio"]),2)
        precio_iva = round(float(precio) * 1.12, 2)

        #Ordeno los OEMS en un diccionario
        gen_values = []  # Lista para almacenar los valores de los inputs en la columna "Código general"
        for key in request.form.keys():
          if key.startswith("gen"):
            gen_values.append(request.form[key])

        oems = {}
        
        for x  in range(1, len(gen_values)+1):
          print(x)
          list = []
          for key in request.form.keys():
              if key.startswith("gen"+str(x)) | key.startswith("sub"+str(x)) :
                list.append(request.form[key])
              oems[x-1] = list  
          

        
        #Pido los stocks de cada sucursal
        stock_prod = {}
        for value in nom_sucursal:
           new_value = str(value).replace(" ", "_")
           stock_prod[value] = int(request.form.get("stock_"+str(new_value), 0))

        ubi_prod = {}
        for value in nom_sucursal:
           new_value = str(value).replace(" ", "_")
           ubi_prod[value] = request.form.get("ubi_"+str(new_value), 0)

        nuevo_producto = {"cod_producto": cod_producto, "descripcion": descripcion, "marca": marca, "referencia": referencia, "precio": precio, "precio_iva": precio_iva, "oems":oems, "stock_prod": stock_prod, "ubi_prod": ubi_prod}

        fdb.child("Inventario").push(nuevo_producto)
        flash("El producto se añadió correctamente")
        return redirect(url_for('inventariogeneral'))
    else:
       return render_template("agregarProducto.html", nom_sucursal=nom_sucursal) #Crear agregar productos



if __name__ == "__main__":
    app.run(debug=True)