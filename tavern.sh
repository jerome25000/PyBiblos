#python3 serv.py conf_test.yaml &
python3 -m pytest test_authors.tavern.yaml
python3 -m pytest test_pagination.tavern.yaml
python3 -m pytest test_books.tavern.yaml
python3 -m pytest test_users.tavern.yaml
python3 -m pytest test_login.tavern.yaml
#kill process python run before, $$ is pid of this script, pkill -P : kill all processes created by this script!
pkill -P $$
