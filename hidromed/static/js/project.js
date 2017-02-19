//opciones de perido datos
var hora = {
	'1': 'Cada minuto',
	'2': 'Cada 15 minutos'
};

var dia = {
	'1': 'Cada minuto',
	'2': 'Cada 15 minutos',
	'3': 'Cada hora'
};

var semana = {
	'4': 'Cada día'
};

var mes = {
	'4': 'Cada día',
	'5': 'Cada semana'
};

var tres_meses = {
	'5': 'Cada semana',
	'6': 'Cada mes'
};

var anho = {
	'6': 'Cada mes'
};

var error = {
	'0': 'El periodo de datos no puede ser superior a un año'
};

//funcion detectar fechas
function PeriodoDatosFecha(){

	if ($('#id_desde').val() != '' && $('#id_hasta').val() != '' 
		&& $('#id_tipo_de_filtro').val() == '7'){
		//mostrar seleccion de tipo de filtro
		$('#periodo_datos').show();

		//obtener fechas
		var desde = FormatFecha($('#id_desde').val());
		var hasta = FormatFecha($('#id_hasta').val());
		var diferencia = daydiff(desde, hasta);

		//asignar valores segun seleccion
		if (diferencia == 0 ){ peridos('2'); }
		else if (diferencia >= 1 && diferencia < 30 ){ peridos('3'); }
		else if (diferencia >= 30 && diferencia < 90 ){ peridos('4'); }
		else if (diferencia >= 90 && diferencia < 360 ){ peridos('5'); }
		else if (diferencia == 365 ){ peridos('6'); }
		else if (diferencia > 365 ){ peridos('error'); }
	}
}

//oculatar fechas segun seleccion del tipo de filtro
function ocultar(value){
	if(value == '7') { 
		$('#fechas').show(); 
		$('#periodo_datos').hide();
	}
    else { 
    	$('#fechas').hide(); 
    	$('#periodo_datos').show();
    }
}

//modificar opciones de periodo de datos
function peridos(value){

	//eliminar opciones anteriores
	$('#id_periodo_datos').empty();

	//asignar opciones segun valor del tipo de filtro
	if (value != '7') { 

		//diccionario de opciones segun valor del tipo de filtro
		if (value == '1') { newOptions = hora; }
		else if (value == '2') { newOptions = dia; }
		else if (value == '3') { newOptions = semana; }
		else if (value == '4') { newOptions = mes; }
		else if (value == '5') { newOptions = tres_meses; }
		else if (value == '6') { newOptions = anho; }
		else if (value == 'error') { newOptions = error; }

		//asignar nuevos valores
		if (typeof newOptions !== 'undefined') {
			$.each(newOptions, function(key,value) {
			  $('#id_periodo_datos').append($("<option></option>")
			     .attr("value", key).text(value));
			});
		}
	}
}

//funciones del select tipo de filtro
$(function() {
    $('#id_tipo_de_filtro').change(function(){

    	//oculatar fechas segun seleccion del tipo de filtro
    	ocultar($('#id_tipo_de_filtro').val());

    	//cambiar choices de periodo de datos
   		peridos($('#id_tipo_de_filtro').val());	
    	PeriodoDatosFecha();
    	
    });
});

//formatear fecha
function FormatFecha(str){
	return new Date(str)
}

//diferencia de dias
function daydiff(first, second) {
    return Math.round((second-first)/(1000*60*60*24));
}

//detectar cambios en los campos de fecha
$(function(){
	$('#id_hasta').change(function(){
		PeriodoDatosFecha();
	});
	$('#id_desde').change(function(){
		PeriodoDatosFecha();
	});
});

//cambiar select formulario medidores
function medidores(){

	//vaciar campos
	$('#id_hijos').empty();
	$('#id_padre').empty();

	//asignacion de variables
	padre_field = $('#id_padre');
	hijos_field = $('#id_hijos');

	//validacion cambios en el documento
	$('#medidores-form').each(function(index, el) {
		$('select', this).change(function() {
			changed_item = $(this);
			if (changed_item.is('#id_medidor')) {
				if ($('#id_medidor').val() != '') {

					//vaciar campos
					$('#id_hijos').empty();

					//poblar datos del campo padre
					medidor_id = $('#id_medidor').val();
					padre_field.load('/ajax/load_medidores/?medidor=' + medidor_id);
				}
				else { 

					//vaciar campos
					$('#id_padre').empty();
					$('#id_hijos').empty();
				}
			}
			else if (changed_item.is('#id_padre')) {
				if ($('#id_padre').val() != '') {

					//poblar datos del campo hijos
					medidor_id = $('#id_medidor').val();
					padre_id = $('#id_padre').val();
					hijos_field.load('/ajax/load_medidores/?medidor=' + medidor_id + '&padre=' + padre_id);
				}	
				else { 

					//vaciar campos
					$('#id_hijos').empty(); 
				}
			}
		});
	});
}

//main
$(document).ready(function(){
	var form = $('.form-container form');
	form.on('submit',function(){
		$('.btn-primary').attr('disabled','disabled');
	})

	//call funciones del documento
	ocultar($('#id_tipo_de_filtro').val());
	peridos($('#id_tipo_de_filtro').val());
	PeriodoDatosFecha();
	medidores();
});