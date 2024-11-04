import time
import pytchat
import requests
import httpx
from datetime import datetime
from playwright.sync_api import sync_playwright
from multiprocessing import Process, Manager

# CONST
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@ai_spongebob/streams"
VK_PLAY_URL = "https://live.vkplay.ru/c1ymba"
TWITCH_URL = "https://www.twitch.tv/kussia88"
POST_URL = "https://YOUR-DOMAIN.COM/get.php"

def launch_browser_with_proxy(p):
    return p.chromium.launch(
        headless=False,
    )

def create_pytchat_client():
    client = httpx.Client(timeout=None)
    return client

def send_comment(source, username, message):
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "source": source,
            "username": username,
            "message": message
        }
        response = requests.post(POST_URL, json=data, headers=headers)  # Без прокси
        if response.status_code != 200:
            console_msg(f"Ошибка при отправке комментария ({source}): {username}. Статус: {response.status_code}", 'red')
            print(response.text)
    except Exception as e:
        console_msg(f"Ошибка при отправке комментария ({source}):", 'red')
        print(e)

def console_msg(source_tag, username, message, source_color='white'):
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    colors = {
        'white': '\x1b[37m',
        'yellow': '\x1b[33m',
        'red': '\x1b[31m',
        'green': '\x1b[32m',
        'pink': '\x1b[35m',
        'cyan': '\x1b[36m',
        'purple': '\x1b[35m'
    }
    source_text_color = colors.get(source_color, colors['white'])
    reset_color = colors['white']

    print(f'\x1b[36m{formatted_date}\x1b[0m {source_text_color}{source_tag}\x1b[0m {reset_color}{username}: {message}\x1b[0m')

def check_youtube_stream_id(youtube_stream_data):
    console_msg("[System]", "Info", "Запуск процесса проверки трансляции на YouTube", 'green')
    with sync_playwright() as p:
        browser = launch_browser_with_proxy(p)
        page = browser.new_page()

        while True:
            page.goto(YOUTUBE_CHANNEL_URL)
            page.wait_for_timeout(5000)

            live_element = page.query_selector('a[href*="/watch?v="]')
            if live_element:
                video_url = live_element.get_attribute('href')
                if video_url:
                    video_id = video_url.split('=')[-1]
                    youtube_stream_data['stream_id'] = video_id
                    console_msg("[YouTube]", "System", f"Текущая трансляция найдена: {video_id}", 'red')
                    break
            else:
                console_msg("[YouTube]", "System", "Текущая трансляция не найдена", 'yellow')
                time.sleep(30)

        browser.close()

def get_youtube_comments(youtube_stream_data):
    console_msg("[System]", "Info", "Запуск процесса получения сообщений из YouTube", 'green')
    while True:
        current_stream_id = youtube_stream_data.get('stream_id', None)
        if current_stream_id:
            try:
                client = create_pytchat_client()
                chat = pytchat.create(video_id=current_stream_id, client=client)
                while chat.is_alive():
                    for c in chat.get().sync_items():
                        username = c.author.name
                        message = c.message
                        console_msg("[YouTube]", username, message, 'red')
                        send_comment("youtube", username, message)
            except Exception as e:
                console_msg("[Error]", "YouTube", f"Ошибка при получении сообщений чата: {e}", 'red')
                time.sleep(5)
        else:
            console_msg("[System]", "Info", "Ожидание активной трансляции на YouTube...", 'yellow')
            time.sleep(10)

def get_vk_play_comments():
    console_msg("[System]", "Info", "Запуск процесса получения сообщений из VK Play", 'green')
    processed_messages = set()

    with sync_playwright() as p:
        browser = launch_browser_with_proxy(p)
        page = browser.new_page()
        page.goto(VK_PLAY_URL)

        while True:
            try:
                #console_msg("[System]", "Info", "Парсинг сообщений чата VK...", 'yellow')
                chat_elements = page.query_selector_all('div[data-role="messageContainer"]')

                if not chat_elements:
                    console_msg("[Debug]", "System", "Элементы чата не найдены. Возможно, структура страницы изменилась.", 'red')
                    time.sleep(5)
                    continue

                for element in chat_elements:
                    author_elem = element.query_selector('.ChatMessageAuthorPanel_name_w3ZOm')
                    main_message_elem = element.query_selector('span[data-role="messageMainContent"]')

                    if not author_elem or not main_message_elem:
                        console_msg("[Debug]", "System", "Элемент автора или сообщения отсутствует.", 'red')
                        continue

                    author = author_elem.inner_text().rstrip(':')
                    message_parts = main_message_elem.query_selector_all('span[data-role="markup"], img')

                    formatted_message = ""
                    for part in message_parts:
                        tag_name = part.evaluate('(node) => node.tagName')
                        if tag_name == 'IMG':
                            emoji_url = part.get_attribute('src')
                            emoji_alt = part.get_attribute('alt') or 'Emoji'
                            formatted_message += f'<img src="{emoji_url}" alt="{emoji_alt}" /> '
                        elif tag_name == 'SPAN':
                            text_content = part.inner_text().strip()
                            if text_content:
                                formatted_message += text_content + " "

                    formatted_message = formatted_message.strip()

                    if formatted_message:
                        #console_msg("[Debug]", "System", f"Обнаружено сообщение: {formatted_message}", 'green')

                        message_id = f"{author}:{formatted_message}"
                        if message_id not in processed_messages:
                            processed_messages.add(message_id)
                            console_msg("[VK Play]", author, formatted_message, 'cyan')
                            send_comment("vk", author, formatted_message)

                if len(processed_messages) > 1000:
                    processed_messages = set(list(processed_messages)[-500:])

                time.sleep(2)
            except Exception as e:
                console_msg("[Error]", "VK Play", f"Ошибка при получении сообщений чата: {e}", 'red')
                time.sleep(5)


def get_twitch_comments():
    console_msg("[System]", "Info", "Запуск процесса получения сообщений из Twitch", 'green')
    with sync_playwright() as p:
        browser = launch_browser_with_proxy(p)
        page = browser.new_page()
        page.goto(TWITCH_URL)

        page.wait_for_timeout(10000)

        processed_messages = set()

        while True:
            try:
                #console_msg("[System]", "Info", "Парсинг сообщений чата Twitch...", 'yellow')
                chat_elements = page.query_selector_all('div[data-a-target="chat-line-message"]')

                if not chat_elements:
                    console_msg("[Error]", "Twitch", "Элементы чата не найдены, возможно, структура страницы изменилась", 'red')

                for element in chat_elements:
                    author_elem = element.query_selector('span[data-a-target="chat-message-username"]')
                    message_parts = element.query_selector_all('span[data-a-target="chat-message-text"], div.chat-line__message--emote-button')

                    if author_elem and message_parts:
                        author = author_elem.inner_text().strip()
                        message = ""

                        for part in message_parts:
                            tag_name = part.evaluate('(node) => node.tagName')

                            if tag_name == 'SPAN':
                                message += part.inner_text().strip() + " "
                            elif tag_name == 'DIV':
                                img_elem = part.query_selector('img')
                                if img_elem:
                                    emote_alt = img_elem.get_attribute('alt')
                                    emote_src = img_elem.get_attribute('src')
                                    message += f'<img src="{emote_src}" alt="{emote_alt}" /> '

                        message = message.strip()
                        message_id = f"{author}:{message}"

                        if message_id not in processed_messages:
                            console_msg("[Twitch]", author, message, 'purple')
                            send_comment("twitch", author, message)
                            processed_messages.add(message_id)

                    if len(processed_messages) > 1000:
                        processed_messages = set(list(processed_messages)[-500:])

                time.sleep(2)
            except Exception as e:
                console_msg("[Error]", "Twitch", f"Ошибка при получении сообщений чата: {e}", 'red')
                time.sleep(5)

if __name__ == "__main__":
    with Manager() as manager:
        youtube_stream_data = manager.dict()
        youtube_stream_data['stream_id'] = None

        youtube_check_process = Process(target=check_youtube_stream_id, args=(youtube_stream_data,))
        youtube_comments_process = Process(target=get_youtube_comments, args=(youtube_stream_data,))
        vk_process = Process(target=get_vk_play_comments)
        twitch_process = Process(target=get_twitch_comments)

        youtube_check_process.start()
        youtube_comments_process.start()
        vk_process.start()
        twitch_process.start()

        youtube_check_process.join()

        youtube_comments_process.join()
        vk_process.join()
        twitch_process.join()