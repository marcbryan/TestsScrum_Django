(function($){
  $(function(){

	var collapsibleElem = document.querySelector('.collapsible');
  	var collapsibleInstance = M.Collapsible.init(collapsibleElem, {});

	//$('select').formSelect();
    $('.sidenav').sidenav();
    $(".dropdown-trigger").dropdown({hover:true, alignement: "right", constrainWidth: true});



  }); // end of document ready
})(jQuery); // end of jQuery name space
