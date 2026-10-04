# Стартовый скрипт этапа 4: ls, cd, history, tac, clear.
# Запуск: ./run.sh -v fixtures/out/deep.zip -s examples/stage4.vsh

# ls: текущий каталог, ключи -l и -a, несколько путей, файл
ls
ls -l /etc
ls -la /home/lena
ls /etc/hostname /var
# cd: абсолютный и относительный путь, .., ~, -
cd /home/lena/study
cd config/practice1
ls -l
cd ../..
cd -
cd ~
cd
# tac: один файл, несколько файлов, двоичный файл
tac /home/lena/diary.txt
tac /etc/hostname /var/log/system.log
tac /home/lena/study/config/practice1/icon.bin
# history: вся история, последние N
history
history 3
# clear: очистка экрана, затем продолжение работы
clear
ls /home
# ошибки (строки пропускаются)
ls /nope
ls -x
cd /etc/passwd
cd /missing
cd / /tmp
tac
tac /nope
tac /etc
tac -s x /etc/hostname
history abc
history -z
history 1 2
clear screen
history -c
history
