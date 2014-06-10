function handleFormSubmit(){
	var submitButton = document.getElementById('submit_button');	
	submitButton.setAttribute('disabled', 'true');
	document.getElementById('buy_form').submit();
}