"""Start one process: loopback by default, explicitly configured behind a proxy."""
import os
from .hosting import HostingConfig


def main():
    hosting = HostingConfig.from_env()
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['OMP_NUM_THREADS'] = '1'
    import uvicorn
    uvicorn.run('demo.app:app', host=hosting.bind_host, port=8000, workers=1,
                access_log=False, proxy_headers=False)


if __name__ == '__main__':
    main()
