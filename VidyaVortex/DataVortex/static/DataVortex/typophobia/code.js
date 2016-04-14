"use strict";

var typist = {
    KEY_SPACE : 32,
    words: [],
    current_word_index: 0,
    correct_words: 0,
    secondselapsed: 0,
    
    /* Uses arrays and join()
     * can be used as stringbuilder is javascript. */
    highlight: function() {        
        var htmlArr = [];
        for(var i = 0; i < typist.current_word_index; i++) {
            htmlArr.push(typist.words[i]);
        }
        htmlArr.push("<span class='highlight'>");
        htmlArr.push(typist.words[typist.current_word_index]);
        htmlArr.push("</span>");
        
        for(i = (typist.current_word_index + 1); i < typist.words.length; i++) {
            htmlArr.push(typist.words[i]);
        }
        
        $("section p").html(htmlArr.join(" "));
    }
};

$(document).ready(function() {
    $("#inputter").focus();
    typist.words = $("section p").html().split(" ");
    typist.highlight();
    
    /* the word that is currently being typed can be found from 
      typist.words -list index typist.current_word_index
    */
   
   
    $("#inputter").keyup(function(){
        
        document.onkeyup = (

            function checkKey(e) 
            {   
                e = e || window.event;

                if(e.keyCode==typist.KEY_SPACE)
                {
                    //alert(typist.words[typist.current_word_index]);
                    if($("#inputter").val().split(" ").join("") == typist.words[typist.current_word_index]){
                           typist.correct_words++;
                           $("#correct").html(typist.correct_words);
                    }
                    if(typist.current_word_index == typist.words.length-1){
                        var c = confirm("WPM: "+ typist.correct_words/(typist.secondselapsed/60)+"\nCorrect words: " + typist.correct_words + "\nTime: " + typist.secondselapsed + " seconds" + "\nSubmit score?");
                        if(c) {
                            var msg = {
                                "messageType": "SCORE",
                                "score": typist.correct_words/(typist.secondselapsed/60)
                            };
                            window.parent.postMessage(msg, "*");
                        }
                        location.reload();
                    }
                    typist.current_word_index++;
                    var WPM = typist.correct_words/(typist.secondselapsed/60);
                    $("#wpm").html(WPM)
                    typist.highlight();
                    $("#inputter").val("");
                }
           
            
            });   
    });

    // request resolution from the game service for the iframe
    var message =  {
          messageType: "SETTING",
          options: {
            "width": 700, //Integer
            "height": 400 //Integer
            }
        };
    window.parent.postMessage(message, "*");
   
    
    setInterval(function() {
        
        typist.secondselapsed++;
        $("#seconds").html(typist.secondselapsed);
    }, 1000)
});