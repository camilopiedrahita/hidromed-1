/* Project specific Javascript goes here. */
$(document).ready(function(){
	var form = $('.form-container form');
	form.on('submit',function(){
		$('.btn-primary').attr('disabled','disabled');
	})
});
