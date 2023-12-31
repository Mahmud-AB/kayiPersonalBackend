$(document).ready(function () {
    chatboxReSize();
    viewRoom(currentSelectRoomId);
    window.addEventListener("resize", function () {
        chatboxReSize();
    });

    if (document.getElementById('send-message-input') != null) {
        document.getElementById('send-message-input').addEventListener('keyup', function () {
            this.style.overflow = 'hidden';
            this.style.height = 0;
            this.style.height = this.scrollHeight + 'px';
        }, false);
    }

    $('#send-message-send').click(function () {
        if (currentSelectRoomId > 0) {
            $.post('/api/user/support-message-any-user', {replay: currentSelectRoomId, message: $("#send-message-input").val()}, function (data, status) {
                if (status == 'success') {
                    if (data.status) {
                        $("#send-message-input").val("");
                        renderMessageToBox(data.data);
                        $("#show-caht-history").animate({
                            scrollTop: $('#show-caht-history')[0].scrollHeight - $('#show-caht-history')[0].clientHeight
                        }, 500);
                    } else {
                        showDangerToast(data.message)
                    }
                }
            });
        }
    })
});

function viewRoom(roomId) {
    currentSelectRoomId = roomId;
    $.get('/api/user/support-message-by-room/' + currentSelectRoomId, function (data, status) {
        if (status == 'success') {
            if (data.status) {
                $('#show-caht-history').html("");
                data.data.forEach(function (d) {
                    renderMessageToBox(d);
                })
                $('#show-caht-history').scrollTop($('#show-caht-history')[0].scrollHeight - $('#show-caht-history')[0].clientHeight);
            } else {
                showDangerToast(data.message)
            }
        }
    })
}

function renderMessageToBox(d) {
    const logoImg = (d.is_sender ? d.image : d.support_user.image) != null ? (d.is_sender ? d.image : d.support_user.image) : "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTmp7Zkhf_H_iJDUGaaRhchdSo0Qt6xUqQJ2HxC9kmAvpvmhxG6&usqp=CAU";
    const html = "" +
        "<div class=\"chat-bubble " + (d.is_sender ? 'incoming-chat' : 'outgoing-chat') + "\">\n" +
        "    <div class=\"chat-message\">\n" +
        "        <p>" + d.message + "</p>\n" +
        "    </div>\n" +
        "    <div class=\"sender-details\">\n" +
        "        <img class=\"sender-avatar img-xs rounded-circle\" src=\"" + logoImg + "\" alt=\"profile image\">\n" +
        "        <p class=\"seen-text\">" + d.username + " : " + timeAgo(d.created) + "</p>\n" +
        "    </div>\n" +
        "</div>"
    $('#show-caht-history').append(html);
}

function chatboxReSize() {
    $('#chatbox-left').height($(window).height() - $('#headerbox').height() - 100);
    $('#chatbox-left').css("overflow-x", 'hidden');
    $('#chatbox-left').css("overflow-y", 'auto');
    $('#chatbox-right').height($(window).height() - $('#headerbox').height() - 70);
    $('#chatbox-right').css("overflow-x", 'hidden');
    $('#chatbox-right').css("overflow-y", 'auto');
}