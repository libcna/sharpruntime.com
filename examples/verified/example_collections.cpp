#include <System/Collections/Generic/Dictionary.hpp>
#include <System/Collections/Generic/List.hpp>

#include <string>

int main() {
    System::Collections::Generic::List<int> values;
    values.Add(3);
    values.Add(7);

    System::Collections::Generic::Dictionary<std::string, int> counts;
    counts.Add("values", values.getCountProperty());
    int count{};

    return values.Contains(7) && counts.TryGetValue("values", count) && count == 2
        ? 0
        : 1;
}
