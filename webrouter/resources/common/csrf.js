$.ajaxSetup({
    beforeSend: function(xhr,settings) {
      //retrieve csrf token if needed
      if (settings && settings.hasOwnProperty("type")
          && settings.type !== "GET"){
          var token = getCSRFToken();
        xhr.setRequestHeader("X-CSRF-Token", token);    //add it to the headers
      }
    }
});

//actual request to get the csrf token
function getCSRFToken() {
    var token = null;
    $.ajax({
        url: "/",
        type: "GET",
        async: false,
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRF-Token", "Fetch");
        },
        complete: function(xhr) {
            token = xhr.getResponseHeader("X-CSRF-Token");
        }
    });
    return token;
}