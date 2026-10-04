# Стартовый скрипт этапа 5: chown (изменения только в памяти).
# Запуск: ./run.sh -v fixtures/out/deep.zip -s examples/stage5.vsh

cd /home/lena
ls -l
# владелец, владелец и группа, только группа, числовой id
chown lena diary.txt
chown lena:staff diary.txt
ls -l diary.txt
chown -v :lena diary.txt
chown -v 1001 diary.txt
chown -v guest:guest diary.txt
chown -v guest:guest diary.txt
# рекурсивно (-R) с подробным выводом (-v)
chown -R -v lena:lena study
ls -l study/config/practice1
# несколько файлов за раз
chown www:www /var/www /var/www/index.html
ls -l /var/www
# ошибки (строки пропускаются)
chown
chown lena
chown bob diary.txt
chown lena:nogroup diary.txt
chown a:b:c diary.txt
chown -x lena diary.txt
chown lena /no/such/file
ls -l
