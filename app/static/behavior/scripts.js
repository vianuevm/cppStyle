YAHOO.util.Event.onDOMReady(function() {

    // initialize Konami Code
    if (typeof(Konami) != "undefined")
    {
        var konami = new Konami();
        konami.pattern = "384069696783495651";
        konami.code = function() {
            alert("You have unlimited submits!");
        };
        konami.load();
    }

});


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
