from scheduler.core.observer import Observer
from scheduler.implementation.current_network import CurrentNetwork

NETWORK_CLASS = CurrentNetwork

if __name__ == '__main__':
    network = NETWORK_CLASS()
    network.start_merlin_sigal()      # ← Важливо!
    
    observer = Observer(network)
    observer.run()