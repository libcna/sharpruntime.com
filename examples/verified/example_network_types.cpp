#include <System/Net/Dns.hpp>
#include <System/Net/IPAddress.hpp>
#include <System/Net/IPEndPoint.hpp>
#include <System/Net/Sockets/AddressFamily.hpp>

int main() {
    const auto address = System::Net::IPAddress::Parse("127.0.0.1");
    const System::Net::IPEndPoint endpoint(address, 8080);
    const auto family = endpoint.getAddressProperty().getAddressFamilyProperty();
    return family == System::Net::Sockets::AddressFamily::InterNetwork ? 0 : 1;
}
