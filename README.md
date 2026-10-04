# vshell — эмулятор командной оболочки UNIX

Дисциплина «Конфигурационное управление», практическая работа №1, вариант 6.

Выполнила: **Вихорь Елена Даниловна**, группа ИКБО-30-25.

---

## Общее описание

`vshell` — учебный эмулятор командной строки UNIX-подобной ОС. Программа
открывает окно, похожее на обычный терминал: приглашение
`пользователь@vshell:каталог$`, ввод команды прямо после него, вывод и
ошибки ниже. Команды работают с виртуальной файловой системой (VFS),
загруженной из ZIP-архива. Архив читается целиком в память и не
распаковывается, поэтому все изменения (например, `chown`) живут только
до закрытия эмулятора.

* Язык: Python 3.8+ (только стандартная библиотека).
* Интерфейс: tkinter.
* Тесты: unittest.

### Этапы и коммиты

| № | Этап | Что сделано |
|---|------|-------------|
| 1 | REPL | окно-терминал, разбор ввода по пробелам, заглушки `ls`/`cd`, `exit` |
| 2 | Конфигурация | параметры `-v`, `-s`, отладочный вывод, стартовый скрипт |
| 3 | VFS | ZIP → память, base64, ошибки загрузки, служебная команда `mount` |
| 4 | Основные команды | `ls`, `cd`, `history`, `tac`, `clear` |
| 5 | Дополнительные команды | `chown` |

### Устройство проекта

| Путь | Назначение |
|------|------------|
| `src/vshell/__main__.py` | запуск: параметры, загрузка VFS, окно или консоль |
| `src/vshell/settings.py` | параметры командной строки и отладочный вывод |
| `src/vshell/lexer.py` | разбор строки на команду и аргументы |
| `src/vshell/interpreter.py` | интерпретатор: приглашение, история, вызов команд |
| `src/vshell/navigation.py` | `ls`, `cd` |
| `src/vshell/textutils.py` | `tac` |
| `src/vshell/session.py` | `exit`, `history`, `clear`, `mount` |
| `src/vshell/ownership.py` | `chown` |
| `src/vshell/memfs.py` | VFS в памяти и загрузка из ZIP |
| `src/vshell/modes.py` | права доступа в виде `rwxr-xr-x` |
| `src/vshell/startup.py` | выполнение стартового скрипта |
| `src/vshell/window.py` | графическое окно-терминал |
| `src/vshell/console.py` | консольный режим |
| `src/vshell/io.py` | общий интерфейс вывода |
| `tests/` | модульные тесты по этапам |
| `examples/` | стартовые скрипты эмулятора (`*.vsh`) |
| `os_scripts/` | скрипты ОС для проверки параметров и VFS |
| `fixtures/build_fixtures.py` | сборка тестовых ZIP-архивов VFS |

---

## Функции и настройки

### Параметры запуска

```
./run.sh [-v ZIP] [-s FILE] [-c]
```

| Параметр | Значение |
|----------|----------|
| `-v ZIP`, `--vfs ZIP` | путь к ZIP-архиву с VFS. Без него — пустая VFS в памяти |
| `-s FILE`, `--script FILE` | стартовый скрипт, выполняется сразу после запуска |
| `-c`, `--console` | работать в консоли без окна |
| `-h`, `--help` | справка |

При старте выводятся все параметры:

```
debug: параметры запуска
debug:   vfs_path    = 'fixtures/out/deep.zip'
debug:   script_path = 'examples/stage4.vsh'
debug:   console     = False
```

### Окно

* Заголовок: `vshell — <имя VFS>`, например `vshell — deep.zip`.
* Ввод набирается прямо после приглашения, Enter выполняет команду.
* Стрелки ↑/↓ листают историю.
* Ошибки выделены красным, служебные сообщения — синим.

### Разбор ввода

Строка делится на слова по пробелам: первое слово — команда, остальные —
аргументы. Лишние пробелы игнорируются.

### Команды

| Команда | Описание |
|---------|----------|
| `ls [-l] [-a] [путь...]` | содержимое каталогов. `-l` — права, владелец, группа, размер; `-a` — также скрытые файлы, `.` и `..` |
| `cd [путь]` | сменить каталог. Без аргумента и `~` — домашний каталог (`/home/<пользователь>`, если он есть в VFS, иначе `/`); `-` — предыдущий каталог |
| `history [N]` | история команд с номерами; `N` — только последние N |
| `history -c` | очистить историю |
| `tac ФАЙЛ...` | вывести строки файлов в обратном порядке |
| `clear` | очистить экран |
| `chown [-R] [-v] ВЛАДЕЛЕЦ[:ГРУППА] ФАЙЛ...` | сменить владельца и/или группу. Формы: `lena`, `lena:staff`, `:staff`, числовой id `1000`. `-R` — рекурсивно, `-v` — подробно |
| `exit [код]` | завершить работу |
| `mount` | служебная: источник VFS, число каталогов и файлов |

`chown` проверяет имена по `/etc/passwd` и `/etc/group` внутри VFS.
Пользователь `root` и текущий пользователь допустимы всегда.

Сообщения об ошибках повторяют формат bash и GNU coreutils:

```
foo: command not found
ls: cannot access '/nope': No such file or directory
cd: /etc/passwd: Not a directory
tac: failed to open 'x' for reading: No such file or directory
history: abc: numeric argument required
chown: invalid user: 'bob'
```

### Стартовый скрипт

Текстовый файл, по одной команде в строке. Строки, начинающиеся с `#`, и
пустые строки не выполняются. Каждая команда показывается вместе с
приглашением, затем её вывод, как в диалоге с пользователем. Если команда
завершилась ошибкой, строка пропускается с пометкой
`(строка N скрипта пропущена)`, и выполнение продолжается.

### Формат VFS

* Обычный ZIP-архив. Каталоги задаются явно (`dir/`) или через пути файлов.
* Права берутся из UNIX-атрибутов архива (иначе 755 для каталогов, 644 для
  файлов). Владелец всех файлов при загрузке — текущий пользователь.
* Двоичный файл записывается в архив как текст `base64:<данные>`, при
  загрузке он декодируется.
* Ошибки загрузки (нет файла, не ZIP, повреждённый base64, путь с `..`)
  выводятся при старте, после чего эмулятор работает с пустой VFS.

---

## Сборка и тесты

Нужен Python 3.8+ с tkinter. Сборка не требуется.

```sh
make test          # модульные тесты
make fixtures      # собрать тестовые VFS в fixtures/out/
make run           # окно с пустой VFS
make demo          # окно с deep.zip и скриптом этапа 4
make check         # скрипты ОС этапов 2 и 3 в консольном режиме
```

> macOS + Homebrew: `brew install python-tk`; conda: `conda install tk`;
> Ubuntu: `sudo apt install python3-tk`.

Тестовые архивы (создаются `fixtures/build_fixtures.py`, в репозиторий не
входят):

| Архив | Содержимое |
|-------|------------|
| `minimal.zip` | один файл |
| `several.zip` | четыре файла, один двоичный |
| `deep.zip` | `/etc`, `/home/lena/study/config/practice1/...` (5 уровней), `/var`, `/tmp`, файлы `passwd` и `group` |
| `corrupt.zip` | не ZIP-файл, для проверки ошибки |

Скрипты ОС (bash) по умолчанию открывают окна по очереди, с `--console`
работают в терминале:

| Скрипт | Проверяет |
|--------|-----------|
| `os_scripts/check_args.sh` | все параметры командной строки |
| `os_scripts/check_vfs.sh` | пустую, минимальную, несколько файлов, глубокую VFS, отсутствующий и повреждённый архив |

Стартовые скрипты: `examples/stage2.vsh`, `examples/exit_code.vsh`,
`examples/stage3.vsh`, `examples/stage4.vsh`, `examples/stage5.vsh`.

---

## Примеры использования

```sh
make fixtures
./run.sh -v fixtures/out/deep.zip
```

Навигация и просмотр:

```
lena@vshell:/$ cd /home/lena
lena@vshell:~$ ls -la
drwxr-xr-x 1 lena lena     0 .
drwxr-xr-x 1 lena lena     0 ..
-rw-r--r-- 1 lena lena    34 diary.txt
drwxr-xr-x 1 lena lena     0 study
lena@vshell:~$ cd study/config/practice1
lena@vshell:~/study/config/practice1$ tac plan.txt
stage 5
stage 4
stage 3
stage 2
stage 1
lena@vshell:~/study/config/practice1$ cd -
/home/lena
lena@vshell:~$ history 2
    5  cd -
    6  history 2
```

Смена владельца:

```
lena@vshell:~$ chown -v lena:staff diary.txt
changed ownership of '/home/lena/diary.txt' from lena:lena to lena:staff
lena@vshell:~$ chown -R www:www /var/www
lena@vshell:~$ ls -l /var/www
-rw-r--r-- 1 www www    16 index.html
lena@vshell:~$ chown bob diary.txt
chown: invalid user: 'bob'
```

Стартовый скрипт с ошибкой:

```
lena@vshell:/$ cd /missing
cd: /missing: No such file or directory
(строка 31 скрипта пропущена)
```
