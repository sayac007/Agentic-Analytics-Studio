"""Start one local-only process; no cloud account or frontend build required."""
import os


def main():
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['OMP_NUM_THREADS'] = '1'
    import uvicorn
    uvicorn.run('demo.app:app', host='127.0.0.1', port=8000, workers=1, access_log=False)


if __name__ == '__main__':
    main()
