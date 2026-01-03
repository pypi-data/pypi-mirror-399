# SSH MCP Server

MCP-сервер для управления VPS через SSH. Предоставляет AI-агентам безопасный и контролируемый доступ к удалённым серверам через Model Context Protocol.

## Установка

```bash
# Через pip
pip install mcp-ssh-vps

# Через uvx (рекомендуется)
uvx mcp-ssh-vps
```

## Подключение к Claude Code

Добавьте в `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "ssh-vps": {
      "command": "uvx",
      "args": ["mcp-ssh-vps"],
      "env": {
        "SSHMCP_CONFIG_PATH": "~/.sshmcp/machines.json"
      }
    }
  }
}
```

Или через CLI:
```bash
claude mcp add ssh-vps -s user -- uvx mcp-ssh-vps
```

## Возможности

- **Tools:** Выполнение команд, чтение/загрузка файлов, управление процессами
- **Resources:** Логи, метрики, статус серверов
- **Prompts:** Шаблоны для развёртывания, бэкапов, мониторинга
- **Безопасность:** Whitelist команд, валидация путей, аудит
- **CLI интерфейс:** Удобное управление серверами из командной строки
- **Динамическое управление:** AI агент может добавлять/удалять сервера

## Быстрый старт

```bash
# Инициализация (интерактивный wizard)
sshmcp-cli init

# Или добавить сервер вручную
sshmcp-cli server add --name prod --host 192.168.1.100 --user deploy

# Проверить подключение
sshmcp-cli server test prod

# Запустить MCP сервер (для отладки)
sshmcp
```

## CLI команды

```bash
# Управление серверами
sshmcp-cli server list              # Список всех серверов
sshmcp-cli server add               # Добавить сервер (интерактивно)
sshmcp-cli server add --name dev --host 10.0.0.1 --user root
sshmcp-cli server remove prod       # Удалить сервер
sshmcp-cli server test prod         # Проверить подключение
sshmcp-cli server edit              # Редактировать конфиг в редакторе

# Импорт из SSH config
sshmcp-cli server import-ssh        # Импортировать из ~/.ssh/config

# Запуск сервера
sshmcp                              # Запустить MCP (stdio)
sshmcp --transport streamable-http  # Запустить HTTP сервер
```

## Профили безопасности

При добавлении сервера можно выбрать уровень безопасности:

- **strict** - только безопасные команды (git, ls, cat, tail)
- **moderate** - стандартные DevOps команды (npm, pm2, docker, systemctl)
- **full** - все команды (кроме rm -rf /)

```bash
sshmcp-cli server add --name prod --security-profile strict
```

## Конфигурация

Конфиг хранится в `~/.sshmcp/machines.json` (создаётся автоматически).

Можно указать другой путь:
```bash
export SSHMCP_CONFIG_PATH=/path/to/config.json
```

## Запуск MCP сервера

```bash
# stdio транспорт (для Claude Desktop, Cursor и т.д.)
sshmcp

# HTTP транспорт
sshmcp --transport streamable-http --port 8000
```

## Интеграция с AI-агентами

См. [docs/integration.md](docs/integration.md) для интеграции с:
- Claude Code
- Factory
- Qwen Code
- Claude Desktop
- Cursor

## Документация

- [Архитектура](docs/architecture.md)
- [MCP Python SDK](docs/mcp-python-sdk.md)
- [Интеграция](docs/integration.md)
- [Roadmap](docs/roadmap.md)

## Лицензия

MIT License - см. [LICENSE](LICENSE)
