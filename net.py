from multiprocessing import Process


class Workers(object):
    '''
    worker object for starting and stopping processes
    '''

    def __init__(self, name, num_workers, target_function, args, logger):
        self.name = name
        self.num_workers = num_workers
        self.target_function = target_function
        self.args = args
        self.queue = args[0]
        self.proc_list = []
        self.logger = logger

    def start_process(self):
        for _ in range(self.num_workers):
            p = Process(target=self.target_function, args=self.args)
            p.start()
            self.proc_list.append(p)
        self.logger.info('started {} {} processes'.format(self.num_workers, self.name))

    def shutdown_process(self):
        for _ in range(self.num_workers):
            self.queue.put('END')
        self.logger.info('waiting for {} to finish'.format(self.name))
        for p in self.proc_list:
            try:
                p.join()
            except KeyboardInterrupt:
                break


class Master(object):
    '''
    Handles read, write, and reporter workers
    '''

    def __init__(self, logger):
        self.workers = {}
        self.order = []
        self.logger = logger

    def new_worker(self, name, num_workers, target_function, args):
        worker = Workers(name, num_workers, target_function, args, self.logger)
        self.workers[name] = worker
        self.order.append(name)

    def start(self):
        for name in self.order:
            self.workers[name].start_process()

    def shutdown(self):
        for name in self.order:
            self.logger.info('shutting down {} processes'.format(name))
            self.workers[name].shutdown_process()
