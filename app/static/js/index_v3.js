var data = (function(){
    var data;
    $.ajax({
        url: "/ajax/books/id-title?v=3",
        dataType: "json",
        async: false,
        success: function(response){
            var titles = [];
            var dict = [];
            $.each(response, function(key, val){
                var new_key = key.replace(/\s{2,}/g, ' ');
                titles.push(new_key);
                dict[new_key] = val;
            });
            data = [titles, dict];
        }
    });
    return data;
})();

var tags_data = (function(){
    var tags_data;
    $.ajax({
        url: "/ajax/tags",
        dataType: "json",
        async: false,
        success: function(response){
            tags_data = response;
        }
    });
    return tags_data;
})();

var book_titles = data[0];
var book_dict = data[1];

// init Bloodhound
var books_suggestions = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    //prefetch: { url: './data/clean_title_data.json' }
    local: book_titles
    //local: Object.keys(book_dict)
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
      source: books_suggestions
      //source: books_suggestions.ttAdapter()   // suggestion engine is passed as the source
    });

function validateMyForm(){
    return check();
}

//tagify part
var tagInput = document.querySelector('input[name=tags]'),
    // init Tagify script on the above inputs
    tagify = new Tagify(tagInput, {
        keepInvalidTags: false,
        maxTags: 10,
        whitelist : tags_data,
        blacklist : [] // <-- passed as an attribute in this demo
    });

// "remove all tags" button event listener
document.querySelector('.tags--removeAllBtn')
    .addEventListener('click', tagify.removeAllTags.bind(tagify))


//function to clean tag input
function clean_text(text){
    //.replace()
    return text.trim()
}

//function to get tags
function getCleanTags(){
    var raw_tag_list = tagify.value, 
    tags = "";
    raw_tag_list.forEach(function(tag_json) {
        tags = tags + clean_text(tag_json['value']) + " "
    }); 
    return tags
}

//function to render card
function renderCard(card_id){
    $(card_id).css("color", "#000000")
    $(card_id).css("border-radius", "10px");
    $(card_id).css("-webkit-box-shadow", "0 3px 3px #efefef");
    $(card_id).css("box-shadow", "0 3px 3px #efefef");
    $(card_id).css("border", "none");
    $(card_id).css("background-color", "rgba(255, 255, 255, 0.8)");
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
        titles = [book_t1, book_t2, book_t3, book_t4, book_t5], 
        id_title_dict = {}, 
        tags_inputed = getCleanTags();
    
    for (var i = 0; i < 5; i++){
        var id = "#card_" + (1 + i);
        if ((titles[i] !== "") && !(book_titles.includes(titles[i]))){
        //if ((titles[i] !== "") && !(titles[i] in book_dict)){
            check_valid = false;
            $(id).css("color", "red");
            document.getElementById('msg').innerHTML = "Please choose book names available in the suggestions";
        } else {
            if(titles[i] !== ""){
                id_list = id_list + (book_dict[titles[i]]) + " ";
            }
        }
    }

    if (check_valid && id_list !== "") {
        //alert(id_list);
        //$("#").value = id_list;
        document.getElementById('book_ids').value = id_list;
        document.getElementById('tags_inputed').value = tags_inputed;
        id_title_dict['1'] = book_t1;
        id_title_dict['2'] = book_t2;
        id_title_dict['3'] = book_t3;
        id_title_dict['4'] = book_t4;
        id_title_dict['5'] = book_t5;
        localStorage.setItem('id_title_dict', JSON.stringify(id_title_dict));
        return true;
    } else {
        return false;
    }
}

var next_empty_field = 1;

//function to change the
function add_book(i, title_inputed){
    var num = i.toString(),
    book_id = "#book_title_" + num,
    removeBtn = "#removeBtn_" + num,
    card = "#card_" + num,
    placeholder = "#title_placeholder_" + num;
    $(placeholder).css("display", "none");
    $(book_id).text(title_inputed);
    $(book_id).css("display", "block");
    $(removeBtn).css("visibility", "visible");
    renderCard(card);
}

//funciton to delete book field
function delete_book(i){
    //alert("delete")
    var num = i.toString(),
    book_id = "#book_title_" + num,
    removeBtn = "#removeBtn_" + num,
    card = "#card_" + num,
    placeholder = "#title_placeholder_" + num;
    $(placeholder).css("display", "inline-block");
    $(book_id).text("");
    $(book_id).css("display", "none");
    $(removeBtn).css("visibility", "hidden");
    $(card).css("border", "black 2px dashed");
    $(card).css("background-color", "transparent");
    $(card).css("color", "#000000");
}

//function to update value in book field
function update_book(i, title_inputed){
    var num = i.toString(),
    book_id = "#book_title_" + num,
    card = "#card_" + num;
    //alert(book_id);
    $(book_id).text(title_inputed);
    renderCard(card);
}

//remove button function
$("#removeBtn_1, #removeBtn_2, #removeBtn_3, #removeBtn_4, #removeBtn_5").click(function(){
    var i = parseInt($(this).attr('id')[$(this).attr('id').length-1]);
    //alert(i);
    var book_t1 = document.getElementById('book_title_1').innerText,
        book_t2 = document.getElementById('book_title_2').innerText,
        book_t3 = document.getElementById('book_title_3').innerText,
        book_t4 = document.getElementById('book_title_4').innerText,
        book_t5 = document.getElementById('book_title_5').innerText,
        titles = [book_t1, book_t2, book_t3, book_t4, book_t5],
        count = 0;
        //alert(titles);

        for (var k = 0; k < 5; k++){
            if (titles[k] !== ""){
                count++;
            }
        }

        if ((count-i) > 0){
            for (var j = i; j < count; j++){
                update_book(j, titles[j]);
            }
        }

        //alert(count);

        delete_book(count);
        next_empty_field = count;
});

//clear input function
function clearInput(){
    $('#input_title').val('');
    //document.getElementById("input_title").value = "";
}

//function to add a book title
function addBookLogic(){
    if (next_empty_field === 6 ){
        $("#msg2").css("color", "red");
        document.getElementById('msg2').innerHTML = "You can input up to 5 books";
    } else {
        var title_inputed = document.getElementById("input_title").value;
        if (title_inputed !== ""){
            add_book(next_empty_field, title_inputed);
            clearInput();
            next_empty_field++;
        }
    }
}

//clear the input when focus out
$('#input_title').focusout(function() {
    clearInput();
});

//press enter to add a book title
$('#input_title').keypress(function(event) {
    if (event.keyCode === 13 || event.which === 13) {
        addBookLogic();
        clearInput();
    }
});

// Collapse advanced search
$("#collapseExample").on("shown.bs.collapse", function () {
    $("a[role='button'][aria-controls='collapseExample']").html('Advanced Search <i class="fas fa-caret-up"></i>');
});
$("#collapseExample").on("hidden.bs.collapse", function () {
    $("a[role='button'][aria-controls='collapseExample']").html('Advanced Search <i class="fas fa-caret-down"></i>');
});

$(document).ready(function() {
    var id_title = localStorage.getItem('id_title_dict');
    if ( id_title != null && id_title !== ""){
        var obj = JSON.parse(id_title);
        Object.keys(obj).forEach(function(key) {
            if (obj[key] !== ""){
                next_empty_field = next_empty_field + 1;
                add_book(key,obj[key]);
            }
        })
    }

    // Update ratings
    $(".book-rating").each(function(index) {
        $(this).rateYo({
            starWidth: "15px",
            rating: $(this).data("source"),
            readOnly: true
        });
    });

    // Scroll to result
    if ($("#results-bookmark").length > 0) {
        $("#results-bookmark")[0].scrollIntoView({
            behavior: "smooth"
        });
    }
});


// Typewriter effect
// https://css-tricks.com/snippets/css/typewriter-effect/
var typewriter_words = [
    "novels", "science fiction", "love stories", "classics", "history",
    "memoirs", "fantasy", "poetry", "American literature", "contemporary civilization"
];

var TxtType = function(el, toRotate, period) {
    this.toRotate = toRotate;
    this.el = el;
    this.loopNum = 0;
    this.period = parseInt(period, 10) || 2000;
    this.txt = '';
    this.tick();
    this.isDeleting = false;
};

TxtType.prototype.tick = function() {
    var i = this.loopNum % this.toRotate.length;
    var fullTxt = this.toRotate[i];

    if (this.isDeleting) {
        this.txt = fullTxt.substring(0, this.txt.length - 1);
    } else {
        this.txt = fullTxt.substring(0, this.txt.length + 1);
    }

    this.el.innerHTML = '<span class="wrap">'+this.txt+'</span>';

    var that = this;
    var delta = 200 - Math.random() * 100;

    if (this.isDeleting) { delta /= 2; }

    if (!this.isDeleting && this.txt === fullTxt) {
        delta = this.period;
        this.isDeleting = true;
    } else if (this.isDeleting && this.txt === '') {
        this.isDeleting = false;
        this.loopNum++;
        delta = 500;
    }

    setTimeout(function() {
        that.tick();
    }, delta);
};

window.onload = function() {
    var elements = document.getElementsByClassName('typewrite');
    for (var i=0; i<elements.length; i++) {
        var toRotate = typewriter_words;
        var period = elements[i].getAttribute('data-period');
        if (toRotate) {
            new TxtType(elements[i], toRotate, period);
        }
    }
    // INJECT CSS
    var css = document.createElement("style");
    css.type = "text/css";
    css.innerHTML = ".typewrite > .wrap { border-right: 0.08em solid #fff}";
    document.body.appendChild(css);
};
