#include <System/Threading/CancellationToken.hpp>
#include <System/Threading/CancellationTokenSource.hpp>
#include <System/Threading/Tasks/Task.hpp>
#include <System/Threading/Tasks/TaskCanceledException.hpp>

int main() {
    System::Threading::CancellationTokenSource source;
    const auto token = source.getTokenProperty();
    source.Cancel();

    auto task = System::Threading::Tasks::TaskT<int>::Run(
        [token] {
            token.ThrowIfCancellationRequested();
            return 42;
        },
        token);

    try {
        (void)task.Wait();
    } catch (const System::Threading::Tasks::TaskCanceledException&) {
        return 0;
    }
    return 1;
}
