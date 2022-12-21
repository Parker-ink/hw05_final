# Yatube
Yatube is a social network for making posts about all what you want.

## Installation
1. Create a project folder. Go to this folder.
2. Clone the project to this folder:
```bash
git clone git@github.com:Parker-ink/hw05_final.git
```
3. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```
4. Install required packages from requirements.txt file:
```bash
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```
5. Make migrations:
```bash
python3 manage.py migrate
```
6. Create Super User
```bash
python3 manage.py createsuperuser
```
7. Start the project
```bash
python3 manage.py runserver
```
