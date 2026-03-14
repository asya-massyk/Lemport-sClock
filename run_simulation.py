from scheduler.core.observer import Observer
from scheduler.implementation.current_network import CurrentNetwork

# NETWORK_CLASS should be set to the current implementation network class
NETWORK_CLASS = CurrentNetwork

if __name__ == '__main__':
    network = NETWORK_CLASS()
    observer = Observer(network)
    observer.run()