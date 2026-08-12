#include <System/Net/Http/HttpClient.hpp>

int main() {
    System::Net::Http::HttpClient client;
    client.setBaseAddressProperty("http://127.0.0.1:8080");
    client.setDefaultHeader("Accept", "application/json");

    return client.getBaseAddressProperty() == "http://127.0.0.1:8080"
        && client.getDefaultHeader("Accept") == "application/json"
        ? 0
        : 1;
}
