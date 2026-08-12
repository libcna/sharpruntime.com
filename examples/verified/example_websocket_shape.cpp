#include <System/Net/WebSockets/ClientWebSocket.hpp>
#include <System/Net/WebSockets/WebSocketState.hpp>

int main() {
    System::Net::WebSockets::ClientWebSocket socket;
    return socket.getStateProperty() == System::Net::WebSockets::WebSocketState::None
        ? 0
        : 1;
}
