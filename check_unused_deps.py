# check_unused_deps.py
import subprocess
import sys
import os
import re


def get_installed_packages():
    """Получает список установленных пакетов (только top-level)"""
    result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--not-required'],
                            capture_output=True, text=True)
    packages = []
    for line in result.stdout.splitlines()[2:]:  # Пропускаем заголовки
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                package_name = parts[0].lower()
                packages.append(package_name)
    return packages


def sanitize_package_name(name):
    """Преобразует имя пакета в допустимое для import"""
    # Убираем суффиксы вроде [bcrypt], [redis]
    name = name.split("[")[0]
    # Заменяем - на _
    return name.replace("-", "_")


def is_package_used(package_name, root_dir="."):
    """Проверяет, используется ли пакет в коде"""
    import_name = sanitize_package_name(package_name)

    # Шаблоны поиска
    patterns = [
        rf"import\s+{re.escape(import_name)}",
        rf"from\s+{re.escape(import_name)}\s+",
        # Проверка импортов с подпакетами: from fastapi.responses
        rf"from\s+{re.escape(import_name)}\."
    ]

    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in patterns:
                            if re.search(pattern, content):
                                return True
                except (IOError, UnicodeDecodeError):
                    pass
    return False


def main():
    print("🔍 Поиск неиспользуемых зависимостей...\n")

    packages = get_installed_packages()
    unused = []

    for pkg in sorted(packages):
        used = is_package_used(pkg)
        status = "✅ Используется" if used else "❌ НЕ используется"
        print(f"{pkg:<25} {status}")

        if not used:
            unused.append(pkg)

    print("\n" + "=" * 50)
    if unused:
        print("❗ Рекомендуется удалить:")
        for pkg in unused:
            print(f"   pip uninstall {pkg}")
    else:
        print("🎉 Все зависимости используются!")


if __name__ == "__main__":
    main()