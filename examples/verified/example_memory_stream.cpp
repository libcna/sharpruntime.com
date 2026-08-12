#include <System/IO/BinaryReader.hpp>
#include <System/IO/BinaryWriter.hpp>
#include <System/IO/MemoryStream.hpp>

#include <string>

int main() {
    System::IO::MemoryStream stream;

    {
        System::IO::BinaryWriter writer(&stream, true);
        writer.Write(static_cast<SharpRuntime::intcs>(42));
        writer.Write(std::string("sharp"));
        writer.Flush();
        writer.Close();
    }

    stream.setPositionProperty(0);
    System::IO::BinaryReader reader(&stream, true);
    const auto number = reader.ReadInt32();
    const auto text = reader.ReadString();

    return number == 42 && text == "sharp" ? 0 : 1;
}
