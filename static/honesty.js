function submitForm(form_id) {
	var submitButton = document.getElementById('submit_button');	
	submitButton.setAttribute('disabled', 'true');
	document.getElementById(form_id).submit();
}