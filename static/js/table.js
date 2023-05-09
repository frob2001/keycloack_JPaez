$(document).ready(function () {
    // Setup - add a text input to each header cell
    $('#example thead th:not(:last-child)').each(function () {
        var title = $(this).text();
        $(this).html('<input type="text" id="tableinput" placeholder="Buscar por ' + title + '" />' + "<h2>" + title + "</h2>")
    });
    

    // DataTable
    var table = $('#example').DataTable({
        //orden de la busqueda, informacion, paginas y longitud de datos
        dom:"<'row'<'col-sm-12 col-md-6 my-2' fB><'col-sm-12 col-md-6'>>" +
        "<'row'<'col-sm-12'tr>>" +
        "<'row'<'col-sm-12 col-md-5'il><'col-sm-12 col-md-7 my-2 text-right'p>>",
        buttons: [
            'excel', 'print'
        ],
        "lengthMenu": [ [10, 25, 50, -1], [10, 25, 50, "All"] ],

        initComplete: function () {
            // Apply the search
            this.api()
                .columns()
                .every(function () {
                    var that = this;

                    $('input', this.header()).on('keyup change clear', function () {
                        if (that.search() !== this.value) {
                            that.search(this.value).draw();
                        }
                    });
                });
        },
        language: {
            processing:     "Cargando...",
            search:         "Buscar: ",
            lengthMenu:     "Mostrar:_MENU_",
            info:           "Mostrando _START_ a _END_ de _TOTAL_ elementos",
            infoEmpty:      "Mostrando 0 a 0 de 0 elementos",
            infoFiltered:   "(filtrado de _MAX_ elementos en total)",
            infoPostFix:    "",
            loadingRecords: "Cargando...",
            zeroRecords:    "No hay elementos",
            emptyTable:     "No hay elementos (tabla vacía)",
            paginate: {
                first:      "Primero",
                previous:   "<",
                next:       ">",
                last:       "Último"
            },
            aria: {
                sortAscending:  ": activer pour trier la colonne par ordre croissant",
                sortDescending: ": activer pour trier la colonne par ordre décroissant"
            }
        },
        buttons: [
            {
                extend: 'excelHtml5',
                exportOptions: {
                    columns: ':not(:last-child)'
                }
            },
            {
                extend: 'print',
                exportOptions: {
                    columns: ':not(:last-child)'
                }
            }
        ]
    });
});

