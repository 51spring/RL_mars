"""Close only the owned DSSAT process tree, without restarting a finished run."""


def close_native_client(native):
    import psutil
    import zmq
    pid=getattr(native,'_client_process_pid',None)
    if pid is not None and (not isinstance(pid,int) or pid<=0):
        raise ValueError('Expected a positive owned simulator PID')
    owned=[]
    if pid is not None:
        try:
            parent=psutil.Process(pid)
            owned=parent.children(recursive=True)+[parent]
        except psutil.NoSuchProcess:
            pass
    for process in owned:
        try:process.terminate()
        except psutil.NoSuchProcess:pass
    _,alive=psutil.wait_procs(owned,timeout=1.)
    for process in alive:
        try:process.kill()
        except psutil.NoSuchProcess:pass
    _,alive=psutil.wait_procs(alive,timeout=1.)
    if alive:raise RuntimeError('Owned DSSAT processes did not exit')
    native._client_process_pid=None
    if hasattr(native,'_cleanup_process'):
        import atexit
        atexit.unregister(native._cleanup_process)
    native._last_is_send=True
    server=getattr(native,'_server',None)
    if server is not None:server.setsockopt(zmq.LINGER,0)
