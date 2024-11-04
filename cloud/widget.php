<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Chat Widget</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">

    <style>
        body {
            font-family: "Roboto", sans-serif;
            color: white;
        }
        #chat {
            overflow: hidden;
            padding: 10px;
            border-radius: 10px;
        }
        .message {
            padding: 5px;
            margin-bottom: 5px;
            opacity: 1;
            transition: opacity 1s;
        }
        .new-message {
            border-left: 4px solid #4caf50; /* Зеленая полоса для новых сообщений */
        }
        .youtube {
            color: #d20a0a;
            font-weight: 600;
        }
        .vk {
            color: #9090ff;
            font-weight: 600;
        }
        .twitch {
            color: #974697;
            font-weight: 600;
        }
    </style>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <div id="chat"></div>

    <script>
        let lastMessageId = 0;

        function loadMessages() {
            $.ajax({
                url: 'api.php',
                type: 'GET',
                dataType: 'json',
                success: function(data) {
                    if (data.length === 0) {
                        $('#chat').empty();
                        lastMessageId = 0;
                    } else if (data[data.length - 1].id !== lastMessageId) {
                        $('#chat').empty();
                        const currentTime = new Date();

                        data.forEach(function(message) {
                            let sourceClass = '';
                            let img_icon = '';
                            let messageTime = new Date(message.date);
                            let isNewMessage = (currentTime - messageTime) / 1000 <= 60;

                            switch (message.source.toLowerCase()) {
                                case 'youtube':
                                    sourceClass = 'youtube';
                                    img_icon = '<img src="img/icon-youtube.png">';
                                    break;
                                case 'vk':
                                    sourceClass = 'vk';
                                    img_icon = '<img src="img/icon-vk.png">';
                                    break;
                                case 'twitch':
                                    sourceClass = 'twitch';
                                    img_icon = '<img src="img/icon-twitch.png?1">';
                                    break;
                                default:
                                    sourceClass = '';
                            }

                            $('#chat').append(
                                `<div class="message ${isNewMessage ? 'new-message' : ''}" id="message-${message.id}">
                                    ${img_icon} <strong class="${sourceClass}">${message.user_name}</strong>: ${message.message}
                                </div>`
                            );
                        });

                        lastMessageId = data[data.length - 1].id;
                    }
                }
            });
        }

        setInterval(loadMessages, 2000);
        loadMessages();
    </script>
</body>
</html>