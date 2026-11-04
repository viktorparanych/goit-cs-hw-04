import os
import multiprocessing
import time
from collections import defaultdict

def search_in_files(file_paths, keywords, queue):
    """
    Функція, яку виконує кожен процес.
    Шукає ключові слова і відправляє результати в головний потік через Queue.
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

    #відправляємо локальний словник цього процесу у спільну чергу
    queue.put(local_results)

def main():
    #налаштування
    KEYWORDS = ["python", "програмування", "потік", "алгоритм"]
    DATA_DIR = "data"
    NUM_PROCESSES = 4 #кількість процесів

    if not os.path.exists(DATA_DIR):
        print(f"Помилка: Папку '{DATA_DIR}' не знайдено.")
        return
        
    all_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    
    if not all_files:
        print(f"Папка '{DATA_DIR}' порожня. Додайте текстові файли.")
        return

    #розбиваємо список файлів на чанки
    chunk_size = len(all_files) // NUM_PROCESSES + (1 if len(all_files) % NUM_PROCESSES > 0 else 0)
    chunks = [all_files[i:i + chunk_size] for i in range(0, len(all_files), chunk_size)]

    #створюємо чергу для обміну даними між процесами
    queue = multiprocessing.Queue()
    processes = []

    print("Багатопроцесорний пошук")
    print(f"Кількість файлів: {len(all_files)}. Кількість процесів: {len(chunks)}.")
    
    #фіксуємо час початку
    start_time = time.time()

    #створюємо та запускаємо процеси
    for chunk in chunks:
        p = multiprocessing.Process(target=search_in_files, args=(chunk, KEYWORDS, queue))
        processes.append(p)
        p.start()

    #збираємо результати з черги
    final_results = defaultdict(list)
    for _ in range(len(processes)):
        local_res = queue.get() # Чекаємо і отримуємо словник від одного з процесів
        for kw, paths in local_res.items():
            final_results[kw].extend(paths)

    #чекаємо коректного завершення всіх процесів
    for p in processes:
        p.join()

    #фіксуємо час завершення
    end_time = time.time()

    #виводимо результати
    print("\nРезультати пошуку")
    for kw, paths in final_results.items():
        print(f"'{kw}': {paths}")
    
    print(f"\nЧас виконання: {end_time - start_time:.5f} секунд")

if __name__ == "__main__":
    main()