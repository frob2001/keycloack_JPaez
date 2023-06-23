$(document).ready(function () {
    // Setup - add a text input to each header cell
    $('#example thead th:not(:last-child)').each(function () {
        var title = $(this).text();
        $(this).html('<input type="text" id="tableinput"/>' + "<h2>" + title + "</h2>")
    });

    $('#example2 thead th').each(function () {
        var title = $(this).text();
        $(this).html('<input type="text" id="tableinput"/>' + "<h2>" + title + "</h2>")
    });
    

    // DataTable
    var table = $('#example').DataTable({
        //orden de la busqueda, informacion, paginas y longitud de datos
        dom:"<'row'<'col-sm-12 col-md-6 my-2' fB><'col-sm-12 col-md-6'>>" +
        "<tr>" +
        "<'row'<'col-sm-12 col-md-5'ilp><'col-sm-12 col-md-7 my-2 text-right'>>",
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
                sortAscending:  "Presiona para ordenar de forma ascendente",
                sortDescending: "Presiona para ordenar de forma descendente"
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
        ],
        drawCallback: function () {
            // Personalizar los botones de paginación
            var pagination = $(this).closest('.dataTables_wrapper').find('.dataTables_paginate');

            pagination.find('a.paginate_button').addClass('btn btn-default');
            pagination.find('a.current').addClass('btn btn-primary');
            pagination.find('a.previous').html('&lt;');
            pagination.find('a.next').html('&gt;');

            // Eliminar los botones de paginación no deseados
            pagination.find('.ellipsis').remove();
            pagination.find('a.paginate_button:not(.previous):not(.next):not(.current)').remove();

            // Agregar el número de página "1", "2", "3" al inicio
            var firstPageButton = $('<a>', {
                href: '#',
                'class': 'paginate_button btn btn-default',
                'aria-controls': 'example',
                'data-dt-idx': '0',
                tabindex: '0'
            }).text('1');
            pagination.prepend(firstPageButton);

            // Agregar el número de página final al final
            var totalPages = Math.ceil(this.api().page.info().recordsTotal / this.api().page.len());
            var lastPageButton = $('<a>', {
                href: '#',
                'class': 'paginate_button btn btn-default',
                'aria-controls': 'example',
                'data-dt-idx': totalPages - 1,
                tabindex: '0'
            }).text(totalPages);
            pagination.append(lastPageButton);
        }
    });
    // DataTable
    var table = $('#example2').DataTable({
        //orden de la busqueda, informacion, paginas y longitud de datos
        dom:"<'row'<'col-sm-12 col-md-6 my-2' fB><'col-sm-12 col-md-6'>>" +
        "<tr>" +
        "<'row'<'col-sm-12 col-md-5'ilp><'col-sm-12 col-md-7 my-2 text-right'>>",
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
                sortAscending:  "Presiona para ordenar de forma ascendente",
                sortDescending: "Presiona para ordenar de forma descendente"
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
        ],
        drawCallback: function () {
            // Personalizar los botones de paginación
            var pagination = $(this).closest('.dataTables_wrapper').find('.dataTables_paginate');

            pagination.find('a.paginate_button').addClass('btn btn-default');
            pagination.find('a.current').addClass('btn btn-primary');
            pagination.find('a.previous').html('&lt;');
            pagination.find('a.next').html('&gt;');

            // Eliminar los botones de paginación no deseados
            pagination.find('.ellipsis').remove();
            pagination.find('a.paginate_button:not(.previous):not(.next):not(.current)').remove();

            // Agregar el número de página "1", "2", "3" al inicio
            var firstPageButton = $('<a>', {
                href: '#',
                'class': 'paginate_button btn btn-default',
                'aria-controls': 'example',
                'data-dt-idx': '0',
                tabindex: '0'
            }).text('1');
            pagination.prepend(firstPageButton);

            // Agregar el número de página final al final
            var totalPages = Math.ceil(this.api().page.info().recordsTotal / this.api().page.len());
            var lastPageButton = $('<a>', {
                href: '#',
                'class': 'paginate_button btn btn-default',
                'aria-controls': 'example',
                'data-dt-idx': totalPages - 1,
                tabindex: '0'
            }).text(totalPages);
            pagination.append(lastPageButton);
        }
    });
    $('#example').addClass('only-table');
    $('#example').wrap('<div class="only-table-wrapper"></div>');
    $('#example2').addClass('only-table');
    $('#example2').wrap('<div class="only-table-wrapper"></div>');
});

