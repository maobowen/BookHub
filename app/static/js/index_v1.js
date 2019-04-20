var data = (function(){
    var data;
    $.ajax({
        url: "/ajax/books/id-title",
        dataType: "json",
        async: false,
        success: function(response){
            var titles = [];
            var dict = [];
            $.each(response, function(key, val){
                titles.push(key);
                dict[key] = val;
            });
            data = [titles, dict];
        }
    });
    return data;
})();

//console.log(data);

var book_titles = data[0];
var book_dict = data[1];

//console.log(book_dict);
//console.log(book_titles);

// init Bloodhound
var books_suggestions = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    //prefetch: { url: './data/clean_title_data.json' }
    local: book_titles
});

// init Typeahead
$('#book_title_1, #book_title_2, #book_title_3, #book_title_4, #book_title_5').typeahead(
    {
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
      name: 'books',
      source: books_suggestions
      //source: books_suggestions.ttAdapter()   // suggestion engine is passed as the source
    });

function validateMyForm(){
    return check();
}

//check function
function check(){
    var book_t1 = document.getElementById('book_title_1').value,
        book_t2 = document.getElementById('book_title_2').value,
        book_t3 = document.getElementById('book_title_3').value,
        book_t4 = document.getElementById('book_title_4').value,
        book_t5 = document.getElementById('book_title_5').value,
        check_valid = true,
        id_list = "",
        titles = [book_t1, book_t2, book_t3, book_t4, book_t5];
        //console.log(titles);
        //console.log(book_titles.includes(titles[0]));


    for (var i = 0; i < 5; i++){
        var id = "#book_title_" + (1 + i);
        if ((titles[i] !== "") && !(book_titles.includes(titles[i]))){
            console.log(i);
            check_valid = false;
            $(id).css("border-color", "red");
            document.getElementById('msg').innerHTML = "Please choose book names in the suggestion";
        } else {
            if(titles[i] !== ""){
                console.log(book_dict[titles[i]][0]);
                $(id).css("border-color", "grey");
                id_list = id_list + (book_dict[titles[i]][0]) + " ";
            }
        }
    }

    if (check_valid && id_list !== "") {
        console.log(id_list);
        //$("#").value = id_list;
        document.getElementById('book_ids').value = id_list;
        return true;
    } else {
        return false;
    }
}
