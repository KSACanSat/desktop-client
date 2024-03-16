from threading import Thread


class PacketThread(Thread):
    """
    Internal class to handle packet processing on specific threads.
    """
    def __init__(self, thread_id, packet, finish_callback, task_fetch_fn):
        """
        Parameters:
        -----------
        thread_id: int
            Identifies the thread for the main Discalculia class.
        packet: list
            A bunch of data waiting to be processed.
        finish_callback: function
            A function to be called when all the calculations are executed.
        task_fetch_fn:
            A function that calls for fetching the next task from the manager object.
        """
        super().__init__()
        self.daemon = True
        self.thread_id = thread_id
        self.packet = packet
        self.finish_callback = finish_callback
        self.task_fetch_fn = task_fetch_fn

    def run(self):
        task_id = 0
        # Run until there aren't any more packets
        while (task := self.task_fetch_fn(task_id)) is not None:
            self.packet = task.process(self.packet)
            task_id += 1
        self.finish_callback(self, self.packet)


class Discalculia:
    """
    The main instance of discalculia.
    """
    def __init__(self, thread_limit=10):
        """
        Parameters
        ----------
        thread_limit : int, optional
            Limits the number of active processing threads. Defaults to 10.
        """
        self.thread_limit = thread_limit
        self.threads = []
        self.running_threads = []
        self.tasks = []
        self.done_packets = []

    def add_task(self, task):
        """
        Add a task to the processing pipeline.
        """
        self.tasks.append(task)

    def process_packet(self, packet):
        """
        Adds a packet to the processing pipeline and starts it as soon as there is an available thread.
        """
        packet_thread = PacketThread(len(self.running_threads), packet,
                                     self.on_process_finished, self.get_task)
        if len(self.running_threads)+1 < self.thread_limit:
            # Start processing packet on different packet
            self.running_threads.append(packet_thread)
            self.running_threads[-1].start()
        else:
            # Add the process to the waiting list
            self.threads.append(packet_thread)

    def get_task(self, idx):
        return self.tasks[idx] if len(self.tasks) > idx else None

    def on_process_finished(self, thread, final_packet):
        del self.running_threads[thread.thread_id]
        if len(self.threads) > 0:
            self.running_threads.append(self.threads[0])
            self.running_threads[-1].start()
            del self.threads[0]
        self.done_packets.append(final_packet)

    def get_done_packets(self):
        packets = self.done_packets.copy()
        self.done_packets.clear()
        return packets

    def close(self):
        pass
