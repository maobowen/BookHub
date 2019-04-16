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
//$('#book_title_1, #book_title_2, #book_title_3, #book_title_4, #book_title_5').typeahead(
$('#input_title').typeahead(
    {
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
      name: 'books',
      source:books_suggestions
      //source: books_suggestions.ttAdapter()   // suggestion engine is passed as the source
    });

function validateMyForm(){
    return check();
}

//check function
function check(){
    var book_t1 = document.getElementById('book_title_1').innerText,
        book_t2 = document.getElementById('book_title_2').innerText,
        book_t3 = document.getElementById('book_title_3').innerText,
        book_t4 = document.getElementById('book_title_4').innerText,
        book_t5 = document.getElementById('book_title_5').innerText,
        check_valid = true,
        id_list = "",
        titles = [book_t1, book_t2, book_t3, book_t4, book_t5];
        //alert(titles);
        //console.log(book_titles.includes(titles[0]));

    for (var i = 0; i < 5; i++){
        var id = "#card_" + (1+i);
        if ((titles[i] !== "") && !(book_titles.includes(titles[i]))){
            console.log(i);
            check_valid = false;
            $(id).css("border-color", "red");
            $(id).css("color", "red");
            document.getElementById('msg').innerHTML = "Please choose book names available in the suggestions";
        } else {
            if(titles[i] !== ""){
                console.log(book_dict[titles[i]][0]);
                $(id).css("border-color", "grey");
                id_list = id_list + (book_dict[titles[i]][0]) + " ";
            }
        }
    }

    if (check_valid && id_list !== "") {
        //alert(id_list);
        //$("#").value = id_list;
        document.getElementById('book_ids').value = id_list;
        return true;
    } else {
        return false;
    }
}

var next_empty_field = 1

//function to change the 
function add_book(i, title_inputed){
    var num = i.toString(), 
    book_id = "#book_title_" + num, 
    removeBtn = "#removeBtn_" + num, 
    card = "#card_" + num,
    placeholder = "#title_placeholder_" + num
    $(placeholder).css("display", "none")
    $(book_id).text(title_inputed)
    $(book_id).css("display", "block")
    $(removeBtn).css("visibility", "visible")
    $(card).css("border", "2px solid #808080")
    $(card).css("color", "#808080")     
}

//funciton to delete book field
function delete_book(i){
    //alert("delete")
    var num = i.toString(), 
    book_id = "#book_title_" + num, 
    removeBtn = "#removeBtn_" + num, 
    card = "#card_" + num,
    placeholder = "#title_placeholder_" + num
    $(placeholder).css("display", "inline-block")
    $(book_id).text("")
    $(book_id).css("display", "none")
    $(removeBtn).css("visibility", "hidden")
    $(card).css("border", "2px dashed #d3d3d3")
    $(card).css("color", "#d3d3d3") 
}

//function to update value in book field
function update_book(i, title_inputed){
    var num = i.toString(), 
    book_id = "#book_title_" + num
    //alert(book_id)
    $(book_id).text(title_inputed)
}

//remove button function
$("#removeBtn_1, #removeBtn_2, #removeBtn_3, #removeBtn_4, #removeBtn_5").click(function(){
    var i = parseInt($(this).attr('id')[$(this).attr('id').length-1])
    //alert(i)
    var book_t1 = document.getElementById('book_title_1').innerText,
        book_t2 = document.getElementById('book_title_2').innerText,
        book_t3 = document.getElementById('book_title_3').innerText,
        book_t4 = document.getElementById('book_title_4').innerText,
        book_t5 = document.getElementById('book_title_5').innerText, 
        titles = [book_t1, book_t2, book_t3, book_t4, book_t5], 
        count = 0
        //alert(titles)
        
        for (var k=0; k<5; k++){
            if (titles[k] != ""){
                count = count + 1
            }
        }

        if ((count-i) > 0){
            for (var j=i; j < count; j++){
                update_book(j, titles[j])
            }
        }

        //alert(count)

        delete_book(count)
        next_empty_field = count
})

//clear input function
function clearInput(){
    $('#input_title').val('')
    //document.getElementById("input_title").value = ""
}

//press enter to add a book title
$('#input_title').keypress(function(event) {
    if (event.keyCode == 13 || event.which == 13) {
        if (next_empty_field == 6 ){
            document.getElementById('msg').innerHTML = "You can input up to 5 books";
        } else {
            var title_inputed = document.getElementById("input_title").value
            if (title_inputed != ""){
                add_book(next_empty_field, title_inputed)
                clearInput()
                next_empty_field = next_empty_field + 1
            }
        }
    }
});

