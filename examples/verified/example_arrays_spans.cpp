#include <System/Array.hpp>
#include <System/Span.hpp>

#include <vector>

int main() {
    std::vector<int> values{5, 4, 3, 2, 1};
    System::Span<int> all(values);
    all.Slice(1, 3).Fill(9);

    System::Array::Sort(values);
    const auto firstNine = System::Array::IndexOf(values, 9);

    System::Span<int> source(values.data(), 4);
    System::Span<int> destination(values.data() + 1, 4);
    source.CopyTo(destination);

    return firstNine == 2 && values == std::vector<int>({1, 1, 5, 9, 9}) ? 0 : 1;
}
