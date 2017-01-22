function finish(){
    console.log("Finished")
    var f = document.getElementById('form').innerHTML;
    Mixmax.done(f);
  }

  showdown.setFlavor('github');
  var converter = new showdown.Converter()

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

  function rerun(k){

    var count = 0;
    function runAllUpto(c, n) {
      document.getElementById("c"+c).innerHTML = "";
      conn.onmessage = function(e) {
        console.log("asdf"+c+","+count+": '"+e.data+"'");
        document.getElementById("c"+c).innerHTML += e.data;
        if(e.data=="\\" && count<3){
          count++;
          document.getElementById("c"+c).innerHTML = document.getElementById("c"+c).innerHTML.replace("\\\\\\", "");
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

  function handler(e){
    this.style.cssText = 'height:auto; padding:0';
    this.style.cssText = 'height:' + this.scrollHeight + 'px';

    var io = this;
    var currId = io.id;
    var currNum = Number(currId.substring(1));
    //console.log(e);

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

    // change code block to normal block
    //  make sure to delete from code list
    if(e.originalEvent.code == "Backspace"){
      if($(io).hasClass("code") && io.value==""){
        $(io).removeClass("code");
      }
    }

    //shift enter to submit
    if(e.keyCode == 13 && !e.shiftKey) {
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
          console.log("changed something");
          codeList[currNum] = io.value;
          console.log(docCount+","+currNum+":"+codeList);
          rerun(currNum);
        }
        $(io).replaceWith('<p class="wasCode" id="'+currId+'">'+io.value.replace("\n", "<br>")+'</p tag=done>');
      }
      else{
        var content = io.value;
        console.log(converter.makeHtml(content));
        var d = $(io).replaceWith("<div id='"+currId+"'><p id='temp'></p><p id='temp1'></p></div>");
        $('#temp').replaceWith(converter.makeHtml(content));
        $('#temp1').replaceWith('<textarea id="'+currId+'md" style="display:none;">'+content+'</textarea>');
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
          console.log("EDITED: "+io.innerHTML);
          $(io).replaceWith('<textarea id="'+currId+'">'+io.innerHTML.replace("<br>", "\n")+'</textarea><br id="s'+currNum+'">');
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
      }

      if(currNum==docCount){
        docCount++;
        $('#form').append("<textarea id='i"+docCount+"' "+settings+"></textarea>").focus();
        $('#form').append("<code id='c"+docCount+"'class='output'></code>");
        $('#i'+docCount).keypress(handler);
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
