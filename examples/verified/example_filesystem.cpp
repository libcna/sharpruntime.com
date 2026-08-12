#include <System/IO/File.hpp>

#include <chrono>
#include <filesystem>
#include <string>

int main() {
    const auto nonce = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto directory = std::filesystem::temp_directory_path()
        / ("sharp-runtime-site-example-" + std::to_string(nonce));
    std::filesystem::create_directory(directory);
    const auto path = (directory / "round-trip.txt").string();

    System::IO::File::WriteAllText(path, "source-verified");
    const auto value = System::IO::File::ReadAllText(path);

    std::filesystem::remove_all(directory);
    return value == "source-verified" ? 0 : 1;
}
