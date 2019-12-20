python3 serv.py test.db --test &
py.test test_authors.tavern.yaml
py.test test_pagination.tavern.yaml
py.test test_books.tavern.yaml
#kill process python run before, $$ is pid of this script, pkill -P : kill all processes created by this script!
pkill -P $$
