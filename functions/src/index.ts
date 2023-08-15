import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';

admin.initializeApp();

exports.actualizarProductosConNuevaSucursal = functions.database.ref('/Sucursales/{sucursalId}')
    .onCreate(async (snapshot, context) => {
        const nuevaSucursalNombre = snapshot.child('nombre').val();

        const productosRef = admin.database().ref('/Productos');
        const productosSnapshot = await productosRef.once('value');

        productosSnapshot.forEach(productoSnapshot => {
            const productoId = productoSnapshot.key;
            const productoRef = productosRef.child(`${productoId}/estado/${nuevaSucursalNombre}`);

            productoRef.set({
                stock: 0,
                ubicacion: 'N/A',
                ubicacionespecifica: 'N/A'
            });
        });

        return null;
    });
