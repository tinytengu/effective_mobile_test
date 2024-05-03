# Личный финансовый кошелек

Приложение для управления доходами и расходами на Python 3.12.3

* GUI: Терминал (интерактивный)
* Форматтер, линтер: `Ruff` + `pycodestyle`
* Усложнение жизни: `mypy`
* Тестирование: `pytest`

# Использование приложения
```
usage: main.py [-h] -f FILENAME [--create]

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
  --create
```

## 0. Подготовка
### 1. Виртуальное окружение
Первоначально необходимо создать изолированное виртуальное окружение Python 3. Возможно использовать pyenv, poetry, что угодно, что решает данную задачу, я приведу самый базовый пример.
```bash
python3.12 -m venv venv
```

### 2. Активация виртуального окружения
```bash
source venv/bin/activate
```

### 3. Установка зависимостей приложения
```bash
pip install -r requirements.txt
```


## 1. Запуск
```bash
python3 main.py --file db.json --create
```
* `db.json` - имя/путь к файлу с импровизированной базой данных
* `--create` - создаёт файл, если он ещё не существует

## 2. Тестирование
### 1. Обычное тестирование
```bash
pytest
```

### 2. С отчётом о покрытии
```bash
pytest --cov=. && coverage html
```

Сразу с открытием в браузере (Windows)
```bash
pytest --cov=. && coverage html && start htmlcov/index.html
```