# README #

Для запуска необходимо указать один или оба параметра --save_to_file и/или --send_to_url.
Весь список параметров:

  -h, --help            Справка
  --web_driver {phantom,firefox}
                        Вы можете выбрать какой веб-драйвер использовать. По
                        умолчанию используется firefox
  --save_to_file        При указании скрипт будет сохранять json в файл
  --use_virtual_display
                        Указывая данный параметр вы сообщите скрипту что НЕ
                        нужно использовать виртуальный дисплей
  --send_to_url         При указании скрипт будет отправлять json на сервер