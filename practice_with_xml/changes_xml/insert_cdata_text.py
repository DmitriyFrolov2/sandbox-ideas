"""
Вставка SQL в конец последнего CDATA-блока в XML-файле.

Процесс:
1. Читаем исходный файл (SOURCE_FILE)
2. Вставляем SQL в конец последнего CDATA
3. Сохраняем результат в TARGET_FILE (папка создаётся автоматически)
"""

import re
import hashlib
from pathlib import Path


# ─── Настройки ────────────────────────────────────────────────────────────────

# Исходный файл — откуда читаем
SOURCE_FILE = Path(r"D:\test_migrations\migrations.xml")

# Целевой файл — куда сохраняем результат (папка создаётся автоматически)
TARGET_FILE = Path(r"E:\main_migrations\26.04.2026\migrations.xml")

# SQL который вставляем в конец последнего CDATA
NEW_SQL = """
ALTER TEST TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'pending';
UPDATE orders SET status = 'completed' WHERE amount > 0;"""

# Маркер для защиты от дублей — первая строка SQL
# Если эта строка уже есть в последнем CDATA — вставка пропускается
MARKER = NEW_SQL.strip().splitlines()[0]


# ─── Ядро ─────────────────────────────────────────────────────────────────────

CDATA_RE = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)


def get_last_cdata_match(content: str):
    """Возвращает match последнего CDATA-блока в файле."""
    matches = list(CDATA_RE.finditer(content))
    if not matches:
        raise ValueError("❌ CDATA-блоки не найдены в файле")
    return matches[-1]


def append_sql_to_last_cdata(content: str, new_sql: str):
    """Дописывает SQL в конец последнего CDATA. Возвращает (new_content, old_body, new_body)."""
    match = get_last_cdata_match(content)

    old_body = match.group(1)
    new_body = old_body.rstrip() + "\n" + new_sql.strip() + "\n        "

    new_content = content[:match.start()] + f"<![CDATA[{new_body}]]>" + content[match.end():]
    return new_content, old_body, new_body


# ─── Верификация ──────────────────────────────────────────────────────────────

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def verify(original: str, updated: str, new_sql: str):
    print("\n─── Верификация ─────────────────────────────────────")

    # 1. Структура вне CDATA не изменилась
    orig_skeleton    = CDATA_RE.sub("__CDATA__", original)
    updated_skeleton = CDATA_RE.sub("__CDATA__", updated)
    if orig_skeleton == updated_skeleton:
        print("✅ Структура вне CDATA не изменилась")
    else:
        print("❌ Структура вне CDATA изменилась!")
        for i, (a, b) in enumerate(zip(orig_skeleton, updated_skeleton)):
            if a != b:
                print(f"   Первое отличие на символе {i}: {repr(a)} → {repr(b)}")
                break

    # 2. SQL присутствует в последнем CDATA
    last_match = get_last_cdata_match(updated)
    if new_sql.strip() in last_match.group(1):
        print("✅ Новый SQL присутствует в последнем CDATA")
    else:
        print("❌ Новый SQL НЕ найден в последнем CDATA")

    # 3. Остальные блоки не тронуты
    orig_cdatas    = CDATA_RE.findall(original)
    updated_cdatas = CDATA_RE.findall(updated)
    unchanged = sum(1 for o, u in zip(orig_cdatas, updated_cdatas) if o == u)
    print(f"✅ Нетронутых CDATA-блоков: {unchanged} из {len(orig_cdatas)}")
    print(f"   Изменённых блоков: {len(orig_cdatas) - unchanged} (ожидаем 1)")

    # 4. Хэши для справки
    print(f"\n   SHA-256 до:    {sha256(original)[:16]}...")
    print(f"   SHA-256 после: {sha256(updated)[:16]}...")
    print("─────────────────────────────────────────────────────")


# ─── Запуск ───────────────────────────────────────────────────────────────────

def main():
    # Проверяем исходный файл
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Исходный файл не найден: {SOURCE_FILE}")

    print(f"📂 Источник: {SOURCE_FILE}  ({SOURCE_FILE.stat().st_size:,} байт)")
    print(f"📁 Цель:     {TARGET_FILE}")

    original = SOURCE_FILE.read_text(encoding="utf-8")

    # Показываем последний CDATA
    last_match = get_last_cdata_match(original)
    print(f"\n── Последний CDATA ──")
    print(last_match.group(1).strip())

    # Защита от дублей — проверяем в исходнике
    if MARKER in last_match.group(1):
        print(f"\n⚠️  Этот SQL уже есть в последнем CDATA — вставка пропущена.")
        print(f"   Маркер: '{MARKER}'")
        return

    # Вставка
    updated, old_body, new_body = append_sql_to_last_cdata(original, NEW_SQL)

    print(f"\n── CDATA после вставки ──")
    print(new_body.strip())

    # Верификация
    verify(original, updated, NEW_SQL)

    # Создаём папку если не существует и сохраняем в TARGET_FILE
    TARGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    TARGET_FILE.write_text(updated, encoding="utf-8")
    print(f"\n💾 Сохранено: {TARGET_FILE}  ({TARGET_FILE.stat().st_size:,} байт)")


if __name__ == "__main__":
    main()