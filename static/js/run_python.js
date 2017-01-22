function finish(){
    console.log("Finished")
    var f = document.getElementById('form').innerHTML;
    Mixmax.done(f);
  }

  showdown.setFlavor('github');
  var converter = new showdown.Converter()

  var bee = 0;

  var docCount = 0;
  var codeSwitch;
  var pending = false;
  var url = document.URL;
  var form = document.getElementById('form');

  var settings = 'autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" rows=1 cols=80';

  //holds code
  var codeList = [];


  url = url.replace("http", "ws").replace("editor", "ws");
  console.log(url);
  var conn = new WebSocket(url);
  $(window).on('beforeunload', function(){
      conn.close();
  });


  $('#i'+docCount).keypress(handler);
  $('#i'+docCount).keyup(exiter);

  function rerun(k){

    var count = 0;
    function runAllUpto(c, n) {
      document.getElementById("c"+c).innerHTML = "";
      conn.onmessage = function(e) {
        console.log("asdf"+c+","+count+": '"+e.data+"'");
        document.getElementById("c"+c).innerHTML += e.data;
        if(e.data=="\\" && count<3){
          count++;
          document.getElementById("c"+c).innerHTML = document.getElementById("c"+c).innerHTML.replace("\\\\\\", "").replace("\n", "<br>");
          console.log("countup");
        }
        else if(e.data=="\n" && count==3){
          count++;
        }
        else{
          count = 0;
        }
        if(count == 4 && c!=n){
          count = 0;
          console.log(c+","+n)
          runAllUpto(c+1, n);
        }
      }
      console.log("sent: "+codeList[c])
      conn.send(codeList[c].replace('\n', '{*n*}'));
    }
    conn.onmessage = function(e) {
      console.log(e.data);
      if(e.data=="done"){
        console.log("done");
        conn.onmessage = function(e) {console.log(e);};
        runAllUpto(0, k);
      }

    }
    conn.send("{*reset*}")
  }

  function exiter(e){
    this.style.cssText = 'height:auto; padding:0';
    this.style.cssText = 'height:' + this.scrollHeight + 'px';
    var io = this;
    // change code block to normal block
    //  make sure to delete from code list
    if(e.originalEvent.code == "Backspace"){
      if($(io).hasClass("code") && io.value==""){
        console.log("exit");
        $(io).removeClass("code");
      }
    }
  }
  
  function handler(e){
    this.style.cssText = 'height:auto; padding:0';
    this.style.cssText = 'height:' + this.scrollHeight + 'px';


    var io = this;
    var currId = io.id;
    var currNum = Number(currId.substring(1));
    console.log(e);

    if($(io).hasClass("code") && bee==0 && e.originalEvent.key=='b'){
      bee++;
    }
    else if($(io).hasClass("code") && bee<3 && e.originalEvent.key=='e'){
      bee++;
      if(bee==3){
        window.open('https://www.youtube.com/watch?v=E6iN6VTL7v8', '');
      }
    }
    else{
      bee = 0;
    }
    //cancel code waiting
    clearTimeout(codeSwitch);
    if(pending){

      //set to code if "\ "
      if(e.originalEvent.charCode==32){
        e.preventDefault();
        $(io).addClass("code");
        pending = false;
      }

      //input the \
      else{
        io.value = '\\';
        pending = false;
      }
    }

    

    //shift enter to submit
    if(e.keyCode == 13 && e.shiftKey) {
      e.preventDefault();
      if(io.value==''){
        io.value = "\n";
      }

      //input is code, and should be sent to socket
      // also add code to list
      // then on resubmits, just go through all consoles and append new output
      var isCode = $(io).hasClass("code");
      if(isCode){
        if(currNum==docCount){
          console.log("running most recent again");
          codeList.push(io.value);
          conn.onmessage = function(e) {
            $('#c'+currNum).append(e.data.replace("\n", "<br>"));
            document.getElementById("c"+currNum).innerHTML = document.getElementById("c"+currNum).innerHTML.replace("\\\\\\", "");
          };
          conn.send(io.value.replace('\n', '{*n*}'));
        }
        else{
          console.log(currNum+" "+docCount);
          console.log("changed something "+codeList);
          codeList[currNum] = io.value;
          console.log(docCount+","+currNum+":"+codeList);
          rerun(currNum);
        }
        $(io).replaceWith('<div class="out" id="'+currId+'">'+io.value.replace("\n", "<br>")+'</div>');
      }
      else{
        var content = io.value;
        //console.log(converter.makeHtml(content));
        var fluff = "";
        var madeHtml = converter.makeHtml(content);
        if( (madeHtml.split(">").length - 1) <= 2){
          if(madeHtml.indexOf("<br>")==-1 && madeHtml.indexOf("<p>&nbsp;</p>"))
            fluff = "<p>&nbsp;</p>";
        }
        var d = $(io).replaceWith("<div id='"+currId+"' class='out'><p id='temp'></p><p id='temp1'></p></div>");
        $('#temp').replaceWith(madeHtml);
        $('#temp1').replaceWith('<textarea id="'+currId+'md" style="display:none;">'+content+'</textarea>');
        codeList.push("");
        //d.append(h);

      };
      //create <p> with content of input (history)
      $('#s'+currNum).remove();
      io = document.getElementById(currId);
      if(isCode){
        $(io).addClass("code");
      }

      //editable history
      io.onclick = function(){
        var isCode = $(io).hasClass("code");
        if(isCode){
          var content = io.innerHTML;
          console.log("EDITED: "+content);
          $(io).replaceWith('<textarea id="'+currId+'">'+content.replace("<br>", "\n")+'</textarea><br id="s'+currNum+'">');
          io = document.getElementById(currId);
          $(io).addClass("code");
        }
        else{
          var content = document.getElementById(currId+'md').value;
          $(currId+'md').remove();
          $(io).replaceWith('<textarea id="'+currId+'">'+content+'</textarea><br id="s'+currNum+'">');

        }
        io = document.getElementById(currId);
        $(io).keypress(handler);
        $(io).keyup(exiter);
      }

      if(currNum==docCount){
        docCount++;
        $('#form').append("<textarea id='i"+docCount+"' "+settings+"></textarea>").focus();
        $('#form').append("<div class='stdout' id='c"+docCount+"'class='output'></div>");
        $('#i'+docCount).keypress(handler);
        $('#i'+docCount).keyup(exiter);
      }
    }

    //press backslash to get code input
    if(e.originalEvent.charCode == 92){
      if(io.value==''){
        e.preventDefault();
        pending = true;
        codeSwitch = setTimeout(function(){
          $(io).addClass("code");
          pending = false;
        }, 1000);
      }
    }

  }

  //function sendEof(){
  //  console.log('closing stdin');
  //  conn.send("{*--EOF--*}");
  //}
