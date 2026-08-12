#include <System/Threading/Channels/Channel.hpp>

int main() {
    auto channel = System::Threading::Channels::Channel<int>::CreateBounded(2);
    if (!channel.Writer->TryWrite(10)) return 1;
    if (!channel.Writer->TryWrite(20)) return 2;
    if (channel.Writer->TryWrite(30)) return 3;

    int first{};
    int second{};
    if (!channel.Reader->TryRead(first)) return 4;
    if (!channel.Reader->TryRead(second)) return 5;
    channel.Writer->Complete();

    return first == 10 && second == 20 ? 0 : 6;
}
