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
use_virtual_display = False
log_dir = 'logs/'
screen_dir = 'screen/'

### Script settings ###
argv_var = dict(
    use_virtual_display=dict(
        default=use_virtual_display,
        action='store_true',
    ),

    web_driver=dict(
        choices=[PhantomJS, Firefox],
        default=web_driver,
    )
)
