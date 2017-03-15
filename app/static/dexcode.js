/**
 * Created by VogtFeehily on 2016/9/25.
 */
$(document).ready(function(){
    /*设置响应式图片，Bootstrap*/
    $("img").addClass("img-responsive");

    /*设置文章框的阴影效果*/
    $(".blog-box").mouseover(function () {
        $(this).css({ "box-shadow": '5px 5px 18px #969696' });
    });
    $(".blog-box").mouseout(function () {
        $(this).css({ "box-shadow": '3px 3px 10px #ababab' });
    });
});

$(function() {
    var like_post = function () {
        $.getJSON($SCRIPT_ROOT + '/like_post', {
            post_id: $("#post_id").text(),
        }, function (data) {
            $("#likes_num").text(data.likes);
            $("#like").css({ "color": '#28a0f6' });
        });
        return false;
    };
    $('a#like').bind("click", like_post);
});





    /* var submit_form = function(e) {
      $.getJSON($SCRIPT_ROOT + '/_add_numbers', {
        a: $('input[name="a"]').val(),
        b: $('input[name="b"]').val()
      }, function(data) {
        $('#result').text(data.result);
        $('input[name=a]').focus().select();
      });
      return false;
    };
    $('a#calculate').bind('click', submit_form);
    $('input[type=text]').bind('keydown', function(e) {
      if (e.keyCode == 13) {
        submit_form(e);
      }
    });
    $('input[name=a]').focus();
  });
})*/