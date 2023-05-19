cd app && python manage.py flask --app intime.py db upgrade && cd ../
echo "$ITP_INIT_DB_DEMO"
if [["$ITP_INIT_DB_DEMO" == "1"]]; \
    then python fill_database.py;  \
fi
