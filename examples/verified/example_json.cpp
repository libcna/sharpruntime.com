#include <System/Text/Json/JsonSerializer.hpp>

#include <iostream>
#include <string>
#include <vector>

int main() {
    const std::vector<int> ids{3, 7, 11};
    const std::string json = System::Text::Json::JsonSerializer::Serialize(ids);
    const auto restored =
        System::Text::Json::JsonSerializer::Deserialize<std::vector<int>>(json);

    std::cout << json << '\n';
    return restored == ids ? 0 : 1;
}
