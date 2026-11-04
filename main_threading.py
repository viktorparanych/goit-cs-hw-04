import os
import threading
import time
from collections import defaultdict

def search_in_files(file_paths, keywords, results, lock):
    """
    Функція, яку виконує кожен потік. 
    Шукає ключові слова у переданому списку файлів.
    """
    local_results = defaultdict(list)
    
    for filepath in file_paths:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read().lower()
                for keyword in keywords:
                    if keyword.lower() in text:
                        local_results[keyword].append(filepath)
        except Exception as e:
            print(f"[Помилка] Не вдалося обробити файл {filepath}: {e}")

    #блокування доступу до спільного словника перед його оновленням
    with lock:
        for kw, paths in local_results.items():
            results[kw].extend(paths)

def main():
    #налаштування
    KEYWORDS = ["python", "програмування", "потік", "алгоритм"]
    DATA_DIR = "data"
    NUM_THREADS = 4 #кількість потоків

    #отримуємо список усіх файлів у папці data
    if not os.path.exists(DATA_DIR):
        print(f"Помилка: Папку '{DATA_DIR}' не знайдено.")
        return
        
    all_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    
    if not all_files:
        print(f"Папка '{DATA_DIR}' порожня. Додайте туди текстові файли (.txt) для пошуку.")
        return

    #розбиваємо список файлів на чанки для кожного потоку
    chunk_size = len(all_files) // NUM_THREADS + (1 if len(all_files) % NUM_THREADS > 0 else 0)
    chunks = [all_files[i:i + chunk_size] for i in range(0, len(all_files), chunk_size)]

    results = defaultdict(list)
    lock = threading.Lock()
    threads = []

    print("Багатопотоковий пошук")
    print(f"Кількість файлів: {len(all_files)}. Кількість потоків: {len(chunks)}.")
    
    #фіксуємо час початку
    start_time = time.time()

    #створюємо та запускаємо потоки
    for chunk in chunks:
        thread = threading.Thread(target=search_in_files, args=(chunk, KEYWORDS, results, lock))
        threads.append(thread)
        thread.start()

    #чекаємо завершення всіх потоків
    for thread in threads:
        thread.join()

    #фіксуємо час завершення
    end_time = time.time()

    #виводимо результати
    print("\nРезультати пошуку")
    for kw, paths in results.items():
        print(f"'{kw}': {paths}")
    
    print(f"\nЧас виконання: {end_time - start_time:.5f} секунд")

if __name__ == "__main__":
    main()