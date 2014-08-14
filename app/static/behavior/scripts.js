$(document).ready(function()
{
	$('input[type=file]').bootstrapFileInput();

	// hide navigation if not logged in
	if (window.location.href.indexOf('login') > -1)
	{
		$('.navigation').hide();
	}

	updateForm();
	$('#code-input').on("change", function(){ updateForm(); });
});

function updateForm()
{
	if (!$('#code-input').val())
	{
		$('#code-submission').attr("disabled", "disabled");
	}
	else
	{
		$('#code-submission').removeAttr("disabled");
	}
}
