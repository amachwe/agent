import a2a_pb2_grpc as a2a_grpc
import a2a_pb2 as a2a_proto
import grpc
from concurrent import futures
import logging


def build_agent_message_response(id:str, message: str) -> a2a_proto.Message:
    message = a2a_proto.Message(
        message_id=id,
        role=a2a_proto.Role.ROLE_AGENT,
        parts = [a2a_proto.Part(text=message)]

    )
    return a2a_proto.SendMessageResponse(msg=message)

class Agent1(a2a_grpc.A2AServiceServicer):
    
    def SendMessage(self, request, context):
        print(request, context)

        response = build_agent_message_response(request.request.message_id, f"Agent1 received: {request}")
        return response
    
    def SendStreamingMessage(self, request, context):
        print(request, context)
        for i in range(3):
            response = build_agent_message_response(request.request.message_id, f"Agent1 streaming part {i+1} for: {request}")
            yield response
    
def serve(port="50051"):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    a2a_grpc.add_A2AServiceServicer_to_server(Agent1(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server started on port {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
