#include <System/ArgumentOutOfRangeException.hpp>
#include <System/EventArgs.hpp>
#include <System/EventHandler.hpp>
#include <System/Nullable.hpp>

class Score final {
public:
    System::EventHandler<System::EventArgs> Changed;

    explicit Score(int value) : value_(value) {
        validate(value);
    }

    [[nodiscard]] int getValueProperty() const noexcept {
        return value_;
    }

    void setValueProperty(int value) {
        validate(value);
        if (value_ == value) return;
        value_ = value;
        const System::EventArgs args;
        Changed.Raise(nullptr, args);
    }

private:
    static void validate(int value) {
        if (value < 0) {
            throw System::ArgumentOutOfRangeException("value");
        }
    }

    int value_{};
};

int main() {
    Score score(1);
    int notifications = 0;
    const auto token = score.Changed.Add(
        [&notifications](System::Object*, const System::EventArgs&) {
            ++notifications;
        });

    const System::Nullable<int> requested = 5;
    score.setValueProperty(requested.GetValueOrDefault(0));
    score.Changed.Remove(token);

    return score.getValueProperty() == 5 && notifications == 1 ? 0 : 1;
}
