import uuid
from scheduler.implementation.current_network import CurrentNetwork
from scheduler.core.observer import Observer

if __name__ == '__main__':
    print("=== Запуск хвильового алгоритму ECHO ===")
    print("Мережа створена. Запускаємо симуляцію...\n")
    
    network = CurrentNetwork()
    observer = Observer(network)
    observer.run()
    
    print("\n=== Симуляція завершена ===")