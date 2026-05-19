ALLOWED_KEYWORDS = [
    "c#", "csharp", ".net", "dotnet", "asp.net", "asp net",
    "backend", "api", "rest", "controller", "service",
    "clean architecture", "architecture", "solid",
    "entity framework", "ef core", "postgresql", "sql",
    "jwt", "token", "authentication", "authorization",
    "dependency injection", "di", "middleware",
    "repository", "unit of work", "migration",
    "blazor", "web api", "microservice", "microservices",
    "database", "dto", "swagger", "serilog",
    "async", "await", "linq","python",
"java",
"javascript",
"typescript",
"react",
"angular",
"vue",
"docker",
"kubernetes",
"oop",
"solid",
"algorithm",
"data structure",
"frontend",
"backend",
"fullstack",
"html",
"css",
"programming",
"coding",
"git",
"github",
"linux",
]


ALLOWED_RUSSIAN_KEYWORDS = [
    "си шарп", "си шарп", "бекенд", "бэкенд", "архитектура",
    "чистая архитектура", "контроллер", "сервис",
    "база данных", "миграция", "токен", "авторизация",
    "аутентификация", "репозиторий", "микросервис",
    "микросервисы", "сваггер", "постгрес", "постгрескл",
    "зависимости", "инъекция", "мидлвар", "апи","программирование",
"код",
"алгоритм",
"структуры данных",
"фронтенд",
"фуллстек",
"джава",
"питон",
"докер",
"гит",
"ооп",
]


ALLOWED_TAJIK_KEYWORDS = [
    "бекенд", "си шарп", "архитектура", "тоза архитектура",
    "маълумот", "база", "токен", "авторизатсия",
    "контроллер", "сервис", "репозиторий"
]


def is_backend_related(text: str) -> bool:
    text = text.lower()

    all_keywords = (
        ALLOWED_KEYWORDS
        + ALLOWED_RUSSIAN_KEYWORDS
        + ALLOWED_TAJIK_KEYWORDS
    )

    return any(keyword in text for keyword in all_keywords)


def domain_refusal_message() -> str:
    return (
        "⚠️ <b>Domain Restriction Activated</b>\n\n"
        "Ман танҳо дар мавзӯи <b>backend development</b> ва "
        "<b>software architecture</b> ҷавоб медиҳам.\n\n"
        "Мавзӯъҳои иҷозатшуда:\n"
        "• C# / ASP.NET Core\n"
        "• Clean Architecture\n"
        "• EF Core / PostgreSQL\n"
        "• JWT Authentication\n"
        "• REST API\n"
        "• Blazor\n"
        "• Microservices\n\n"
        "Лутфан саволи техникӣ диҳед."
    )