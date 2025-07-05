from loguru import logger
import argparse
import logging
import grpc
from concurrent import futures
from user_srv.handler.user import UserServicer
from user_srv.proto import user_pb2_grpc, user_pb2
import signal
import sys
import os

BASE_DIR= os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

def on_exit(signo, frame):
    logger.info("Server exiting...")
    sys.exit(0)

def server():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', nargs="?", type=str, default='127.0.0.1', help='host')
    parser.add_argument('--port', nargs="?", type=int, default=50051, help='port')
    args = parser.parse_args()

    logger.add("user_srv/logs/server_{time}.log", rotation="10 MB", retention="10 days")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServicer_to_server(UserServicer(), server)
    server.add_insecure_port(f'{args.host}:{args.port}')
    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)
    logger.info(f"Starting server on {args.host}:{args.port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    server()