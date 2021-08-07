function callAddFunc(){
    // read user input and write it to a json object
    var id = document.getElementsByName('productID')[0]['value'];
    var category = document.getElementsByName('category')[0]['value'];
    var price = document.getElementsByName('price')[0]['value'];
    var params = {
        "productID": id,
        "category": category,
        "price": price
    };
    //send post request to python application
    $.ajax({
        url: "/addProd/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(params),
        complete: function(xhr, status){
            document.getElementById("form").innerHTML = xhr.responseText;
            console.log(xhr.responseText);
        }
    });
}