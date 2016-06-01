# -*- coding: utf-8 -*-

### Webdriver const ###
PhantomJS = 'phantom'
Firefox = 'firefox'

### Webdriver settings ###
web_driver = Firefox
service_args = None
load_timeout = 60
explicit_waits = 10
implicitly_wait = 5

### Direct parameters ###
debug = True
use_virtual_display = True
log_dir = 'logs/'
screen_dir = 'screen/'

### Send json settings ###
save_to_file = False
send_to_url = False

### Script settings ###
argv_var = dict(
    save_to_file=dict(
        default=save_to_file,
        action='store_true',
        help='При указании скрипт будет сохранять json в файл',
    ),
    send_to_url=dict(
        default=send_to_url,
        action='store_true',
        help='При указании скрипт будет отправлять json на сервер',
    ),
    use_virtual_display=dict(
        default=use_virtual_display,
        action='store_false',
        help='Указывая данный параметр вы сообщите скрипту что НЕ нужно использовать виртуальный дисплей',
    ),
    web_driver=dict(
        choices=[PhantomJS, Firefox],
        default=web_driver,
        help='Вы можете выбрать какой веб-драйвер использовать. По умолчанию используется firefox',
    )
)
