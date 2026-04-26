"""
Вставка SQL в конец CDATA-блока без изменения структуры файла вне CDATA.

Подход: работаем с файлом как с текстом через re.
lxml НЕ используем — он переформатирует отступы и переносы.
"""

import re
import hashlib
from pathlib import Path


# ─── Настройки ────────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent / "migrations"
INPUT_FILE = BASE_DIR / "migrations.xml"

# Якорь для поиска нужного CDATA.
# Скрипт найдёт CDATA внутри блока, который содержит этот текст.
# Можно указать id миграции, уникальный комментарий, часть SQL — что угодно.
ANCHOR = 'migration id="003"'

# SQL который дописываем в конец CDATA.
# Первая строка-комментарий используется как уникальный маркер —
# при повторном запуске скрипт найдёт её и не будет вставлять дубль.
NEW_SQL = """
-- patch 2025-01-15: add status column
ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'pending';
UPDATE orders SET status = 'completed' WHERE amount > 0;"""

# Уникальный маркер для проверки дублей — берём первую строку NEW_SQL
MARKER = NEW_SQL.strip().splitlines()[0]


# ─── Ядро ─────────────────────────────────────────────────────────────────────

# Находит CDATA-блок (любой, включая многострочный)
CDATA_RE = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)


def find_cdata_for_anchor(content: str, anchor: str):
    """
    Ищем CDATA-блок внутри фрагмента, который начинается с anchor.
    Возвращает match объект или None.
    """
    anchor_pos = content.find(anchor)
    if anchor_pos == -1:
        return None

    # Ищем CDATA только после якоря
    return CDATA_RE.search(content, anchor_pos)


def append_sql_to_cdata(content: str, anchor: str, new_sql: str):
    """
    Находит нужный CDATA по якорю и дописывает SQL в конец.
    Возвращает (new_content, old_cdata, new_cdata).
    """
    match = find_cdata_for_anchor(content, anchor)
    if not match:
        raise ValueError(f"❌ CDATA не найден после якоря: '{anchor}'")

    old_cdata_body = match.group(1)           # содержимое между [[ и ]]
    new_cdata_body = old_cdata_body.rstrip() + "\n" + new_sql.strip() + "\n        "

    # Заменяем только этот конкретный CDATA (по позиции, не глобально)
    new_full = f"<![CDATA[{new_cdata_body}]]>"

    # Используем позицию из match чтобы не задеть другие блоки
    new_content = content[:match.start()] + new_full + content[match.end():]

    return new_content, old_cdata_body, new_cdata_body


# ─── Верификация ──────────────────────────────────────────────────────────────

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def verify(original: str, updated: str, anchor: str, new_sql: str):
    print("\n─── Верификация ───────────────────────────────────────")

    # 1. Структура вне CDATA не изменилась
    original_outside = CDATA_RE.sub("__CDATA__", original)
    updated_outside  = CDATA_RE.sub("__CDATA__", updated)

    if original_outside == updated_outside:
        print("✅ Структура вне CDATA — не изменилась (пробелы, отступы, теги)")
    else:
        print("❌ Структура вне CDATA изменилась!")
        for i, (a, b) in enumerate(zip(original_outside, updated_outside)):
            if a != b:
                print(f"   Первое отличие на символе {i}: {repr(a)} → {repr(b)}")
                break

    # 2. Нужный CDATA найден и содержит новый SQL
    match = find_cdata_for_anchor(updated, anchor)
    if match and new_sql.strip() in match.group(1):
        print("✅ Новый SQL присутствует в целевом CDATA")
    else:
        print("❌ Новый SQL НЕ найден в целевом CDATA")

    # 3. Остальные CDATA-блоки не тронуты
    original_cdatas = CDATA_RE.findall(original)
    updated_cdatas  = CDATA_RE.findall(updated)

    unchanged = sum(
        1 for o, u in zip(original_cdatas, updated_cdatas) if o == u
    )
    changed = len(original_cdatas) - unchanged
    print(f"✅ Нетронутых CDATA-блоков: {unchanged} из {len(original_cdatas)}")
    print(f"   Изменённых блоков: {changed} (ожидаем 1)")

    # 4. Хэши для справки
    print(f"\n   SHA-256 до:    {sha256(original)[:16]}...")
    print(f"   SHA-256 после: {sha256(updated)[:16]}...")
    print("───────────────────────────────────────────────────────")


# ─── Запуск ───────────────────────────────────────────────────────────────────

def main():
    input_path = Path(INPUT_FILE)

    if not input_path.exists():
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    print(f"📂 Читаем: {input_path}  ({input_path.stat().st_size:,} байт)")

    original = input_path.read_text(encoding="utf-8")

    print(f"🔍 Якорь: '{ANCHOR}'")
    print(f"🔍 Маркер дубля: '{MARKER}'")

    # Защита от дублей — ищем маркер в нужном CDATA
    match = find_cdata_for_anchor(original, ANCHOR)
    if match and MARKER in match.group(1):
        print("\n⚠️  Этот SQL уже есть в CDATA — повторная вставка пропущена.")
        return

    # Вставка
    updated, old_body, new_body = append_sql_to_cdata(original, ANCHOR, NEW_SQL)

    print(f"\n── CDATA до ({len(old_body)} симв.) ──")
    print(old_body.strip())
    print(f"\n── CDATA после ({len(new_body)} симв.) ──")
    print(new_body.strip())

    # Верификация до записи
    verify(original, updated, ANCHOR, NEW_SQL)

    # Пишем обратно в тот же файл
    input_path.write_text(updated, encoding="utf-8")
    print(f"\n💾 Файл обновлён: {input_path}  ({input_path.stat().st_size:,} байт)")


if __name__ == "__main__":
    main()