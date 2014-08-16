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


$(document).ready(function() {
	function updateForm() {
		if (!$('#code-input').val())
		{
			$('#code-submission').attr("disabled", "disabled");
		}
		else
		{
			$('.code-submission').removeAttr("disabled");
		}
	}

	function closeFeedback() {
		var ul = document.getElementById("errorlist");
		var items = ul.getElementsByTagName("li");
		var itemLength = items.length;
		while(items.length) {
			items[0].remove();
		}
	}

	$('input[type=file]').bootstrapFileInput();

	// hide navigation if not logged in
	if (window.location.href.indexOf('login') > -1) {
		$('.navigation').hide();
	}

	$('.closeBtn').on("click", function() {
		closeFeedback();
	});

	$('#code-input').on("change", function(){ 
 		updateForm(); 
	});

	updateForm();

    $('#upload-file-btn').click(function() {
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/uploadajax',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function(data) {
                console.log('Success!');
				$.each(
					data.errors,
					function(i,v) {
						if(!v.search("Grading ")) {
							$("#errorlist").append("<li><h4>" + v + "</h4></li>") ;
						} else {
							$("#errorlist").append("<li class='message-error'>" + v + "</li>");
					}
					console.log(v);
					}
				);
                if (data.errors.length === 1)
                {
                	// no errors
                	$("#errorlist").append("<li class='message-success'>No errors have been found! :)</li>");
                }
			},
		});
	});
});


