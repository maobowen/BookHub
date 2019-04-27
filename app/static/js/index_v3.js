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
        maxTags: 5,
        whitelist : ["A# .NET", "A# (Axiom)", "A-0 System", "A+", "A++", "ABAP", "ABC", "ABC ALGOL", "ABSET", "ABSYS", "ACC", "Accent", "Ace DASL", "ACL2", "Avicsoft", "ACT-III", "Action!", "ActionScript", "Ada", "Adenine", "Agda", "Agilent VEE", "Agora", "AIMMS", "Alef", "ALF", "ALGOL 58", "ALGOL 60", "ALGOL 68", "ALGOL W", "Alice", "Alma-0", "AmbientTalk", "Amiga E", "AMOS", "AMPL", "Apex (Salesforce.com)", "APL", "AppleScript", "Arc", "ARexx", "Argus", "AspectJ", "Assembly language", "ATS", "Ateji PX", "AutoHotkey", "Autocoder", "AutoIt", "AutoLISP / Visual LISP", "Averest", "AWK", "Axum", "Active Server Pages", "ASP.NET", "B", "Babbage", "Bash", "BASIC", "bc", "BCPL", "BeanShell", "Batch (Windows/Dos)", "Bertrand", "BETA", "Bigwig", "Bistro", "BitC", "BLISS", "Blockly", "BlooP", "Blue", "Boo", "Boomerang", "Bourne shell (including bash and ksh)", "BREW", "BPEL", "B", "C--", "C++ – ISO/IEC 14882", "C# – ISO/IEC 23270", "C/AL", "Caché ObjectScript", "C Shell", "Caml", "Cayenne", "CDuce", "Cecil", "Cesil", "Céu", "Ceylon", "CFEngine", "CFML", "Cg", "Ch", "Chapel", "Charity", "Charm", "Chef", "CHILL", "CHIP-8", "chomski", "ChucK", "CICS", "Cilk", "Citrine (programming language)", "CL (IBM)", "Claire", "Clarion", "Clean", "Clipper", "CLIPS", "CLIST", "Clojure", "CLU", "CMS-2", "COBOL – ISO/IEC 1989", "CobolScript – COBOL Scripting language", "Cobra", "CODE", "CoffeeScript", "ColdFusion", "COMAL", "Combined Programming Language (CPL)", "COMIT", "Common Intermediate Language (CIL)", "Common Lisp (also known as CL)", "COMPASS", "Component Pascal", "Constraint Handling Rules (CHR)", "COMTRAN", "Converge", "Cool", "Coq", "Coral 66", "Corn", "CorVision", "COWSEL", "CPL", "CPL", "Cryptol", "csh", "Csound", "CSP", "CUDA", "Curl", "Curry", "Cybil", "Cyclone", "Cython", "M2001", "M4", "M#", "Machine code", "MAD (Michigan Algorithm Decoder)", "MAD/I", "Magik", "Magma", "make", "Maple", "MAPPER now part of BIS", "MARK-IV now VISION:BUILDER", "Mary", "MASM Microsoft Assembly x86", "MATH-MATIC", "Mathematica", "MATLAB", "Maxima (see also Macsyma)", "Max (Max Msp – Graphical Programming Environment)", "Maya (MEL)", "MDL", "Mercury", "Mesa", "Metafont", "Microcode", "MicroScript", "MIIS", "Milk (programming language)", "MIMIC", "Mirah", "Miranda", "MIVA Script", "ML", "Model 204", "Modelica", "Modula", "Modula-2", "Modula-3", "Mohol", "MOO", "Mortran", "Mouse", "MPD", "Mathcad", "MSIL – deprecated name for CIL", "MSL", "MUMPS", "Mystic Programming L"],
        blacklist : [".NET", "PHP"] // <-- passed as an attribute in this demo
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
    alert(raw_tag_list)
    alert(tags)
    return tags
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
    $(card).css("color", "#000000");
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
    $(card).css("color", "#000000")
}

//function to update value in book field
function update_book(i, title_inputed){
    var num = i.toString(),
    book_id = "#book_title_" + num,
    card = "#card_" + num;
    //alert(book_id);
    $(book_id).text(title_inputed);
    $(card).css("color", "#000000");
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
})

//clear input function
function clearInput(){
    $('#input_title').val('');
    //document.getElementById("input_title").value = "";
}

//function to add a book title
function addBookLogic(){
    if (next_empty_field === 6 ){
        document.getElementById('msg').innerHTML = "You can input up to 5 books";
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
});

/*
// Chainable event listeners
tagify.on('add', onAddTag)
      .on('remove', onRemoveTag)
      .on('input', onInput)
      .on('edit', onTagEdit)
      .on('invalid', onInvalidTag)
      .on('click', onTagClick);

// tag added callback
function onAddTag(e){
    console.log("onAddTag: ", e.detail);
    console.log("original input value: ", input.value)
    tagify.off('add', onAddTag) // exmaple of removing a custom Tagify event
}

// tag remvoed callback
function onRemoveTag(e){
    console.log(e.detail);
    console.log("tagify instance value:", tagify.value)
}

// on character(s) added/removed (user is typing/deleting)
function onInput(e){
    console.log(e.detail);
    console.log("onInput: ", e.detail);
}

function onTagEdit(e){
    console.log("onTagEdit: ", e.detail);
}

// invalid tag added callback
function onInvalidTag(e){
    console.log("onInvalidTag: ", e.detail);
}

// invalid tag added callback
function onTagClick(e){
    console.log(e.detail);
    console.log("onTagClick: ", e.detail);
}

*/