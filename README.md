# Respondent Testing E2E

Репозиторий автотестов для фронтовой части веб‑приложения
Тесты написаны на **Python + Playwright + pytest** и ориентированы на пользовательские сценарии (логин, прохождение теста, просмотр результата и т.п.).

---

## 1. Быстрый старт

### 1.1. Требования

- Python 3.11+
- Git
- Браузер(ы), поддерживаемые Playwright (Chromium, Firefox, WebKit)

### 1.2. Клонирование репозитория

```bash
git clone https://github.com/<OWNER>/respondent-testing-e2e.git
cd respondent-testing-e2e
```

### 1.3. Создание виртуального окружения и установка зависимостей

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
playwright install
```

### 1.4. Настройка окружения (.env)

В корне репозитория создайте файл `.env` (не коммитится, должен быть в `.gitignore`):

```env
ENV=dev
BASE_URL=https://dev

BROWSERS=chromium
HEADLESS=True

BROWSER_STATE_FILE=browser-state.json

TEST_USER.EMAIL="user.name@gmail.com"
TEST_USER.USERNAME="username"
TEST_USER.PASSWORD="password"
```

Основная конфигурация читается через `config.py` и доступна как объект `settings`.

---

## 2. Архитектура проекта

Проект организован по принципам Page Object Model и разделения ответственности.

```text
respondent-testing-e2e/
├── components/          # Составные части страниц (navbar, sidebar, виджеты)
├── data/                # Тестовые данные (json, csv и т.п.)
├── elements/            # Базовые UI-элементы (кнопка, инпут, селект и т.п.)
├── fixtures/            # Pytest-фикстуры (браузеры, страницы, авторизация)
├── pages/               # Page Object'ы (страницы/экраны приложения)
├── tests/               # Автотесты (сценарии, сгруппированные по фичам)
├── utils/               # Утилиты (хелперы, генераторы данных, ожидания)
├── .env                 # Переменные окружения (локально, не в git)
├── config.py            # Pydantic Settings: settings.*
├── conftest.py          # Глобальные фикстуры pytest
├── pytest.ini           # Конфигурация pytest и общие опции запуска
├── requirements.txt     # Python-зависимости проекта
└── README.md
```

### 2.1. Логическая схема

- **Tests** используют фикстуры и PageObject'ы и описывают только бизнес‑логику сценариев.
- **Fixtures** создают браузер/страницы, выполняют авторизацию, подготавливают данные.
- **Pages / Components / Elements** инкапсулируют работу с UI и локаторами.
- **config.py / .env** описывает окружение, базовый URL и тестовых пользователей.

---

## 3. Назначение ключевых разделов

### 3.1. `elements/`

- Базовые обёртки над Playwright‑локаторами: кнопка, поле ввода, селект, чекбокс и т.п.
- Пример: `BaseElement` реализует методы `get_locator`, `click`, `check_visible`, `check_have_text` и единожды описывает логику работы с `data-testid`, ожиданиями и логированием.
- Все другие элементы наследуются от `BaseElement` и добавляют специфические действия (например, `fill`, `select_option`).

### 3.2. `components/`

- Составные компоненты страницы: navbar, sidebar, формы, таблицы, карточки.
- Каждый компонент использует элементы из `elements/` и отвечает за проверки/действия на своём участке страницы (например, `NavbarComponent.check_user_name`, `SidebarComponent.click_logout`).
- Базовый `BaseComponent` содержит общие методы (например, `check_current_url`).

### 3.3. `pages/`

- Page Object'ы для страниц/экранов: Login, Registration, Dashboard, TestPassing и т.п.
- Базовый `BasePage` умеет:
  - `visit(url)` — открыть страницу,
  - `reload()` — перезагрузить,
  - `check_current_url(pattern)` — проверить URL.
- Конкретные страницы:
  - содержат локаторы и компоненты,
  - предоставляют бизнес‑методы: `login_page.login(email, password)`, `test_page.start_test()`, `result_page.check_score(...)`.

### 3.4. `fixtures/` и `conftest.py`

- Фикстуры для:
  - инициализации браузера и контекста (`chromium_page`, `chromium_page_with_state`),
  - создания `Page` с нужным `base_url` и `storage_state`,
  - предоставления PageObject'ов в тест (например, `login_page: LoginPage`).
- `conftest.py` подключает плагины и модули фикстур через `pytest_plugins`, чтобы они были доступны во всех тестах.

### 3.5. `tests/`

- Каталог с реальными автотестами.
- Рекомендуемая организация:
  - `tests/ui/auth/` — авторизация и регистрация,
  - `tests/ui/test_passing/` — прохождение теста,
  - `tests/ui/results/` — работа с результатами,
  - `tests/smoke/` — быстрые smoke‑сценарии для критических флоу.
- Каждый тест:
  - использует фикстуры страниц и данных,
  - не обращается к локаторам напрямую,
  - покрывается маркерами (`@pytest.mark.smoke`, `@pytest.mark.regression`).

### 3.6. `utils/`

- Вспомогательные функции и утилиты:
  - генераторы тестовых данных (email, username, пароль),
  - хелперы для ожиданий (wait_for, wait_until_visible),
  - маппинг маршрутов приложения,
  - логирование, обработка ошибок.

### 3.7. `config.py`

- Централизованная конфигурация приложения с использованием Pydantic Settings.
- Читает переменные из `.env`.
- Доступен через глобальный объект `settings` из `config import settings`.

---

## 4. Процесс разработки автотеста

### 4.1. Добавление нового сценария

1. **Определить бизнес‑флоу**  
   Описать словами: стартовая страница, действия пользователя, ожидаемый результат.

2. **Подготовить PageObject/компоненты (если нужно)**

   - Добавить/обновить нужные классы в `pages/`, `components/`, `elements/`.
   - Локаторы брать через Playwright Inspector или `page.get_by_test_id`.

3. **Добавить/обновить фикстуры**

   - В `fixtures/pages.py` добавить фикстуру, возвращающую новый PageObject.
   - При необходимости создать фикстуру с подготовленным состоянием (например, залогиненный пользователь).

4. **Написать тест**

   - Создать файл в `tests/...` (по фиче или типу тестов).
   - Использовать только PageObject'ы и фикстуры.
   - Отмечать тесты маркерами (`@pytest.mark.smoke`, `@pytest.mark.regression`).

5. **Запустить локально и убедиться в стабильности**
   - Запуск только новых тестов или файла.
   - При необходимости добавить ретраи/ожидания в PageObject'ы, а не в сам тест.

### 4.2. Пример типового сценария (уровень идеи)

```python
import pytest
from config import settings

def test_user_can_pass_test(login_page, test_page, result_page):
    """Пользователь может успешно пройти тест и увидеть результаты."""
    # Этап 1: вход в систему
    login_page.visit("/login")
    login_page.login(
        email=settings.test_user.email,
        password=settings.test_user.password
    )

    # Этап 2: прохождение теста
    test_page.start_test()
    test_page.answer_all_questions_correctly()
    test_page.submit()

    # Этап 3: проверка результатов
    result_page.check_score_is_displayed()
    result_page.check_score_greater_than(0)
```

---

## 5. Запуск тестов

### 5.1. Локальный запуск

**Все тесты:**

```bash
pytest
```

**Только smoke‑тесты:**

```bash
pytest -m smoke
```

**Тесты по директории/файлу:**

```bash
pytest tests/ui/auth/test_authorization.py
pytest tests/ui/test_passing/
```

**Запуск конкретного теста:**

```bash
pytest tests/ui/auth/test_authorization.py::TestAuthorization::test_successful_login
```

**Параллельный запуск (требует pytest-xdist):**

```bash
pytest -n auto
```

**Запуск с выводом логов в консоль:**

```bash
pytest -s
```

**Запуск с отключением headless-режима для дебага:**

```bash
pytest --headed
```

### 5.2. Отчёты

**HTML‑отчёт pytest-html**  
Генерируется опцией `--html=reports/report.html --self-contained-html` (настроено в `pytest.ini`).  
После запуска тестов открыть `reports/report.html` в браузере.

**Allure‑отчёт (если используется)**

- В `pytest.ini` настроен вывод `--alluredir=reports/allure-results`.
- Генерация и просмотр отчёта:
  ```bash
  allure serve reports/allure-results
  ```

---

## 6. Полезные ссылки и документация

- [Playwright Python официальная документация](https://playwright.dev/python/)
- [Pytest документация](https://docs.pytest.org/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Page Object Model паттерн](https://playwright.dev/python/docs/pom)

---

**Версия документации:** 1.0  
**Последнее обновление:** 2026-01-16
